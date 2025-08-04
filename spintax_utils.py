import re
import os

def spintax_preview(template, variables, sample_values):
    preview = template
    # Replace variable placeholders ({{var}}) with sample values
    for var, val in sample_values.items():
        preview = preview.replace(f'{{{{{var}}}}}', val)
    # Also replace all occurrences of cell references with sample values
    for var, cell in variables.items():
        val = sample_values.get(var, '')
        if cell:
            pattern = re.compile(re.escape(cell.strip()), re.IGNORECASE)
            preview = pattern.sub(val, preview)
    return preview

def generate_formula(template, variables, main_keyword):
    # Handle both multiple template options separated by | AND nested spintax within templates
    
    if not template:
        return '=SPINTAX_NESTED("")', None
    
    # First, handle complex variable patterns like {{spintax}}
    complex_var_pattern = re.compile(r'\{\{[^}]*\{[^}]*\}[^}]*\}\}')
    if complex_var_pattern.search(template):
        # This template contains spintax wrapped in {{...}}, let's unwrap it
        def unwrap_spintax(match):
            content = match.group(1)  # Content inside {{...}}
            return content  # Return just the content without the outer braces
        
        template = complex_var_pattern.sub(unwrap_spintax, template)
    
    # Now check if we have multiple template options (split by | at the top level)
    # We need to be careful not to split on | that are inside {} braces
    
    # Split the template by | but only at the top level (not inside braces)
    template_parts = []
    current_part = ""
    brace_depth = 0
    
    for char in template:
        if char == '{':
            brace_depth += 1
            current_part += char
        elif char == '}':
            brace_depth -= 1
            current_part += char
        elif char == '|' and brace_depth == 0:
            # This is a top-level pipe separator
            if current_part.strip():
                template_parts.append(current_part.strip())
            current_part = ""
        else:
            current_part += char
    
    # Don't forget the last part
    if current_part.strip():
        template_parts.append(current_part.strip())
    
    # If we have multiple template parts, create spintax format
    if len(template_parts) > 1:
        # Process each template part individually
        processed_options = []
        
        for template_part in template_parts:
            processed_part = process_single_template(template_part, variables, main_keyword)
            processed_options.append(processed_part)
        
        # Create spintax format with the processed options
        spintax_content = '{' + '|'.join(processed_options) + '}'
        return create_formula_from_processed_content(spintax_content, variables, main_keyword)
    else:
        # Single template (may contain nested spintax)
        return create_formula_from_processed_content(template, variables, main_keyword)

def process_single_template(template_part, variables, main_keyword):
    """Process a single template part, replacing only {{variable}} patterns, not {spintax} patterns"""
    # Only replace {{variable}} patterns that don't contain braces inside
    var_pattern = re.compile(r'\{\{([^{}]*)\}\}')
    
    processed_part = template_part
    
    # Find and replace {{variable}} patterns (only simple variables, not spintax)
    for match in var_pattern.finditer(template_part):
        var_name = match.group(1)
        # Only process if the variable name doesn't contain braces (not spintax)
        if '{' not in var_name and '}' not in var_name:
            if var_name == 'main_keyword' and main_keyword:
                processed_part = processed_part.replace(f'{{{{{var_name}}}}}', main_keyword)
            elif var_name in variables:
                # Keep as variable placeholder for now - will be handled in final processing
                continue
            else:
                processed_part = processed_part.replace(f'{{{{{var_name}}}}}', '')
    
    return processed_part

def create_formula_from_processed_content(content, variables, main_keyword):
    """Create the final CONCATENATE formula from processed content"""
    cell_ref_pattern = re.compile(r'\b([A-Za-z]+[0-9]+)\b')
    var_pattern = re.compile(r'\{\{([^{}]*)\}\}')  # Only match simple variables, not spintax
    parts = []
    matches = []
    
    # Find all matches (variables and cell refs) - but NOT spintax braces
    for m in var_pattern.finditer(content):
        var_name = m.group(1)
        # Only treat as variable if it doesn't contain braces (not spintax)
        if '{' not in var_name and '}' not in var_name:
            matches.append((m.start(), m.end(), 'var', var_name))
    
    for m in cell_ref_pattern.finditer(content):
        # Only add cell refs not inside {{ }}
        inside_var = False
        for vstart, vend, _, _ in matches:
            if m.start() >= vstart and m.end() <= vend:
                inside_var = True
                break
        if not inside_var:
            matches.append((m.start(), m.end(), 'cell', m.group(1)))
    
    # Sort matches by start position
    matches.sort(key=lambda x: x[0])
    
    # Build the concatenation parts
    idx = 0
    while idx < len(matches):
        mstart, mend, mtype, mval = matches[idx]
        # Add preceding text
        prev_end = matches[idx-1][1] if idx > 0 else 0
        if mstart > prev_end:
            text_part = content[prev_end:mstart]
            if text_part:
                parts.append('"' + text_part.replace('"', '""') + '"')
        
        if mtype == 'var':
            if mval == 'main_keyword' and main_keyword:
                parts.append('"' + main_keyword.replace('"', '""') + '"')
            elif mval in variables:
                cell = str(variables[mval])
                if cell_ref_pattern.match(cell):
                    parts.append(cell)
                else:
                    parts.append('"' + cell.replace('"', '""') + '"')
            else:
                parts.append('""')
        elif mtype == 'cell':
            parts.append(mval)
        idx += 1
    
    # Add trailing text
    if matches:
        last_end = matches[-1][1]
        if last_end < len(content):
            text_part = content[last_end:]
            if text_part:
                parts.append('"' + text_part.replace('"', '""') + '"')
    else:
        # No matches, just quote the entire content
        if content:
            parts.append('"' + content.replace('"', '""') + '"')
    
    # Create the final formula
    if parts:
        concat = ', '.join(parts)
        formula = f'=SPINTAX_NESTED(CONCATENATE({concat}))'
    else:
        formula = '=SPINTAX_NESTED("")'
    
    return formula, None
