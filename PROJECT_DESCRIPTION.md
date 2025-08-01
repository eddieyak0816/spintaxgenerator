# Project: Spintax Template Generator for Google Sheets

## Purpose
Create a Python tool that helps users generate spintax-based content templates for use in Google Sheets. The tool will:
- Prompt the user for a main keyword, related keywords, company name, services, locations, and other relevant information.
- Allow the user to use a default spintax template or input a custom one, with variables for easy substitution.
- Replace variables in the template with Google Sheets cell references (e.g., H2, I2, J2, K2).
- Output a Google Sheets-ready formula that uses a custom SPINTAX Apps Script function to generate unique content in bulk, without further AI/token usage.
- Optionally save the generated formula to a file for later use.

## What is the Spintax Formula in Google Sheets?

The spintax formula in Google Sheets is a formula that uses a custom Apps Script function (commonly called `SPINTAX`) to process spintax-formatted text and generate unique content. The formula output by this tool typically looks like:

```
=SUBSTITUTE(SPINTAX(CONCATENATE("...spintax template with cell references...")), "", "")
```

- `SPINTAX(...)` is a custom function you must define in your Google Sheet using Apps Script. It parses and randomly selects options from spintax (e.g., `{red|blue|green}`).
- `CONCATENATE("...")` joins together the template and cell references.
- `SUBSTITUTE(..., "", "")` is a placeholder and can be adjusted as needed.

When you paste this formula into a Google Sheets cell, it generates a unique version of your spintax template for each row, using the values from the referenced cells. The actual `SPINTAX` function must be implemented in your Google Sheets via Apps Script for this to work.

## Workflow
1. User runs the Python script.
2. User is prompted for required information (main keyword, product, company, location, etc.).
3. User chooses to use the default template or provides a custom spintax template.
4. The script replaces variables with cell references and outputs a Google Sheets formula.
5. User can save the formula to a file.

## Key Features
- Spintax support for content variation.
- Variable substitution for Google Sheets integration.
- Simple CLI interface.
- Easy to update/extend with new variables or templates.

## Next Steps
- Continue to refine the script based on user feedback.
- Add support for more variables or template sections if needed.
- Update this file as the project evolves, with user approval.

---

_Last updated: July 31, 2025_
