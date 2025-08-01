from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
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
    template = DEFAULT_TEMPLATE
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
    template = DEFAULT_TEMPLATE
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
                template = prompts[selected_template]
            else:
                template = ''
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
            sample_values = {k: v for k, v in request.form.items() if k.startswith('sample_')}
            sample_values = {k.replace('sample_', ''): v for k, v in sample_values.items()}
            main_keyword = request.form.get('main_keyword', '').strip()
            if main_keyword:
                sample_values['main_keyword'] = main_keyword
            template = request.form.get('template_text', '').strip()
            preview = spintax_preview(template, variables, sample_values)
            tab = 'template'
        elif action == 'generate_formula':
            main_keyword = request.form.get('main_keyword', '').strip()
            template = request.form.get('template_text', '').strip()
            formula, err = generate_formula(template, variables, main_keyword)
            if err:
                flash(err, 'warning')
            tab = 'template'
        elif action == 'clear_template':
            # Only clear the template, not variables
            template = ''
            tab = 'template'
        elif action == 'select_prompt':
            prompts = load_prompts()
            selected_prompt = request.form.get('prompt_select', '')
            if selected_prompt in prompts:
                template = prompts[selected_prompt]
                prompt_name = selected_prompt
                new_prompt_name = selected_prompt
                prompt_text = prompts[selected_prompt]
            else:
                template = ''
                prompt_name = ''
                new_prompt_name = ''
                prompt_text = ''
            # After selecting a prompt, show it in the Prompt Manager tab
            tab = 'prompts'
        # Prompt Manager Tab
        elif action == 'save_prompt':
            prompts = load_prompts()
            prompt_text = request.form.get('prompt_text', '').strip()
            new_prompt_name = request.form.get('new_prompt_name', '').strip()
            dropdown_prompt_name = request.form.get('prompt_name', '').strip()
            prompt_name_to_save = new_prompt_name if new_prompt_name else dropdown_prompt_name
            print('--- SAVE PROMPT ---')
            print('prompt_name_to_save:', prompt_name_to_save)
            print('prompt_text:', prompt_text)
            if not prompt_text or not prompt_name_to_save:
                flash('Prompt name and text cannot be empty.', 'warning')
            else:
                prompts[prompt_name_to_save] = prompt_text
                save_prompts(prompts)
                print('Prompts AFTER SAVE:', load_prompts())
                flash(f"Prompt '{prompt_name_to_save}' saved.", 'success')
            # After saving, reload prompts and set both fields to saved name
            prompts = load_prompts()
            prompt_name = prompt_name_to_save
            new_prompt_name = prompt_name_to_save
            prompt_text = prompt_text
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
        prompts['Default'] = DEFAULT_TEMPLATE
        save_prompts(prompts)

    # --- Always show selected prompt's name and text in Prompt Manager tab ---
    if tab == 'prompts' and prompt_name:
        new_prompt_name = prompt_name
        prompt_text = prompts.get(prompt_name, '')

    # Render
    print('--- RENDER DEBUG ---')
    print('Tab:', tab)
    print('Prompt Name:', prompt_name)
    print('New Prompt Name:', new_prompt_name)
    print('Prompt Text:', prompt_text)
    return render_template('index.html', **locals())


if __name__ == '__main__':
    app.run(debug=True)
