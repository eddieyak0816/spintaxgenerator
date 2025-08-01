import os
import json

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), 'prompts.json')

DEFAULT_TEMPLATE = '''<p>{Transform|Elevate|Enhance} your {{main_keyword}} home with {stunning|beautiful|exquisite} {{product}} from {{company}}. We {proudly serve|cater to|specialize in serving} homeowners throughout {{main_keyword}} and the surrounding areas of {{location}}, {delivering|providing|offering} {top-quality|premium|superior} {{product}} that {combine|blend|merge} {durability|strength|resilience} with {timeless|classic|enduring} {beauty|elegance|appeal}.</p>'''

def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_prompts(prompts):
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2)
