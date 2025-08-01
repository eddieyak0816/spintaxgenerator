# Spintax Template Generator for Google Sheets

## Project Overview
This project is a modern, user-friendly Python GUI tool for generating spintax content templates and Google Sheets formulas, with advanced variable management and prompt template features. It is designed to help content creators, marketers, and spreadsheet users efficiently create dynamic, randomized text for use in Google Sheets, leveraging both spintax and variable/cell mapping.

## Features
- **Modern Tabbed GUI**: Clean, professional interface using `ttk.Notebook` tabs for logical separation:
  - **Variables Tab**: Manage variables and their corresponding Google Sheets cell references. Add, remove, and clear variables. Enter sample values for previewing template output.
  - **Template Tab**: Edit or use a default spintax template. Preview output with sample values. Generate a ready-to-use Google Sheets formula. Clear template as needed.
  - **Prompt Manager Tab**: Create, edit, save, and delete prompt templates for AI or content generation. Prompts are persisted in a local JSON file.
- **Spintax Support**: Write templates using spintax (e.g., `{option1|option2}`) and variable placeholders (e.g., `{{City}}`).
- **Variable/Cell Mapping**: Map variable names to Google Sheets cell references for formula output.
- **Sample Value Preview**: Instantly preview template output with user-provided sample values.
- **Google Sheets Formula Output**: Generate a formula that can be pasted directly into Google Sheets, with all variables and spintax logic handled.
- **Prompt Management**: Save and reuse prompt templates for AI or content workflows.
- **Modern Look & Usability**: Uses `ttk` widgets, improved padding, tooltips, and a visually appealing layout for a professional, accessible experience.

## Technologies Used
- Python 3
- tkinter & ttk (for GUI)
- scrolledtext (for multi-line text areas)
- re, json, os (for logic and persistence)

## How to Use
1. **Variables Tab**: Enter your main keyword, add variables and their cell references, and provide sample values for previewing.
2. **Template Tab**: Edit the spintax template or use the default. Preview the output with your sample values. Generate and copy the Google Sheets formula.
3. **Prompt Manager Tab**: Manage prompt templates for reuse in AI/content workflows.

## Recent Improvements
- Complete GUI modernization: all widgets now use `ttk` for a native look.
- Tabbed interface for logical separation and reduced clutter.
- Improved layout, padding, and section separation.
- Tooltips for all key fields and text areas.
- Font and color tweaks for a more modern, readable appearance.
- Robust error handling and user feedback.

## File Structure
- `spintax_template_gui.py`: Main application file.
- `prompts.json`: Stores user-created prompt templates (auto-created/managed by the app).

## Author & License
Created by Eddie (and GitHub Copilot). License: MIT (or as specified by the user).
