## Meta Prompt Instructions for Internal Linking

When generating content for sibling or last sibling pages, always include instructions in your meta prompt for dynamic parent linking. Specify that the AI/content generator should use the following Google Sheets formula to find the first filled cell to the left and above the current cell:

```excel
=LET(
  parentRange, B$1:B4,
  lastFilledRow, MAX(FILTER(ROW(parentRange), parentRange<>"")),
  parentCell, INDEX(parentRange, lastFilledRow),
  IF(parentCell="", "", "<a href='/" & LOWER(SUBSTITUTE(parentCell, " ", "-")) & "'>" & parentCell & "</a>")
)
```

This ensures all generated content and formulas are context-aware and dynamically linked according to your sheet's structure.
# Spintax Template Generator for Google Sheets

## Project Overview
A Flask web application for generating spintax templates and Google Sheets formulas, with robust variable and prompt management. The app features a modern Bootstrap UI and modular Python backend.

## Key Features
- **Variables Tab:** Add, remove, and clear variable-to-cell mappings for template generation.
- **Template Tab:** Edit spintax templates, preview with sample values, generate Google Sheets formulas, and select templates from a dropdown.
- **Template Manager Tab:** Add, edit, load, and delete named templates. Dropdown selection loads template; Save/Delete buttons perform respective actions.
- **Flexible Template Recognition:** Both variable placeholders (`{{City}}`) and direct cell references (`A1`, `B1`) in the template are recognized and correctly output as cell references in the Google Sheets formula.
- **Debugging:** Backend print statements and frontend debug block for troubleshooting.
- **Modular Codebase:** Separate modules for spintax logic and template management.

## Recent Changes (as of August 1, 2025)
- Refactored formula generation logic:
  - Now recognizes both `{{variable}}` and direct cell references (e.g., `A1`, `B1`) in the template.
  - Formula output correctly separates cell references from quoted text for Google Sheets compatibility.
- Template Tab now includes a dropdown to select and load templates, filling the Spintax Template textarea.
- All requested UI and backend changes for robust template management are complete.

## Next Steps
- User to confirm all prompt management actions work as expected.
- Address any further bugs or feature requests as needed.

## File References
- `spintax_template_webapp.py`: Main Flask app, backend logic, debugging.
- `spintax_utils.py`: Spintax preview and formula generation logic.
- `templates/index.html`: Jinja2 template, UI, form action handling, debug block.

## Status
- All core features implemented and tested.
- Codebase is modular, maintainable, and user-friendly.
- Ready for further development or documentation updates.
