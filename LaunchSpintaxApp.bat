@echo off
REM Launch Spintax Template Generator Flask app
cd /d "%~dp0"
start "Spintax Template Generator" python spintax_template_webapp.py
