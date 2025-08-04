from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import random
from spintax_utils import spintax_preview, generate_formula
from prompt_manager import load_prompts, save_prompts, DEFAULT_TEMPLATE
import os

app = Flask(__name__)
app.secret_key = 'spintax_secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    # Assign initial state before debugging
    variables = {}
    sample_values = {}
    main_keyword = ''
    template_options = ['']  # Changed from single template to list
    use_default = True
    preview = ''
    formula = ''
    prompts = load_prompts()
    prompt_name = ''
    prompt_text = ''
    new_prompt_name = ''
    tab = request.form.get('tab') or request.args.get('tab', 'variables')
    selected_template = ''

    # Debug: Print incoming form data and key variables
    if request.method == 'POST':
        print('--- POST DEBUG ---')
        print('Form:', dict(request.form))
        print('Action:', request.form.get('action'))
        print('Tab:', tab)
        print('Prompt Name:', prompt_name)
        print('New Prompt Name:', new_prompt_name)
        print('Prompt Text:', prompt_text)
        print('Prompts BEFORE:', load_prompts())
    # State
    variables = {}
    sample_values = {}
    main_keyword = ''
    template_options = ['']  # Changed from single template to list
    use_default = True
    preview = ''
    formula = ''
    prompts = load_prompts()
    prompt_name = ''
    prompt_text = ''
    new_prompt_name = ''
    tab = request.form.get('tab') or request.args.get('tab', 'variables')

    if request.method == 'POST':
        action = request.form.get('action')
        # Always restore variables from hidden field unless clearing variables
        if action == 'clear_variables':
            variables = {}
        else:
            variables = json.loads(request.form.get('variables_json', '{}'))

        # Template Tab: Load template from dropdown
        if action == 'load_template':
            selected_template = request.form.get('selected_template', '').strip()
            if selected_template in prompts:
                # Parse stored template back into multiple options
                stored_template = prompts[selected_template]
                if '|||OPTION_SEPARATOR|||' in stored_template:
                    template_options = stored_template.split('|||OPTION_SEPARATOR|||')
                else:
                    # Legacy single template support
                    template_options = [stored_template]
            else:
                template_options = ['']
            tab = 'template'
        # Variables Tab
        elif action == 'add_variable':
            name = request.form.get('var_name', '').strip()
            cell = request.form.get('var_cell', '').strip()
            if name and cell:
                variables[name] = cell
            tab = 'variables'
        elif action == 'remove_variable':
            remove_var = request.form.get('remove_var')
            if remove_var in variables:
                del variables[remove_var]
            tab = 'variables'
        elif action == 'clear_variables':
            tab = 'variables'
        # Template Tab
        elif action == 'preview':
            # Collect all template options
            template_options = []
            i = 0
            while f'template_option_{i}' in request.form:
                option = request.form.get(f'template_option_{i}', '').strip()
                if option:  # Only add non-empty options
                    template_options.append(option)
                i += 1
            
            if not template_options:
                template_options = ['']
            
            sample_values = {k: v for k, v in request.form.items() if k.startswith('sample_')}
            sample_values = {k.replace('sample_', ''): v for k, v in sample_values.items()}
            main_keyword = request.form.get('main_keyword', '').strip()
            if main_keyword:
                sample_values['main_keyword'] = main_keyword
            
            # Combine all templates with | separator for preview
            combined_template = '|'.join(template_options)
            preview = spintax_preview(combined_template, variables, sample_values)
            tab = 'template'
        elif action == 'refresh_sample':
            # Same as preview but randomly select one option for sample
            template_options = []
            i = 0
            while f'template_option_{i}' in request.form:
                option = request.form.get(f'template_option_{i}', '').strip()
                if option:
                    template_options.append(option)
                i += 1
            
            if not template_options:
                template_options = ['']
            
            sample_values = {k: v for k, v in request.form.items() if k.startswith('sample_')}
            sample_values = {k.replace('sample_', ''): v for k, v in sample_values.items()}
            main_keyword = request.form.get('main_keyword', '').strip()
            if main_keyword:
                sample_values['main_keyword'] = main_keyword
            
            # Randomly select one option for sample preview
            if template_options and template_options[0]:
                selected_option = random.choice(template_options)
                preview = spintax_preview(selected_option, variables, sample_values)
            else:
                preview = ''
            tab = 'template'
        elif action == 'generate_formula':
            # Collect all template options
            template_options = []
            i = 0
            while f'template_option_{i}' in request.form:
                option = request.form.get(f'template_option_{i}', '').strip()
                if option:
                    template_options.append(option)
                i += 1
            
            if not template_options:
                template_options = ['']
            
            main_keyword = request.form.get('main_keyword', '').strip()
            # Combine all templates with | separator for formula generation
            combined_template = '|'.join(template_options)
            formula, err = generate_formula(combined_template, variables, main_keyword)
            if err:
                flash(err, 'warning')
            tab = 'template'
        elif action == 'clear_template':
            # Clear all template options
            template_options = ['']
            tab = 'template'
        elif action == 'select_prompt':
            prompts = load_prompts()
            selected_prompt = request.form.get('prompt_select', '')
            if selected_prompt in prompts:
                stored_template = prompts[selected_prompt]
                if '|||OPTION_SEPARATOR|||' in stored_template:
                    template_options = stored_template.split('|||OPTION_SEPARATOR|||')
                else:
                    template_options = [stored_template]
                prompt_name = selected_prompt
                new_prompt_name = selected_prompt
                prompt_text = stored_template
            else:
                template_options = ['']
                prompt_name = ''
                new_prompt_name = ''
                prompt_text = ''
            # After selecting a prompt, show it in the Prompt Manager tab
            tab = 'prompts'
        # Prompt Manager Tab
        elif action == 'save_prompt':
            prompts = load_prompts()
            
            # Collect current template options from the form
            current_template_options = []
            i = 0
            while f'template_option_{i}' in request.form:
                option = request.form.get(f'template_option_{i}', '').strip()
                if option:
                    current_template_options.append(option)
                i += 1
            
            # Use combined template options as the prompt text
            if current_template_options:
                combined_template = '|||OPTION_SEPARATOR|||'.join(current_template_options)
            else:
                combined_template = request.form.get('prompt_text', '').strip()
            
            new_prompt_name = request.form.get('new_prompt_name', '').strip()
            dropdown_prompt_name = request.form.get('prompt_name', '').strip()
            prompt_name_to_save = new_prompt_name if new_prompt_name else dropdown_prompt_name
            print('--- SAVE PROMPT ---')
            print('prompt_name_to_save:', prompt_name_to_save)
            print('combined_template:', combined_template)
            print('current_template_options:', current_template_options)
            if not combined_template or not prompt_name_to_save:
                flash('Prompt name and template options cannot be empty.', 'warning')
            else:
                prompts[prompt_name_to_save] = combined_template
                save_prompts(prompts)
                print('Prompts AFTER SAVE:', load_prompts())
                flash(f"Template '{prompt_name_to_save}' saved with {len(current_template_options)} options.", 'success')
            # After saving, reload prompts and set both fields to saved name
            prompts = load_prompts()
            prompt_name = prompt_name_to_save
            new_prompt_name = prompt_name_to_save
            prompt_text = combined_template
            # Keep the current template options for display
            template_options = current_template_options if current_template_options else ['']
            tab = 'prompts'
        elif action == 'delete_prompt':
            prompts = load_prompts()
            dropdown_prompt_name = request.form.get('prompt_name', '').strip()
            print('--- DELETE PROMPT ---')
            print('dropdown_prompt_name:', dropdown_prompt_name)
            print('Prompts BEFORE DELETE:', prompts)
            if dropdown_prompt_name and dropdown_prompt_name in prompts:
                del prompts[dropdown_prompt_name]
                save_prompts(prompts)
                print('Prompts AFTER DELETE:', load_prompts())
                flash(f"Prompt '{dropdown_prompt_name}' deleted.", 'success')
            else:
                flash('No prompt selected for deletion.', 'warning')
            # After deletion, reload prompts and clear fields
            prompts = load_prompts()
            prompt_name = ''
            new_prompt_name = ''
            prompt_text = ''
            tab = 'prompts'
        elif action == 'load_prompt':
            prompts = load_prompts()
            prompt_name = request.form.get('prompt_name', '').strip()
            new_prompt_name = prompt_name
            prompt_text = prompts.get(prompt_name, '')
            tab = 'prompts'
        else:
            # For all other actions except load_prompt and select_prompt, clear new_prompt_name and prompt_text
            if action not in ['load_prompt', 'select_prompt']:
                new_prompt_name = ''
                prompt_text = ''

    # For GET or after POST, always reload prompts
    prompts = load_prompts()
    # Ensure 'Default' prompt exists
    if 'Default' not in prompts:
        prompts['Default'] = 'Default template option 1|Default template option 2'
        save_prompts(prompts)

    # --- Always show selected prompt's name and text in Prompt Manager tab ---
    if tab == 'prompts' and prompt_name:
        new_prompt_name = prompt_name
        prompt_text = prompts.get(prompt_name, '')

    # Ensure template_options is always a list
    if not isinstance(template_options, list):
        template_options = ['']

    # Render
    print('--- RENDER DEBUG ---')
    print('Tab:', tab)
    print('Template Options:', template_options)
    print('Prompt Name:', prompt_name)
    print('New Prompt Name:', new_prompt_name)
    return render_template('index.html', **locals())


if __name__ == '__main__':
    app.run(debug=True)
