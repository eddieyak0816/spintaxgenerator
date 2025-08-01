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
    # Find all {{variable}} and direct cell references (A1, B1, etc.)
    cell_ref_pattern = re.compile(r'\b([A-Za-z]+[0-9]+)\b')
    var_pattern = re.compile(r'\{\{(.*?)\}\}')
    parts = []
    last = 0
    matches = []
    # Find all matches (variables and cell refs)
    for m in var_pattern.finditer(template):
        matches.append((m.start(), m.end(), 'var', m.group(1)))
    for m in cell_ref_pattern.finditer(template):
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
            parts.append('"' + template[prev_end:mstart].replace('"', '""') + '"')
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
        if last_end < len(template):
            parts.append('"' + template[last_end:].replace('"', '""') + '"')
    else:
        parts.append('"' + template.replace('"', '""') + '"')
    concat = ', '.join(parts)
    formula = f'=SPINTAX(CONCATENATE({concat}))'
    return formula, None
