import re

def get_input(prompt, default=None):
    value = input(f"{prompt} [{default if default else ''}]: ")
    return value.strip() if value.strip() else default

# Default spintax template (edit as needed)
default_template = '''<p>{Transform|Elevate|Enhance} your {{main_keyword}} home with {stunning|beautiful|exquisite} {{product}} from {{company}}. We {proudly serve|cater to|specialize in serving} homeowners throughout {{main_keyword}} and the surrounding areas of {{location}}, {delivering|providing|offering} {top-quality|premium|superior} {{product}} that {combine|blend|merge} {durability|strength|resilience} with {timeless|classic|enduring} {beauty|elegance|appeal}.</p>'''

def main():
    print("Spintax Template Generator for Google Sheets\n")
    print("Define your variables (e.g., main_keyword, product, company, location). Type 'done' when finished.\n")
    variables = []
    while True:
        var = get_input("Variable name (or 'done' to finish)")
        if not var or var.lower() == 'done':
            break
        variables.append(var)

    use_default = get_input("Use default template? (y/n)", "y")

    if use_default.lower() == 'y':
        template = default_template
        # Find variables as words (not in curly braces)
        found_vars = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', template))
        # Remove words that are not user variables (e.g., HTML tags, spintax, etc.)
        reserved = {'Transform', 'Elevate', 'Enhance', 'stunning', 'beautiful', 'exquisite', 'from', 'We', 'proudly', 'serve', 'cater', 'to', 'specialize', 'in', 'serving', 'homeowners', 'throughout', 'and', 'the', 'surrounding', 'areas', 'of', 'delivering', 'providing', 'offering', 'top', 'quality', 'premium', 'superior', 'that', 'combine', 'blend', 'merge', 'durability', 'strength', 'resilience', 'with', 'timeless', 'classic', 'enduring', 'beauty', 'elegance', 'appeal', 'home', 'countertops', 'counter', 'tops', 'PentalQuartz', 'Stone', 'Tech', 'Fabrication', 'including', 'measurement', 'consultation', 'Custom', 'Tailored', 'Personalized', 'fabrication', 'to', 'your', 'specifications', 'Precise', 'Accurate', 'Meticulous', 'installation', 'by', 'our', 'experienced', 'skilled', 'trained', 'team', 'Wide', 'Extensive', 'Diverse', 'selection', 'of', 'colors', 'patterns', 'Competitive', 'Affordable', 'Reasonable', 'pricing', 'options', 'Upgrade', 'Renovate', 'Kitchen', 'Today', 'Ready', 'Eager', 'Excited', 'enhance', 'upgrade', 'gorgeous', 'Contact', 'Reach', 'out', 'Get', 'in', 'touch', 'with', 'schedule', 'book', 'arrange', 'consultation', 'appointment', 'free', 'estimate', 'Call', 'us', 'Reach', 'at', 'or', 'fill', 'out', 'complete', 'submit', 'online', 'form', 'get', 'started', 'begin', 'project', 'take', 'first', 'step', 'towards', 'dream', 'Why', 'Homeowners', 'Trust', 'Choose', 'Prefer', 'Decades', 'Commitment', 'Dedication', 'customer', 'satisfaction', 'client', 'happiness', 'Use', 'Utilization', 'state', 'of', 'the', 'art', 'cutting', 'edge', 'advanced', 'technology', 'Attention', 'Focus', 'on', 'detail', 'every', 'project', 'Prompt', 'Timely', 'Efficient', 'service', 'throughout', 'and', 'Discover', 'Experience', 'Explore', 'allure', 'let', 'allow', 'us', 'to', 'bring', 'deliver', 'provide', 'charm', 'bathroom', 'Other', 'areas', 'that', 'we', 'serve', 'Counters', 'Counter', 'Tops', 'Countertops', 'in', 'href', 'https', 'stonetechfabrication', 'com', 'pentalquartz', 'counters', 'lower', 'substitute', 'h3', 'i3', 'a', 'li', 'ul', 'p', 'h2', 'h3', 'target', 'blank', 'rel', 'noopener'}
        found_vars = {v for v in found_vars if v not in reserved}
        missing = found_vars - set(variables)
        if missing:
            print(f"\nWarning: The default template uses variables you did not define: {', '.join(missing)}")
            for m in missing:
                variables.append(m)
    else:
        print("Enter your custom spintax template. Use variable names (no brackets) for variables.")
        template = input("Template: ")
        found_vars = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', template))
        reserved = {'Transform', 'Elevate', 'Enhance', 'stunning', 'beautiful', 'exquisite', 'from', 'We', 'proudly', 'serve', 'cater', 'to', 'specialize', 'in', 'serving', 'homeowners', 'throughout', 'and', 'the', 'surrounding', 'areas', 'of', 'delivering', 'providing', 'offering', 'top', 'quality', 'premium', 'superior', 'that', 'combine', 'blend', 'merge', 'durability', 'strength', 'resilience', 'with', 'timeless', 'classic', 'enduring', 'beauty', 'elegance', 'appeal', 'home', 'countertops', 'counter', 'tops', 'PentalQuartz', 'Stone', 'Tech', 'Fabrication', 'including', 'measurement', 'consultation', 'Custom', 'Tailored', 'Personalized', 'fabrication', 'to', 'your', 'specifications', 'Precise', 'Accurate', 'Meticulous', 'installation', 'by', 'our', 'experienced', 'skilled', 'trained', 'team', 'Wide', 'Extensive', 'Diverse', 'selection', 'of', 'colors', 'patterns', 'Competitive', 'Affordable', 'Reasonable', 'pricing', 'options', 'Upgrade', 'Renovate', 'Kitchen', 'Today', 'Ready', 'Eager', 'Excited', 'enhance', 'upgrade', 'gorgeous', 'Contact', 'Reach', 'out', 'Get', 'in', 'touch', 'with', 'schedule', 'book', 'arrange', 'consultation', 'appointment', 'free', 'estimate', 'Call', 'us', 'Reach', 'at', 'or', 'fill', 'out', 'complete', 'submit', 'online', 'form', 'get', 'started', 'begin', 'project', 'take', 'first', 'step', 'towards', 'dream', 'Why', 'Homeowners', 'Trust', 'Choose', 'Prefer', 'Decades', 'Commitment', 'Dedication', 'customer', 'satisfaction', 'client', 'happiness', 'Use', 'Utilization', 'state', 'of', 'the', 'art', 'cutting', 'edge', 'advanced', 'technology', 'Attention', 'Focus', 'on', 'detail', 'every', 'project', 'Prompt', 'Timely', 'Efficient', 'service', 'throughout', 'and', 'Discover', 'Experience', 'Explore', 'allure', 'let', 'allow', 'us', 'to', 'bring', 'deliver', 'provide', 'charm', 'bathroom', 'Other', 'areas', 'that', 'we', 'serve', 'Counters', 'Counter', 'Tops', 'Countertops', 'in', 'href', 'https', 'stonetechfabrication', 'com', 'pentalquartz', 'counters', 'lower', 'substitute', 'h3', 'i3', 'a', 'li', 'ul', 'p', 'h2', 'h3', 'target', 'blank', 'rel', 'noopener'}
        found_vars = {v for v in found_vars if v not in reserved}
        for m in found_vars:
            if m not in variables:
                variables.append(m)

    # Prompt for sample values for preview
    print("\nEnter sample values for each variable (for preview):")
    sample_values = {}
    for var in variables:
        sample_values[var] = get_input(f"Sample value for {var}")

    # Prompt for cell references for each variable
    print("\nNow enter Google Sheets cell references for each variable:")
    cell_map = {}
    for var in variables:
        cell_map[var] = get_input(f"Cell reference for {var} (e.g., H2)")

    # Show preview with sample values, replacing cell references with sample values
    preview = template
    for var, cell in cell_map.items():
        val = sample_values[var]
        preview = re.sub(rf'\b{re.escape(cell)}\b', val, preview)
    print("\n--- Preview with sample values ---\n")
    print(preview)
    print("\n--- End of preview ---\n")

    # Replace cell references with Google Sheets cell references in the formula
    formula_template = template
    for var, cell in cell_map.items():
        formula_template = re.sub(rf'\b{re.escape(cell)}\b', f'" & {cell} & "', formula_template)

    # Prepare for Google Sheets formula
    formula = f'=SUBSTITUTE(SPINTAX(CONCATENATE("{formula_template}")), "", "")'
    print("\nGoogle Sheets Formula:\n")
    print(formula)

    save = get_input("Save template to file? (y/n)", "n")
    if save and save.lower() == 'y':
        filename = get_input("Filename", "spintax_template.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formula)
        print(f"Template saved to {filename}")

if __name__ == "__main__":
    main()
