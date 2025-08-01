# Spintax Template Generator for Google Sheets

## Project Overview
A Flask web application for generating spintax templates and Google Sheets formulas, with robust variable and prompt management. The app features a modern Bootstrap UI and modular Python backend.

## Key Features
- **Variables Tab:** Add, remove, and clear variable-to-cell mappings for template generation.
- **Template Tab:** Edit spintax templates, preview with sample values, and generate Google Sheets formulas.
- **Prompt Manager Tab:** Add, edit, load, and delete named prompts. Dropdown selection loads prompt; Save/Delete buttons perform respective actions.
- **Debugging:** Backend print statements and frontend debug block for troubleshooting.
- **Modular Codebase:** Separate modules for spintax logic and prompt management.

## Recent Changes (as of August 1, 2025)
- Refactored form action handling in Prompt Manager tab:
  - Dropdown selection uses JS to set a temporary hidden action field for loading prompts.
  - Save/Delete buttons use their own action values, ensuring reliable prompt management.
  - Removed persistent hidden action field to prevent action conflicts.
- Confirmed reliable add, edit, and delete functionality for prompts in the web UI.
- Debug block displays current form state for easier troubleshooting.

## Next Steps
- User to confirm all prompt management actions work as expected.
- Address any further bugs or feature requests as needed.

## File References
- `spintax_template_webapp.py`: Main Flask app, backend logic, debugging.
- `templates/index.html`: Jinja2 template, UI, form action handling, debug block.

## Status
- All core features implemented and tested.
- Codebase is modular, maintainable, and user-friendly.
- Ready for further development or documentation updates.
