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
    # Template now contains multiple options separated by |
    # We need to create a single template with {option1|option2|option3} format
    
    # Split the template by | to get individual options
    template_parts = [part.strip() for part in template.split('|') if part.strip()] if template else ['']
    
    if not template_parts:
        return '=SPINTAX_NESTED("")', None
    
    # If we have multiple options, we need to create the {option1|option2|option3} format
    if len(template_parts) > 1:
        # Process each template part and then combine them with |
        processed_options = []
        
        for template_part in template_parts:
            # Process each template part individually for variables and cell references
            cell_ref_pattern = re.compile(r'\b([A-Za-z]+[0-9]+)\b')
            var_pattern = re.compile(r'\{\{(.*?)\}\}')
            parts = []
            matches = []
            
            # Find all matches (variables and cell refs) in this template part
            for m in var_pattern.finditer(template_part):
                matches.append((m.start(), m.end(), 'var', m.group(1)))
            for m in cell_ref_pattern.finditer(template_part):
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
            
            # Build this option with variables replaced
            processed_part = template_part
            
            # Replace variables with their cell references or main keyword
            for _, _, mtype, mval in reversed(matches):  # Process in reverse to maintain positions
                if mtype == 'var':
                    if mval == 'main_keyword' and main_keyword:
                        processed_part = processed_part.replace(f'{{{{{mval}}}}}', main_keyword)
                    elif mval in variables:
                        # For cell references, we'll handle them in the final concatenation
                        continue  # Keep the variable placeholder for now
                    else:
                        processed_part = processed_part.replace(f'{{{{{mval}}}}}', '')
            
            processed_options.append(processed_part)
        
        # Now create the spintax format: {option1|option2|option3}
        spintax_content = '{' + '|'.join(processed_options) + '}'
        
        # Now process the combined spintax content for the final formula
        cell_ref_pattern = re.compile(r'\b([A-Za-z]+[0-9]+)\b')
        var_pattern = re.compile(r'\{\{(.*?)\}\}')
        parts = []
        matches = []
        
        # Find all matches in the spintax content
        for m in var_pattern.finditer(spintax_content):
            matches.append((m.start(), m.end(), 'var', m.group(1)))
        for m in cell_ref_pattern.finditer(spintax_content):
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
        
        # Build the final concatenation parts
        idx = 0
        while idx < len(matches):
            mstart, mend, mtype, mval = matches[idx]
            # Add preceding text
            prev_end = matches[idx-1][1] if idx > 0 else 0
            if mstart > prev_end:
                parts.append('"' + spintax_content[prev_end:mstart].replace('"', '""') + '"')
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
            if last_end < len(spintax_content):
                parts.append('"' + spintax_content[last_end:].replace('"', '""') + '"')
        else:
            parts.append('"' + spintax_content.replace('"', '""') + '"')
    
    else:
        # Single option, process normally
        template_part = template_parts[0]
        cell_ref_pattern = re.compile(r'\b([A-Za-z]+[0-9]+)\b')
        var_pattern = re.compile(r'\{\{(.*?)\}\}')
        parts = []
        matches = []
        
        # Find all matches (variables and cell refs)
        for m in var_pattern.finditer(template_part):
            matches.append((m.start(), m.end(), 'var', m.group(1)))
        for m in cell_ref_pattern.finditer(template_part):
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
        idx = 0
        while idx < len(matches):
            mstart, mend, mtype, mval = matches[idx]
            # Add preceding text
            prev_end = matches[idx-1][1] if idx > 0 else 0
            if mstart > prev_end:
                parts.append('"' + template_part[prev_end:mstart].replace('"', '""') + '"')
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
            if last_end < len(template_part):
                parts.append('"' + template_part[last_end:].replace('"', '""') + '"')
        else:
            parts.append('"' + template_part.replace('"', '""') + '"')
    
    # Create the final formula
    if parts:
        concat = ', '.join(parts)
        formula = f'=SPINTAX_NESTED(CONCATENATE({concat}))'
    else:
        formula = '=SPINTAX_NESTED("")'
    
    return formula, None
