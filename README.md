# Spintax Template Generator for Google Sheets

## Project Overview
This project is a modern, user-friendly Python GUI tool for generating spintax content templates and Google Sheets formulas, with advanced variable management and prompt template features. It is designed to help content creators, marketers, and spreadsheet users efficiently create dynamic, randomized text for use in Google Sheets, leveraging both spintax and variable/cell mapping.

## Features
### Main Features

- **Modern Tabbed GUI**: Clean, professional interface using `ttk.Notebook` tabs for logical separation:
  - **Variables Tab**: Manage variables and their corresponding Google Sheets cell references. Add, remove, and clear variables. Enter sample values for previewing template output.
  - **Template Tab**: Edit or use a default spintax template. Preview output with sample values. Generate a ready-to-use Google Sheets formula. Clear template as needed.
  - **Prompt Manager Tab**: Create, edit, save, and delete prompt templates for AI or content generation. Prompts are persisted in a local JSON file.

- **Spintax Support**: Write templates using spintax (e.g., `{option1|option2}`) and variable placeholders (e.g., `{{City}}`).
- **Variable/Cell Mapping**: Map variable names to Google Sheets cell references for formula output. Supports dynamic referencing for parent, sibling, and last sibling relationships.
- **Sample Value Preview**: Instantly preview template output with user-provided sample values.
- **Google Sheets Formula Output**: Generate a formula that can be pasted directly into Google Sheets, with all variables and spintax logic handled. Output is compatible with Google Sheets functions and cell references.
- **Prompt Management**: Save and reuse prompt templates for AI or content workflows. Prompts are stored in a local JSON file for easy access and editing.
- **Internal Linking Logic**: Define and generate internal links within content based on page type (parent, sibling, last sibling) and cell relationships. Automatically includes links to parent/sibling pages using mapped cell references.
- **Dynamic Content Generation**: Content adapts to the selected cell, with context-aware linking and variable substitution for each page type.
- **AI Auto-Fill (Web Version)**: Optionally use AI to auto-fill answers for SEO questions and business info (web version only).
- **Speech Recognition (Web Version)**: Use speech-to-text to fill in answers (web version only).
- **Live Preview (Web Version)**: See a real-time preview of the generated meta prompt as you fill out the form (web version only).
- **Modern Look & Usability**: Uses `ttk` widgets, improved padding, tooltips, and a visually appealing layout for a professional, accessible experience.

### Additional Capabilities

- **Breadcrumb Navigation**: Automatically generate breadcrumb navigation for parent/sibling relationships.
- **Anchor Text Optimization**: Use target keywords and location for anchor text in internal links.
- **FAQ, Schema, and SEO Sections**: Generate FAQ sections, schema markup suggestions, meta titles/descriptions/keywords, and more.
- **Spintax Examples and Guidance**: Built-in examples and instructions for writing effective spintax and nested spintax.
- **Error Handling and User Feedback**: Robust error handling and clear feedback for invalid input or template issues.
- **File Persistence**: All prompt templates are saved locally for reuse.
- **Flexible Output**: Easily copy/paste generated formulas and content into Google Sheets or other tools.

### Use Cases

- Generate dynamic, randomized SEO content for Google Sheets
- Create internal linking structures for large, multi-page sites
- Manage and preview spintax templates with sample data
- Build and reuse prompt templates for AI content workflows
- Automate content generation for location-based or service-based businesses


## Technologies Used
- Python 3
- tkinter & ttk (for GUI)
- scrolledtext (for multi-line text areas)
- re, json, os (for logic and persistence)

## How to Use
1. **Variables Tab**: Enter your main keyword, add variables and their cell references, and provide sample values for previewing.
2. **Template Tab**: Edit the spintax template or use the default. Preview the output with your sample values. Generate and copy the Google Sheets formula.
3. **Prompt Manager Tab**: Manage prompt templates for reuse in AI/content workflows.

4. **Defining Target Cell and Internal Linking**:
   - When generating content for a specific cell (e.g., C3), specify that cell as the target.
   - Use your sheet's structure to map relationships:
     - The sibling page is typically the next row in the same column (e.g., C4).
     - The parent page is dynamically determined by looking left one column and up as many rows as necessary to find the first filled cell (e.g., for C5, search B1:B4 for the last non-blank cell).
   - In your template or prompt, reference these cell mappings so that internal links are dynamically generated:
     - Link to the sibling and parent pages using their cell references.
     - Use anchor text that combines the target keyword and location from the mapped cells.
   - This ensures each generated content block is context-aware and correctly linked within your sheet's structure.
   - Be sure to include this dynamic parent link logic in your meta prompt instructions, so any AI or content generation process uses the correct formula for parent linking. For example, your meta prompt should specify:

     "For each sibling or last sibling page, generate an internal link to the parent page using the following dynamic Google Sheets formula, which finds the first filled cell to the left and above the current cell:

     =LET(
       parentRange, B$1:B4,
       lastFilledRow, MAX(FILTER(ROW(parentRange), parentRange<>"")),
       parentCell, INDEX(parentRange, lastFilledRow),
       IF(parentCell="", "", "<a href='/" & LOWER(SUBSTITUTE(parentCell, " ", "-")) & "'>" & parentCell & "</a>")
     )
     "

   This ensures your generated content and formulas are always context-aware and dynamically linked according to your sheet's structure.
   - Be sure to include this dynamic parent link logic in your meta prompt instructions, so any AI or content generation process uses the correct formula for parent linking. For example, your meta prompt should specify:

     "For each sibling or last sibling page, generate an internal link to the parent page using the following dynamic Google Sheets formula, which finds the first filled cell to the left and above the current cell:

     =LET(
       parentRange, B$1:B4,
       lastFilledRow, MAX(FILTER(ROW(parentRange), parentRange<>"")),
       parentCell, INDEX(parentRange, lastFilledRow),
       IF(parentCell="", "", "<a href='/" & LOWER(SUBSTITUTE(parentCell, " ", "-")) & "'>" & parentCell & "</a>")
     )
     "

   This ensures your generated content and formulas are always context-aware and dynamically linked according to your sheet's structure.

   **Dynamic Parent Link Formula (for sibling and last sibling pages):**
   Use the following Google Sheets formula to always link to the closest parent above in the column to the left:

   ```excel
   =LET(
     parentRange, B$1:B4,
     lastFilledRow, MAX(FILTER(ROW(parentRange), parentRange<>"")),
     parentCell, INDEX(parentRange, lastFilledRow),
     IF(parentCell="", "", "<a href='/" & LOWER(SUBSTITUTE(parentCell, " ", "-")) & "'>" & parentCell & "</a>")
   )
   ```
   - Replace `B$1:B4` with the range from the top of the parent column to the row above your current cell.
   - This formula should be included in all sibling pages and the last sibling page to ensure correct parent linking.

## Recent Improvements
### Recent Improvements

- Complete GUI modernization: all widgets now use `ttk` for a native look.
- Tabbed interface for logical separation and reduced clutter.
- Improved layout, padding, and section separation.
- Tooltips for all key fields and text areas.
- Font and color tweaks for a more modern, readable appearance.
- Robust error handling and user feedback.
- Internal linking logic for parent/sibling/last sibling pages
- Dynamic cell mapping and context-aware content generation
- AI auto-fill, speech recognition, and live preview (web version)
- Enhanced spintax and formula output for Google Sheets
- Flexible prompt management and file persistence

## File Structure
- `spintax_template_gui.py`: Main application file.
- `prompts.json`: Stores user-created prompt templates (auto-created/managed by the app).

## Author & License
Created by Eddie (and GitHub Copilot). License: MIT (or as specified by the user).
