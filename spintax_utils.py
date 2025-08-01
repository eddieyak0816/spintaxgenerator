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
    found_vars = set(re.findall(r'\{\{(.*?)\}\}', template))
    missing = found_vars - set(variables.keys())
    if 'main_keyword' in found_vars and 'main_keyword' not in variables:
        missing = missing - {'main_keyword'}
    if missing:
        return None, f"The template uses variables you did not define: {', '.join(missing)}"
    # Build the formula by splitting the template into text and variable/cell parts
    parts = []
    pattern = re.compile(r'\{\{(.*?)\}\}')
    last = 0
    cell_ref_pattern = re.compile(r'^[A-Za-z]+[0-9]+$')
    for m in pattern.finditer(template):
        if m.start() > last:
            # Add preceding text
            parts.append('"' + template[last:m.start()].replace('"', '""') + '"')
        var = m.group(1)
        if var == 'main_keyword' and main_keyword:
            parts.append('"' + main_keyword.replace('"', '""') + '"')
        elif var in variables:
            cell = str(variables[var])
            # If the variable value looks like a cell reference, use it directly (no quotes)
            if cell_ref_pattern.match(cell):
                parts.append(cell)
            else:
                parts.append('"' + cell.replace('"', '""') + '"')
        else:
            parts.append('""')
        last = m.end()
    if last < len(template):
        parts.append('"' + template[last:].replace('"', '""') + '"')
    concat = ', '.join(parts)
    formula = f'=SPINTAX(CONCATENATE({concat}))'
    return formula, None
