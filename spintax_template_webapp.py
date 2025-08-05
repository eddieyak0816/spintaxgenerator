from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import random
import re
import requests
import os
from spintax_utils import spintax_preview, generate_formula
from prompt_manager import load_prompts, save_prompts, DEFAULT_TEMPLATE

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


@app.route('/prompt-builder', methods=['GET', 'POST'])
def prompt_builder():
    # SEO Content Generator Questions
    seo_questions = {
        'business_info': {
            'title': 'Business Information',
            'questions': {
                'business_name': 'What is your business name?',
                'industry': 'What industry are you in?',
                'location': 'What is your primary business location (city, state/province, country)?',
                'target_audience': 'Who is your target audience?',
                'unique_selling_proposition': 'What is your unique selling proposition or main differentiator?'
            }
        },
        'services_products': {
            'title': 'Services/Products',
            'questions': {
                'main_services': 'What are your main services or products? (List 3-5 primary offerings)',
                'service_benefits': 'What are the key benefits customers get from each service/product?',
                'pricing_model': 'What is your pricing model or range?',
                'service_area': 'What geographic area do you serve?'
            }
        },
        'seo_content': {
            'title': 'SEO & Content Preferences',
            'questions': {
                'primary_keywords': 'What are your primary keywords? (3-5 main terms you want to rank for)',
                'secondary_keywords': 'What are your secondary/long-tail keywords? (10-15 supporting terms)',
                'content_tone': 'What tone should the content have? (Professional, friendly, authoritative, conversational, etc.)',
                'content_length': 'What content length do you prefer? (Short paragraphs, medium articles, long-form content)',
                'call_to_action': 'What is your preferred call-to-action? (Contact us, Get a quote, Schedule consultation, etc.)'
            }
        },
        'competitors': {
            'title': 'Competition & Market',
            'questions': {
                'main_competitors': 'Who are your main competitors? (List 2-3 companies)',
                'competitive_advantage': 'What advantages do you have over competitors?',
                'market_position': 'How do you position yourself in the market? (Premium, budget-friendly, specialized, full-service, etc.)'
            }
        },
        'content_goals': {
            'title': 'Content Goals',
            'questions': {
                'content_purpose': 'What is the main purpose of this content? (Lead generation, brand awareness, education, sales, etc.)',
                'target_actions': 'What actions do you want visitors to take after reading your content?',
                'content_distribution': 'Where will this content be used? (Website pages, blog posts, social media, email campaigns, etc.)',
                'success_metrics': 'How do you measure content success? (Traffic, leads, conversions, rankings, etc.)'
            }
        }
    }
    
    # Handle form submission
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'ai_autofill':
            # Get the business description from the user
            business_description = request.form.get('business_description', '').strip()
            if business_description:
                # Generate AI-powered answers
                ai_answers = generate_ai_answers(business_description)
                return render_template('prompt_builder.html', 
                                     seo_questions=seo_questions, 
                                     answers=ai_answers,
                                     business_description=business_description)
            else:
                flash('Please provide a business description for AI auto-fill.', 'warning')
        
        elif action == 'generate_prompt':
            # Collect all answers
            answers = {}
            for section_key, section_data in seo_questions.items():
                answers[section_key] = {}
                for question_key, question_text in section_data['questions'].items():
                    answer = request.form.get(f'{section_key}_{question_key}', '').strip()
                    if answer:
                        answers[section_key][question_key] = answer
            
            # Generate the updated prompt
            updated_prompt = generate_updated_prompt(answers)
            
            return render_template('prompt_builder.html', 
                                 seo_questions=seo_questions, 
                                 answers=answers, 
                                 updated_prompt=updated_prompt)
    
    return render_template('prompt_builder.html', seo_questions=seo_questions, answers={})


def generate_ai_answers(business_description):
    """Generate AI-powered answers using specific prompts for each question"""
    
    # Define specific prompts for each question
    question_prompts = {
        'business_info': {
            'business_name': {
                'prompt': f"""Based on this business description: "{business_description}"

Extract or infer the business name. Look for:
- Explicit mentions of company/business names
- Brand names or identifiers
- If no name is mentioned, suggest a professional name based on the services described

Respond with just the business name, nothing else.""",
                'max_length': 50
            },
            'industry': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the most specific industry category this business belongs to. Consider:
- Primary business activities and services
- Target market and customers  
- Business model and operations
- Industry-specific terminology used

Provide a concise, professional industry classification (e.g., 'Digital Marketing', 'Residential Real Estate', 'Automotive Repair', 'Healthcare Services'). Be specific rather than generic.

Respond with just the industry name, nothing else.""",
                'max_length': 100
            },
            'location': {
                'prompt': f"""Based on this business description: "{business_description}"

Extract or infer the business location. Look for:
- Cities, states, regions mentioned
- Service areas described
- Geographic indicators
- If no location is mentioned, respond with "Local area"

Respond with just the location (City, State format preferred), nothing else.""",
                'max_length': 100
            },
            'target_audience': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the primary target audience for this business. Consider:
- Who would need these services/products?
- Demographics mentioned or implied
- Customer types served
- Market segments addressed

Provide a clear, specific description of the target audience (e.g., "Small business owners seeking digital marketing", "Homeowners in need of HVAC services").

Respond with 1-2 sentences describing the target audience.""",
                'max_length': 200
            },
            'unique_selling_proposition': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify or create a compelling unique selling proposition (USP). Look for:
- What makes this business different from competitors
- Special qualifications, experience, or approach
- Unique benefits or value provided
- If not explicitly mentioned, infer based on the business type

Create a strong USP that highlights competitive advantages.

Respond with 1-2 sentences describing the unique selling proposition.""",
                'max_length': 250
            }
        },
        'services_products': {
            'main_services': {
                'prompt': f"""Based on this business description: "{business_description}"

List the main services or products offered by this business. Focus on:
- Primary offerings mentioned
- Core services/products that drive revenue
- 3-5 most important offerings

Format as a clear, comma-separated list of services/products.

Respond with just the list, nothing else.""",
                'max_length': 200
            },
            'service_benefits': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the key benefits customers receive from this business's services/products. Consider:
- Value propositions mentioned or implied
- Problems solved for customers
- Outcomes and results provided
- Customer satisfaction elements

List 4-6 key benefits in a clear, benefit-focused format.

Respond with a comma-separated list of benefits.""",
                'max_length': 300
            },
            'pricing_model': {
                'prompt': f"""Based on this business description: "{business_description}"

Determine or suggest an appropriate pricing model for this business. Consider:
- Industry standards for this type of business
- Service delivery method
- Customer payment preferences
- Value-based vs. time-based pricing

Suggest a realistic pricing approach (e.g., "Hourly rates", "Project-based pricing", "Monthly retainers", "Competitive market rates").

Respond with 1-2 sentences describing the pricing model.""",
                'max_length': 150
            },
            'service_area': {
                'prompt': f"""Based on this business description: "{business_description}"

Determine the geographic service area for this business. Consider:
- Location mentioned
- Type of business (local vs. remote)
- Service delivery method
- Industry norms

Describe the service area (e.g., "Greater Austin area", "Nationwide remote services", "Local and surrounding counties").

Respond with just the service area description, nothing else.""",
                'max_length': 100
            }
        },
        'seo_content': {
            'primary_keywords': {
                'prompt': f"""Based on this business description: "{business_description}"

Generate 3-5 primary SEO keywords that this business should target. Consider:
- Main services/products offered
- Geographic location
- Industry terms customers would search for
- High-value, specific keywords

Create keywords that potential customers would actually search for when looking for these services.

Respond with a comma-separated list of primary keywords.""",
                'max_length': 200
            },
            'secondary_keywords': {
                'prompt': f"""Based on this business description: "{business_description}"

Generate 8-12 secondary/long-tail SEO keywords. Include:
- Specific service variations
- Location-based terms
- Problem-solving keywords
- Industry-specific terms
- "Near me" variations

Focus on longer, more specific phrases customers might search for.

Respond with a comma-separated list of secondary keywords.""",
                'max_length': 400
            },
            'content_tone': {
                'prompt': f"""Based on this business description: "{business_description}"

Recommend the best content tone for this business's marketing. Consider:
- Industry expectations
- Target audience preferences
- Business positioning
- Trust and authority needs

Choose from professional, friendly, authoritative, conversational, technical, approachable, or a combination.

Respond with 1-2 words describing the recommended tone (e.g., "Professional yet approachable").""",
                'max_length': 100
            },
            'content_length': {
                'prompt': f"""Based on this business description: "{business_description}"

Recommend optimal content length strategies for this business. Consider:
- Industry complexity
- Customer research behavior
- SEO requirements
- Attention spans of target audience

Suggest content length preferences for different content types.

Respond with a brief recommendation (e.g., "Medium-length articles (500-1000 words) with clear headings").""",
                'max_length': 150
            },
            'call_to_action': {
                'prompt': f"""Based on this business description: "{business_description}"

Create the most effective call-to-action (CTA) for this business. Consider:
- What action leads to conversions
- Customer decision-making process
- Industry best practices
- Urgency and value

Suggest 1-2 primary CTAs that would convert prospects to customers.

Respond with the recommended call-to-action phrases.""",
                'max_length': 100
            }
        },
        'competitors': {
            'main_competitors': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the types of competitors this business faces. Consider:
- Direct service/product competitors
- Industry players
- Local vs. national competition
- Alternative solutions customers might choose

Describe competitor categories rather than specific company names.

Respond with 1-2 sentences describing the competitive landscape.""",
                'max_length': 200
            },
            'competitive_advantage': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify or suggest key competitive advantages for this business. Consider:
- Unique qualifications or experience
- Service delivery advantages
- Technology or process improvements
- Customer service excellence
- Specializations or niches

List 2-4 potential competitive advantages.

Respond with a clear list of competitive advantages.""",
                'max_length': 250
            },
            'market_position': {
                'prompt': f"""Based on this business description: "{business_description}"

Determine the best market positioning for this business. Consider:
- Premium vs. budget positioning
- Specialist vs. generalist approach
- Local leader vs. niche player
- Quality vs. convenience focus

Recommend a positioning strategy that differentiates from competitors.

Respond with 1-2 sentences describing the recommended market position.""",
                'max_length': 150
            }
        },
        'content_goals': {
            'content_purpose': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the primary purpose of content marketing for this business. Consider:
- Business goals and objectives
- Customer acquisition needs
- Brand awareness requirements
- Trust and authority building

Determine what content should accomplish for this business.

Respond with the main content purpose (e.g., "Lead generation and trust building").""",
                'max_length': 100
            },
            'target_actions': {
                'prompt': f"""Based on this business description: "{business_description}"

Define the key actions this business wants visitors to take after consuming content. Consider:
- Conversion path for this industry
- Customer decision-making process
- Lead generation needs
- Sales process requirements

List 2-4 specific actions that lead to business results.

Respond with a comma-separated list of target actions.""",
                'max_length': 200
            },
            'content_distribution': {
                'prompt': f"""Based on this business description: "{business_description}"

Recommend the best content distribution channels for this business. Consider:
- Where target customers spend time
- Industry-appropriate platforms
- Content format preferences
- Resource requirements

Suggest 4-6 effective distribution channels.

Respond with a comma-separated list of distribution channels.""",
                'max_length': 200
            },
            'success_metrics': {
                'prompt': f"""Based on this business description: "{business_description}"

Identify the most important metrics for measuring content success. Consider:
- Business revenue drivers
- Customer acquisition costs
- Industry-standard KPIs
- Measurable outcomes

Suggest 3-5 key metrics that indicate content effectiveness.

Respond with a comma-separated list of success metrics.""",
                'max_length': 200
            }
        }
    }
    
    # Process each section and question with AI
    answers = {}
    
    for section_key, section_questions in question_prompts.items():
        answers[section_key] = {}
        
        for question_key, prompt_data in section_questions.items():
            try:
                # Generate AI response for this specific question - ALWAYS include business description
                ai_response = call_ai_service(prompt_data['prompt'], business_description, prompt_data['max_length'])
                answers[section_key][question_key] = ai_response.strip()
                print(f"[AI DEBUG] Generated answer for {section_key}.{question_key}: {ai_response[:50]}...")
            except Exception as e:
                # Fallback to a basic response if AI call fails
                fallback_response = generate_fallback_answer(section_key, question_key, business_description)
                answers[section_key][question_key] = fallback_response
                print(f"[AI DEBUG] AI call failed for {section_key}.{question_key}: {e}")
    
    return answers


def call_ai_service(prompt, business_description="", max_length=200):
    """
    Call an AI service to generate a response to the prompt.
    Primary: Google Gemini API, with fallbacks for other services.
    ALWAYS try Gemini first for all questions.
    """
    
    # Try Gemini first - always attempt AI for all questions
    try:
        gemini_response = call_gemini(prompt, business_description, max_length)
        if gemini_response and len(gemini_response.strip()) > 10:  # Only accept substantial responses
            print(f"[AI DEBUG] Gemini successful for: {prompt[:50]}...")
            return gemini_response
        else:
            print(f"[AI DEBUG] Gemini returned insufficient response: '{gemini_response}'")
    except Exception as e:
        print(f"[AI DEBUG] Gemini call failed: {e}")
        
    # Try OpenAI as backup if available
    try:
        return call_openai(prompt, business_description, max_length)
    except Exception as e2:
        print(f"[AI DEBUG] OpenAI call failed: {e2}")
        
    # Final fallback to intelligent pattern matching
    print(f"[AI DEBUG] Using intelligent fallback for: {prompt[:50]}...")
    return call_intelligent_fallback(prompt, business_description, max_length)


def call_gemini(prompt, business_description="", max_length=200):
    """Call Google Gemini API for AI responses"""
    import json
    
    # Use the provided API key
    api_key = "AIzaSyARN1sB_stvSTkbnJCVfzlp-DyDxf7WyUQ"
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Include business description in the prompt for better context
    full_prompt = prompt
    if business_description:
        full_prompt = f"Business Description: {business_description}\n\nQuestion: {prompt}"
    
    # Prepare the request for Gemini
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You are a business analysis expert. Provide concise, accurate responses based on business descriptions. Follow the instructions exactly and keep responses focused and professional. Maximum {max_length} characters.\n\n{full_prompt}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": min(max_length, 150),
            "stopSequences": []
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    content = candidate['content']['parts'][0]['text'].strip()
                    # Clean up the response
                    content = content.replace('"', '').replace("'", "").strip()
                    return content[:max_length] if len(content) > max_length else content
                else:
                    raise Exception("No valid content in Gemini response")
            else:
                raise Exception("No candidates in Gemini response")
        else:
            error_msg = f"Gemini API error: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")


def call_openai(prompt, business_description="", max_length=200):
    """Call OpenAI's API for AI responses"""
    import json
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    
    # Include business description for better context
    full_prompt = prompt
    if business_description:
        full_prompt = f"Business Description: {business_description}\n\nQuestion: {prompt}"
    
    # Prepare the request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # Use a more efficient model for quick responses
    data = {
        'model': 'gpt-3.5-turbo',  # or 'gpt-4' for better quality
        'messages': [
            {
                'role': 'system',
                'content': 'You are a business analysis expert. Provide concise, accurate responses based on business descriptions. Follow the instructions exactly and keep responses focused and professional.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': min(max_length, 150),  # Keep responses concise
        'temperature': 0.3,  # Lower temperature for more consistent responses
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                # Clean up the response
                content = content.replace('"', '').replace("'", "").strip()
                return content[:max_length] if len(content) > max_length else content
            else:
                raise Exception("No valid response from OpenAI")
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")


def call_alternative_ai(prompt, max_length=200):
    """
    Call alternative AI services (Claude, local models, etc.)
    This is a placeholder for other AI service integrations
    """
    
    # Example for Claude API (Anthropic)
    # Uncomment and configure if you have Claude API access
    """
    claude_api_key = os.getenv('CLAUDE_API_KEY')
    if claude_api_key:
        headers = {
            'x-api-key': claude_api_key,
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'claude-3-haiku-20240307',
            'max_tokens': max_length,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text'].strip()
    """
    
    # For now, raise an exception to fall back to the intelligent fallback
    raise Exception("No alternative AI services configured")


def call_intelligent_fallback(prompt, business_description="", max_length=200):
    """
    Intelligent fallback using advanced pattern matching and rule-based responses
    This analyzes the actual business description text
    """
    
    # Use provided business description or extract from prompt if available
    if business_description:
        description = business_description
    else:
        # Extract the business description from the prompt if embedded
        desc_match = re.search(r'"([^"]*)"', prompt)
        description = desc_match.group(1) if desc_match else ""
    
    return generate_intelligent_response(prompt, description, max_length)
    if not desc_match:
        # Try alternative extraction patterns
        desc_match = re.search(r'description[:\s]+([^\n]+)', prompt, re.IGNORECASE)
    
    business_description = desc_match.group(1) if desc_match else ""
    desc_lower = business_description.lower()
    
    # Business name extraction with advanced patterns
    if "business name" in prompt.lower():
        name_patterns = [
            r'(?:name of my company is|company is called|business is named|we are)\s+([^,.!?]+)',
            r'(?:my company|our company|the company)\s+([A-Z][a-zA-Z\s&-]+)',
            r'^([A-Z][a-zA-Z\s&-]+)\s+(?:is|provides|specializes|offers)',
            r'([A-Z][a-zA-Z\s&-]+)\s+(?:digital marketing|marketing|consulting|services)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, business_description, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common words that shouldn't be in company names
                name = re.sub(r'\s+(and we|that|which|who)\s.*', '', name, flags=re.IGNORECASE)
                return name
        
        # If no pattern matches, try to extract first capitalized phrase
        words = business_description.split()
        if words:
            for i, word in enumerate(words):
                if word[0].isupper() and i < len(words) - 1:
                    if words[i+1][0].isupper() or words[i+1].lower() in ['digital', 'marketing', 'consulting', 'services', 'solutions']:
                        potential_name = ' '.join(words[i:i+3])
                        potential_name = re.sub(r'\s+(and|that|which|who).*', '', potential_name, flags=re.IGNORECASE)
                        return potential_name.strip()
    
    # Industry classification with detailed analysis
    elif "industry" in prompt.lower():
        industry_mappings = {
            'digital marketing': ['digital marketing', 'online marketing', 'internet marketing', 'web marketing'],
            'marketing & advertising': ['marketing', 'advertising', 'promotion', 'branding'],
            'web development': ['web development', 'website development', 'web design', 'website design'],
            'seo services': ['seo', 'search engine optimization', 'search marketing'],
            'social media services': ['social media', 'social networks', 'social engagement'],
            'ppc advertising': ['pay-per-click', 'ppc', 'paid advertising', 'google ads'],
            'video production': ['video', 'video generation', 'video creation', 'multimedia'],
            'technology services': ['software', 'tech', 'technology', 'IT services', 'development'],
            'consulting services': ['consulting', 'consultant', 'advisory', 'strategy'],
            'healthcare': ['medical', 'healthcare', 'clinic', 'dental', 'therapy'],
            'legal services': ['law', 'legal', 'attorney', 'lawyer'],
            'real estate': ['real estate', 'property', 'homes', 'realtor'],
            'automotive': ['auto', 'car', 'vehicle', 'automotive', 'mechanic'],
            'restaurant & food': ['restaurant', 'dining', 'food', 'catering', 'cafe'],
            'retail': ['retail', 'store', 'shop', 'boutique', 'merchandise'],
            'fitness & wellness': ['gym', 'fitness', 'training', 'workout', 'wellness'],
            'beauty & personal care': ['salon', 'spa', 'beauty', 'hair', 'cosmetic'],
            'education & training': ['education', 'school', 'training', 'tutoring', 'learning'],
            'home services': ['cleaning', 'landscaping', 'plumbing', 'electrical', 'hvac']
        }
        
        # Score each industry based on keyword matches
        industry_scores = {}
        for industry, keywords in industry_mappings.items():
            score = sum(1 for keyword in keywords if keyword in desc_lower)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            # Return the industry with the highest score
            best_industry = max(industry_scores, key=industry_scores.get)
            return best_industry.title()
        else:
            return "Professional Services"
    
    # Location extraction
    elif "location" in prompt.lower():
        location_patterns = [
            r'(?:throughout|across|in|located in|based in|serving)\s+(?:the\s+)?([A-Z][a-zA-Z\s]+(?:United States|USA|US|America))',
            r'(?:in|located in|based in|serving)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$|\s+we|\s+and)',
            r'([A-Z][a-zA-Z]+,\s*[A-Z]{2})',  # City, State format
            r'([A-Z][a-zA-Z\s]+\s+area)',
            r'(?:nationwide|national|across the country)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, business_description)
            if match:
                location = match.group(1).strip() if match.groups() else match.group()
                # Clean up the location
                location = re.sub(r'\s+(we|and|that).*', '', location, flags=re.IGNORECASE)
                return location
        
        return "Nationwide"
    
    # For other types of questions, use more sophisticated analysis
    else:
        # Use the original fallback system for other questions
        return generate_intelligent_response(prompt, business_description, max_length)


def generate_intelligent_response(prompt, business_description, max_length):
    """Generate intelligent responses for various question types"""
    
    desc_lower = business_description.lower()
    prompt_lower = prompt.lower()
    
    # Target Actions - What visitors should do
    if "target actions" in prompt_lower or "actions" in prompt_lower and "visitors" in prompt_lower:
        if "digital marketing" in desc_lower:
            return "Schedule a free consultation, request a marketing audit, download our strategy guide, get a custom quote"
        elif "restaurant" in desc_lower:
            return "Make a reservation, order online for delivery, view our menu, join our rewards program"
        elif "consulting" in desc_lower:
            return "Book a discovery call, request a proposal, download case studies, schedule a strategy session"
        elif "ecommerce" in desc_lower or "online store" in desc_lower:
            return "Add to cart, create account, subscribe to newsletter, read reviews"
        else:
            return "Contact us for information, schedule a consultation, request a quote, download resources"
    
    # Content Distribution - Where content will be used
    elif "content distribution" in prompt_lower or ("where" in prompt_lower and "content" in prompt_lower):
        if "digital marketing" in desc_lower:
            return "Company website and blog, LinkedIn business page, Google Ads landing pages, email newsletters, industry webinars"
        elif "restaurant" in desc_lower:
            return "Restaurant website, Google My Business, Instagram and Facebook, food delivery apps, local review sites"
        elif "consulting" in desc_lower:
            return "Professional website, LinkedIn articles, industry publications, email marketing, speaking events"
        elif "ecommerce" in desc_lower:
            return "Product pages, blog content, social media posts, email campaigns, marketplace listings"
        else:
            return "Website pages, blog posts, social media platforms, email marketing, print materials"
    
    # Success Metrics - How to measure content success
    elif "success metrics" in prompt_lower or ("measure" in prompt_lower and "success" in prompt_lower):
        if "digital marketing" in desc_lower:
            return "Lead generation volume, cost per acquisition, organic search rankings, conversion rates, client lifetime value"
        elif "restaurant" in desc_lower:
            return "Online reservations, delivery orders, social media engagement, customer reviews, repeat visits"
        elif "consulting" in desc_lower:
            return "Consultation bookings, proposal requests, thought leadership engagement, referral generation, client acquisition"
        elif "ecommerce" in desc_lower:
            return "Sales conversions, cart abandonment rate, product page views, customer acquisition cost, average order value"
        else:
            return "Website traffic growth, lead generation, conversion rates, engagement metrics, brand awareness"
    
    # Target Audience
    elif "target audience" in prompt_lower:
        if "digital marketing" in desc_lower:
            return "Businesses of all sizes seeking to improve their online presence and digital marketing ROI across multiple industries"
        elif "all genres" in desc_lower or "all types" in desc_lower:
            return "Diverse businesses across multiple industries looking for comprehensive digital marketing solutions"
        else:
            return "Businesses seeking professional marketing services and digital growth solutions"
    
    elif "unique selling proposition" in prompt_lower or "usp" in prompt_lower:
        advantages = []
        if "data-driven" in desc_lower:
            advantages.append("data-driven approach")
        if re.search(r'(\d+)\s*years?', desc_lower):
            years_match = re.search(r'(\d+)\s*years?', desc_lower)
            years = years_match.group(1)
            advantages.append(f"{years}+ years of proven experience")
        if "comprehensive" in desc_lower or "all aspects" in desc_lower:
            advantages.append("comprehensive service offerings")
        
        if advantages:
            return f"Specialized in {', '.join(advantages)} with measurable results"
        else:
            return "Data-driven marketing strategies with proven results and comprehensive service delivery"
    
    elif "main services" in prompt_lower:
        services = []
        service_keywords = {
            'web development': ['web development', 'website development'],
            'SEO': ['seo', 'search engine optimization'],
            'PPC advertising': ['pay-per-click', 'ppc', 'paid advertising'],
            'social media management': ['social media management', 'social media'],
            'social media engagement': ['social media engagement', 'engagement'],
            'video generation': ['video generation', 'video creation'],
            'content marketing': ['content marketing', 'content creation'],
            'email marketing': ['email marketing'],
            'conversion optimization': ['conversion optimization', 'cro'],
            'analytics & reporting': ['analytics', 'reporting', 'data analysis'],
            'brand strategy': ['branding', 'brand strategy'],
            'marketing automation': ['automation', 'marketing automation']
        }
        
        for service, keywords in service_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                services.append(service)
        
        # Add common digital marketing services if none found
        if not services:
            services = ['Digital Marketing Strategy', 'SEO', 'PPC Advertising', 'Social Media Management', 'Web Development']
        
        return ', '.join(services[:6])  # Limit to 6 services
    
    elif "primary keywords" in prompt_lower:
        keywords = []
        if "digital marketing" in desc_lower:
            keywords.extend(["digital marketing", "online marketing"])
        if "seo" in desc_lower:
            keywords.append("SEO services")
        if "ppc" in desc_lower or "pay-per-click" in desc_lower:
            keywords.append("PPC advertising")
        if "social media" in desc_lower:
            keywords.append("social media marketing")
        if "web development" in desc_lower:
            keywords.append("web development")
        
        if not keywords:
            keywords = ["digital marketing", "online marketing", "SEO", "PPC", "social media"]
        
        return ', '.join(keywords[:5])
    
    # Default responses for other question types
    elif "pricing model" in prompt_lower:
        return "Customized pricing packages based on scope and business needs, with monthly retainer and project-based options"
    elif "call to action" in prompt_lower or "call-to-action" in prompt_lower:
        return "Get your free digital marketing audit, Schedule a strategy consultation"
    elif "content tone" in prompt_lower:
        return "Professional and results-focused"
    elif "competitive advantage" in prompt_lower:
        return "Data-driven approach, 15+ years experience, comprehensive service portfolio, measurable ROI"
    elif "content purpose" in prompt_lower:
        return "Lead generation and authority building through educational content"
    else:
        return "Professional response tailored to your business needs and industry requirements"


def generate_fallback_answer(section_key, question_key, business_description):
    """Generate a basic fallback answer if AI service fails"""
    fallback_answers = {
        'business_info': {
            'business_name': 'Your Business Name',
            'industry': 'Professional Services',
            'location': 'Your City, State',
            'target_audience': 'Local customers seeking quality professional services',
            'unique_selling_proposition': 'Quality service with personalized attention and competitive pricing'
        },
        'services_products': {
            'main_services': 'Professional consultation, service delivery, ongoing support',
            'service_benefits': 'Quality results, professional expertise, customer satisfaction, reliable service',
            'pricing_model': 'Competitive pricing with flexible payment options',
            'service_area': 'Local area and surrounding communities'
        },
        'seo_content': {
            'primary_keywords': 'professional services, local business, quality service',
            'secondary_keywords': 'professional services near me, local business solutions, quality service provider, expert consultation, reliable services',
            'content_tone': 'Professional and approachable',
            'content_length': 'Medium-length content with clear structure',
            'call_to_action': 'Contact us today, Get a quote'
        },
        'competitors': {
            'main_competitors': 'Other local professional service providers',
            'competitive_advantage': 'Personalized service, local expertise, competitive pricing',
            'market_position': 'Quality-focused service provider'
        },
        'content_goals': {
            'content_purpose': 'Lead generation and brand awareness',
            'target_actions': 'Contact for consultation, request information',
            'content_distribution': 'Website, social media, local advertising',
            'success_metrics': 'Leads generated, customer inquiries, website traffic'
        }
    }
    
    return fallback_answers.get(section_key, {}).get(question_key, 'Professional response based on your business needs')


def generate_updated_prompt(answers):
    """Generate an updated prompt with all the user's answers filled in"""
    
    # Base prompt template
    base_prompt = """I need you to create a comprehensive SEO content generator that produces spintax formulas for Google Sheets. This generator should create multiple types of content optimized for search engines and user engagement.

**BUSINESS CONTEXT:**"""
    
    # Add business information
    if 'business_info' in answers:
        base_prompt += "\n"
        business = answers['business_info']
        if 'business_name' in business:
            base_prompt += f"- Business Name: {business['business_name']}\n"
        if 'industry' in business:
            base_prompt += f"- Industry: {business['industry']}\n"
        if 'location' in business:
            base_prompt += f"- Location: {business['location']}\n"
        if 'target_audience' in business:
            base_prompt += f"- Target Audience: {business['target_audience']}\n"
        if 'unique_selling_proposition' in business:
            base_prompt += f"- Unique Selling Proposition: {business['unique_selling_proposition']}\n"
    
    # Add services/products section
    if 'services_products' in answers:
        base_prompt += "\n**SERVICES/PRODUCTS:**\n"
        services = answers['services_products']
        if 'main_services' in services:
            base_prompt += f"- Main Services/Products: {services['main_services']}\n"
        if 'service_benefits' in services:
            base_prompt += f"- Key Benefits: {services['service_benefits']}\n"
        if 'pricing_model' in services:
            base_prompt += f"- Pricing Model: {services['pricing_model']}\n"
        if 'service_area' in services:
            base_prompt += f"- Service Area: {services['service_area']}\n"
    
    # Add SEO content preferences
    if 'seo_content' in answers:
        base_prompt += "\n**SEO & CONTENT PREFERENCES:**\n"
        seo = answers['seo_content']
        if 'primary_keywords' in seo:
            base_prompt += f"- Primary Keywords: {seo['primary_keywords']}\n"
        if 'secondary_keywords' in seo:
            base_prompt += f"- Secondary Keywords: {seo['secondary_keywords']}\n"
        if 'content_tone' in seo:
            base_prompt += f"- Content Tone: {seo['content_tone']}\n"
        if 'content_length' in seo:
            base_prompt += f"- Content Length: {seo['content_length']}\n"
        if 'call_to_action' in seo:
            base_prompt += f"- Call-to-Action: {seo['call_to_action']}\n"
    
    # Add competition section
    if 'competitors' in answers:
        base_prompt += "\n**COMPETITION & MARKET:**\n"
        comp = answers['competitors']
        if 'main_competitors' in comp:
            base_prompt += f"- Main Competitors: {comp['main_competitors']}\n"
        if 'competitive_advantage' in comp:
            base_prompt += f"- Competitive Advantage: {comp['competitive_advantage']}\n"
        if 'market_position' in comp:
            base_prompt += f"- Market Position: {comp['market_position']}\n"
    
    # Add content goals
    if 'content_goals' in answers:
        base_prompt += "\n**CONTENT GOALS:**\n"
        goals = answers['content_goals']
        if 'content_purpose' in goals:
            base_prompt += f"- Content Purpose: {goals['content_purpose']}\n"
        if 'target_actions' in goals:
            base_prompt += f"- Target Actions: {goals['target_actions']}\n"
        if 'content_distribution' in goals:
            base_prompt += f"- Content Distribution: {goals['content_distribution']}\n"
        if 'success_metrics' in goals:
            base_prompt += f"- Success Metrics: {goals['success_metrics']}\n"
    
    # Add the requirements section
    base_prompt += """
**CONTENT REQUIREMENTS:**

Please create spintax templates for the following content types:

1. **Landing Page Headlines** (10-15 variations)
   - Include primary keywords naturally
   - Focus on benefits and unique value propositions
   - Create urgency or appeal to emotions
   - Length: 40-60 characters for optimal display

2. **Meta Descriptions** (8-12 variations)
   - Include primary and secondary keywords
   - Clear call-to-action
   - Compelling benefit statements
   - Length: 150-160 characters

3. **Service Page Content** (6-10 variations)
   - Detailed service descriptions
   - Benefits-focused language
   - Include relevant keywords naturally
   - Address common customer pain points
   - Length: 200-300 words per variation

4. **Blog Post Introductions** (8-12 variations)
   - Hook readers immediately
   - Preview the value they'll get
   - Include target keywords
   - Length: 100-150 words

5. **Call-to-Action Buttons** (15-20 variations)
   - Action-oriented language
   - Create urgency
   - Different styles (direct, soft, benefit-focused)
   - Length: 2-5 words

6. **Social Media Posts** (10-15 variations)
   - Platform-optimized content
   - Include hashtags and mentions
   - Engaging and shareable
   - Various post types (promotional, educational, behind-the-scenes)

7. **Email Subject Lines** (12-18 variations)
   - High open-rate focused
   - Personalization elements
   - Urgency and curiosity
   - A/B testing ready

**TECHNICAL REQUIREMENTS:**

- Use Google Sheets SPINTAX_NESTED formula format
- Include {spintax|variations|like|this} for randomization
- Use {{variable}} format for dynamic content insertion
- Ensure each template generates unique, readable content
- Include proper spacing and punctuation
- Make templates that can be combined for longer content

**OUTPUT FORMAT:**

For each content type, provide:
1. The spintax template
2. Sample variables needed ({{business_name}}, {{service}}, {{location}}, etc.)
3. Example of generated content
4. Google Sheets formula ready to copy/paste

Please ensure all content is:
- SEO optimized with natural keyword integration
- Engaging and conversion-focused
- Professional yet approachable
- Scalable for different business needs
- Ready for immediate implementation"""

    return base_prompt


if __name__ == '__main__':
    app.run(debug=True)
