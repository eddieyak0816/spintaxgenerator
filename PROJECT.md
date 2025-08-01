# Spintax Template Generator Project

## Overview
This project provides a tool for generating spintax content templates for Google Sheets, supporting both a desktop GUI (Tkinter) and a web version (Flask/Bootstrap). It allows users to define variables, map them to cell references, preview content with sample values, generate Google Sheets formulas, and manage prompt templates.

## Features
- **Variable/Cell Mapping:** Define variables and map them to Google Sheets cell references.
- **Spintax Template Editing:** Edit or use a default spintax template with variable placeholders.
- **Preview with Sample Values:** See a live preview of the template with sample values substituted.
- **Google Sheets Formula Output:** Generate a formula for use in Google Sheets, with variables replaced by cell references.
- **Prompt Manager:** Create, save, edit, and delete prompt templates, with persistence in `prompts.json`.
- **Tabbed Interface:** Both desktop and web versions use a tabbed layout for Variables, Template, and Prompt Manager.
- **Modern UI:** The web version uses Bootstrap for a clean, responsive look. The desktop version uses ttk styles and a blue accent color (#1E2E66).

## Desktop Version (Tkinter)
- File: `spintax_template_gui.py`
- Run with: `python spintax_template_gui.py`
- No external dependencies beyond Python's standard library.

## Web Version (Flask)
- File: `spintax_template_webapp.py`
- Requires Flask: Install with `pip install flask`
- Run with: `python spintax_template_webapp.py`
- Open the provided local URL (e.g., http://127.0.0.1:5000/) in Chrome or any browser.
- UI uses Bootstrap via CDN, no extra frontend build required.

## Data Persistence
- Prompts are saved in `prompts.json` in the project directory.

## Usage
1. **Variables Tab:**
   - Add variables and their cell references.
   - Remove or clear variables as needed.
2. **Template Tab:**
   - Edit the spintax template or use the default.
   - Enter sample values for preview.
   - Generate a Google Sheets formula.
3. **Prompt Manager Tab:**
   - Create, save, update, or delete prompt templates.

## Project Structure
- `spintax_template_gui.py` — Desktop GUI version
- `spintax_template_webapp.py` — Web version (Flask)
- `prompts.json` — Stores user prompt templates

## Requirements
- Python 3.7+
- Flask (for web version)

## License
This project is for personal and business use. Please contact the author for redistribution or commercial licensing.

---
For questions or improvements, contact the project maintainer.
