import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import re
import json
import os
from tkinter import ttk

class SpintaxTemplateGUI:
    def add_variable(self):
        name = self.var_name.get().strip()
        cell = self.var_cell.get().strip()
        if not name or not cell:
            messagebox.showwarning("Input Error", "Please enter both variable name and cell reference.")
            return
        self.variables[name] = cell
        self.vars_list.insert(tk.END, f"{name} → {cell}")
        self.var_name.delete(0, tk.END)
        self.var_cell.delete(0, tk.END)
        self.update_sample_entries()

    def update_sample_entries(self):
        # Remove old widgets
        for widget in self.sample_frame.winfo_children():
            widget.destroy()
        self.sample_entries.clear()
        # Add entry for each variable
        for idx, var in enumerate(self.variables):
            tk.Label(self.sample_frame, text=f"{var}:").grid(row=idx, column=0, sticky='w')
            entry = tk.Entry(self.sample_frame, width=20)
            entry.grid(row=idx, column=1, sticky='w')
            self.sample_entries[var] = entry

    def preview_with_samples(self):
        # Get sample values
        sample_values = {var: entry.get() for var, entry in self.sample_entries.items()}
        main_kw = self.main_keyword_entry.get().strip()
        if main_kw:
            sample_values['main_keyword'] = main_kw
        if self.use_default.get():
            template = self.default_template
        else:
            template = self.template_text.get('1.0', tk.END).strip()
        preview = template
        # Replace variable placeholders ({{var}}) with sample values
        for var, val in sample_values.items():
            preview = preview.replace(f'{{{{{var}}}}}', val)
        # Also replace all occurrences of cell references with sample values (case-insensitive, robust)
        for var, cell in self.variables.items():
            val = sample_values.get(var, '')
            if cell:
                # Use regex to replace all case-insensitive occurrences, even if surrounded by HTML or at line start/end
                pattern = re.compile(re.escape(cell.strip()), re.IGNORECASE)
                preview = pattern.sub(val, preview)
        self.preview_box.config(state='normal')
        self.preview_box.delete('1.0', tk.END)
        self.preview_box.insert('1.0', preview)
        self.preview_box.config(state='disabled')

    # --- Prompt Manager Methods ---
    def load_prompts(self):
        if os.path.exists(self.prompts_file):
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_prompts(self):
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            json.dump(self.prompts, f, indent=2)

    def refresh_prompt_list(self):
        self.prompt_listbox.delete(0, tk.END)
        for name in self.prompts:
            self.prompt_listbox.insert(tk.END, name)

    def new_prompt(self):
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_listbox.selection_clear(0, tk.END)

    def save_prompt(self):
        prompt = self.prompt_text.get('1.0', tk.END).strip()
        if not prompt:
            messagebox.showwarning("Input Error", "Prompt text cannot be empty.")
            return
        name = simpledialog.askstring("Prompt Name", "Enter a name for this prompt:")
        if not name:
            return
        self.prompts[name] = prompt
        self.save_prompts()
        self.refresh_prompt_list()
        messagebox.showinfo("Saved", f"Prompt '{name}' saved.")

    def update_prompt(self):
        sel = self.prompt_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Prompt", "Select a prompt to update.")
            return
        name = self.prompt_listbox.get(sel[0])
        prompt = self.prompt_text.get('1.0', tk.END).strip()
        if not prompt:
            messagebox.showwarning("Input Error", "Prompt text cannot be empty.")
            return
        self.prompts[name] = prompt
        self.save_prompts()
        self.refresh_prompt_list()
        messagebox.showinfo("Updated", f"Prompt '{name}' updated.")

    def delete_prompt(self):
        sel = self.prompt_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Prompt", "Select a prompt to delete.")
            return
        name = self.prompt_listbox.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete prompt '{name}'?"):
            del self.prompts[name]
            self.save_prompts()
            self.refresh_prompt_list()
            self.prompt_text.delete('1.0', tk.END)

    def load_selected_prompt(self, event=None):
        sel = self.prompt_listbox.curselection()
        if not sel:
            return
        name = self.prompt_listbox.get(sel[0])
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', self.prompts[name])
    def __init__(self, root):
        self.root = root
        self.variables = {}
        self.default_template = '''<p>{Transform|Elevate|Enhance} your {{main_keyword}} home with {stunning|beautiful|exquisite} {{product}} from {{company}}. We {proudly serve|cater to|specialize in serving} homeowners throughout {{main_keyword}} and the surrounding areas of {{location}}, {delivering|providing|offering} {top-quality|premium|superior} {{product}} that {combine|blend|merge} {durability|strength|resilience} with {timeless|classic|enduring} {beauty|elegance|appeal}.</p>'''
        self.root.title("Spintax Template Generator for Google Sheets")
        self.root.geometry("800x600")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f7f7fa')
        style.configure('Section.TFrame', background='#eaf3fb', borderwidth=1, relief='solid')
        style.configure('Header.TFrame', background='#1E2E66')
        style.configure('TLabel', background='#f7f7fa', font=('Segoe UI', 10))
        style.configure('Section.TLabel', background='#eaf3fb', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#1E2E66', foreground='white', font=('Segoe UI', 16, 'bold'))
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), background='#1E2E66', foreground='white')
        style.map('Accent.TButton', background=[('active', '#16204a')], foreground=[('active', 'white')])
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), background='#e0e7ef', foreground='#222')
        style.map('TButton', background=[('active', '#c7d2fe')])
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCheckbutton', background='#f7f7fa', font=('Segoe UI', 10))

        # Add a colored header
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill='x')
        ttk.Label(header, text="Spintax Template Generator for Google Sheets", style='Header.TLabel').pack(padx=20, pady=12, anchor='w')

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Variables Tab ---
        self.tab_vars = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vars, text="Variables")

        vars_outer = ttk.Frame(self.tab_vars, style='Section.TFrame')
        vars_outer.pack(fill='both', expand=True, padx=20, pady=20)

        # Main Keyword
        ttk.Label(vars_outer, text="Main Keyword:", style='Section.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        self.main_keyword_entry = ttk.Entry(vars_outer, width=30)
        self.main_keyword_entry.grid(row=0, column=1, columnspan=2, sticky='w', pady=(0,5))
        self._add_tooltip(self.main_keyword_entry, "The main keyword for your template.")

        # Variable Name/Cell
        ttk.Label(vars_outer, text="Variable Name:", style='Section.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Label(vars_outer, text="Cell Reference:", style='Section.TLabel').grid(row=1, column=1, sticky='w')
        self.var_name = ttk.Entry(vars_outer, width=15)
        self.var_name.grid(row=2, column=0, padx=(0,5))
        self._add_tooltip(self.var_name, "Name for your variable, e.g. product")
        self.var_cell = ttk.Entry(vars_outer, width=10)
        self.var_cell.grid(row=2, column=1, padx=(0,5))
        self._add_tooltip(self.var_cell, "Google Sheets cell reference, e.g. B2")
        ttk.Button(vars_outer, text="Add Variable", command=self.add_variable, style='Accent.TButton').grid(row=2, column=2, padx=(0,5))

        # Variables List
        ttk.Label(vars_outer, text="Variables List:", style='Section.TLabel').grid(row=3, column=0, columnspan=2, sticky='w', pady=(10,0))
        self.vars_list = tk.Listbox(vars_outer, width=40, height=5, font=('Segoe UI', 10))
        self.vars_list.grid(row=4, column=0, columnspan=2, pady=5, sticky='w')
        ttk.Button(vars_outer, text="Remove Selected", command=self.remove_variable).grid(row=4, column=2, sticky='e', padx=(0,5))
        ttk.Button(vars_outer, text="Clear All Variables", command=self.clear_all_variables).grid(row=5, column=2, sticky='e', pady=(0,10), padx=(0,5))

        # Sample Values
        ttk.Label(vars_outer, text="Sample Values for Preview:", style='Section.TLabel').grid(row=6, column=0, columnspan=3, sticky='w', pady=(10,0))
        self.sample_entries = {}
        self.sample_frame = ttk.Frame(vars_outer)
        self.sample_frame.grid(row=7, column=0, columnspan=3, sticky='w', pady=(0,10))
        self.update_sample_entries()

        # --- Template Tab ---
        self.tab_template = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_template, text="Template")


        template_outer = ttk.Frame(self.tab_template, style='Section.TFrame')
        template_outer.pack(fill='both', expand=True, padx=20, pady=20)


        self.use_default = tk.BooleanVar(value=True)
        ttk.Checkbutton(template_outer, text="Use default template", variable=self.use_default, command=self.toggle_template).grid(row=0, column=0, columnspan=3, sticky='w')

        ttk.Label(template_outer, text="Spintax Template (editable):").grid(row=1, column=0, columnspan=3, sticky='w')
        ttk.Label(template_outer, text="Tip: Use variable names like {{City}} in your template. Cell references (e.g., A1) are for formula output only.", foreground="#888").grid(row=1, column=1, columnspan=2, sticky='e')
        self.template_text = scrolledtext.ScrolledText(template_outer, width=60, height=6)
        self.template_text.grid(row=2, column=0, columnspan=3)
        self.template_text.insert('1.0', self.default_template)
        self.template_text.config(state='normal')

        ttk.Button(template_outer, text="Preview with Sample Values", command=self.preview_with_samples).grid(row=3, column=0, pady=10)
        ttk.Button(template_outer, text="Generate Formula", command=self.generate_formula).grid(row=3, column=1)
        ttk.Button(template_outer, text="Clear Spintax Template", command=self.clear_spintax_template).grid(row=3, column=2)

        ttk.Label(template_outer, text="Preview:").grid(row=4, column=0, columnspan=3, sticky='w')
        self.preview_box = scrolledtext.ScrolledText(template_outer, width=60, height=4)
        self.preview_box.grid(row=5, column=0, columnspan=3)
        self.preview_box.config(state='disabled')

        ttk.Label(template_outer, text="Google Sheets Formula:").grid(row=6, column=0, columnspan=3, sticky='w')
        self.formula_box = scrolledtext.ScrolledText(template_outer, width=60, height=4)
        self.formula_box.grid(row=7, column=0, columnspan=3)
        self.formula_box.config(state='disabled')

        # --- Prompt Manager Tab ---
        self.tab_prompts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prompts, text="Prompt Manager")

        prompts_outer = ttk.Frame(self.tab_prompts, style='Section.TFrame')
        prompts_outer.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(prompts_outer, text="Prompt Manager:").grid(row=0, column=0, sticky='w', pady=(10,0))
        self.prompt_listbox = tk.Listbox(prompts_outer, width=30, height=5, font=('Segoe UI', 10))
        self.prompt_listbox.grid(row=1, column=0, rowspan=4, sticky='n', pady=(0,10))
        self.prompt_listbox.bind('<<ListboxSelect>>', self.load_selected_prompt)

        self.prompt_text = scrolledtext.ScrolledText(prompts_outer, width=40, height=5, font=('Segoe UI', 10))
        self.prompt_text.grid(row=1, column=1, rowspan=2, columnspan=2, sticky='n', pady=(0,10))
        self._add_tooltip(self.prompt_text, "Edit or create prompt templates here.")

        ttk.Button(prompts_outer, text="New Prompt", command=self.new_prompt).grid(row=3, column=1, sticky='w', pady=(0,5))
        ttk.Button(prompts_outer, text="Save Prompt", command=self.save_prompt).grid(row=3, column=2, sticky='w', pady=(0,5))
        ttk.Button(prompts_outer, text="Update Prompt", command=self.update_prompt).grid(row=4, column=1, sticky='w')
        ttk.Button(prompts_outer, text="Delete Prompt", command=self.delete_prompt).grid(row=4, column=2, sticky='w')
    def _init_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Light mode
        style.configure('TFrame', background='#f7f7fa')
        style.configure('Section.TFrame', background='#eaf3fb', borderwidth=1, relief='solid')
        style.configure('Header.TFrame', background='#1E2E66')
        style.configure('TLabel', background='#f7f7fa', font=('Segoe UI', 10))
        style.configure('Section.TLabel', background='#eaf3fb', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#1E2E66', foreground='white', font=('Segoe UI', 16, 'bold'))
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), background='#1E2E66', foreground='white')
        style.map('Accent.TButton', background=[('active', '#16204a')], foreground=[('active', 'white')])
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), background='#e0e7ef', foreground='#222')
        style.map('TButton', background=[('active', '#c7d2fe')])
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCheckbutton', background='#f7f7fa', font=('Segoe UI', 10))
        style.configure('Header.TCheckbutton', background='#1E2E66', foreground='white', font=('Segoe UI', 10, 'bold'))
        # Dark mode
        # Improved dark mode palette
        style.configure('Dark.TFrame', background='#151922')  # main bg
        style.configure('DarkSection.TFrame', background='#23273a', borderwidth=1, relief='solid')  # section bg
        style.configure('DarkHeader.TFrame', background='#1E2E66')
        style.configure('Dark.TLabel', background='#151922', foreground='#e3e8f0', font=('Segoe UI', 10))
        style.configure('DarkSection.TLabel', background='#23273a', foreground='#e3e8f0', font=('Segoe UI', 10))
        style.configure('DarkHeader.TLabel', background='#1E2E66', foreground='#f3f6fa', font=('Segoe UI', 16, 'bold'))
        style.configure('DarkAccent.TButton', font=('Segoe UI', 10, 'bold'), background='#1E2E66', foreground='#f3f6fa')
        style.map('DarkAccent.TButton', background=[('active', '#16204a')], foreground=[('active', '#f3f6fa')])
        style.configure('Dark.TButton', font=('Segoe UI', 10, 'bold'), background='#23273a', foreground='#e3e8f0')
        style.map('Dark.TButton', background=[('active', '#1E2E66')])
        style.configure('Dark.TEntry', font=('Segoe UI', 10), fieldbackground='#23273a', foreground='#e3e8f0')
        style.configure('Dark.TCheckbutton', background='#151922', foreground='#e3e8f0', font=('Segoe UI', 10))
        style.configure('DarkHeader.TCheckbutton', background='#1E2E66', foreground='#f3f6fa', font=('Segoe UI', 10, 'bold'))

    def _toggle_dark_mode(self):
        dark = self.dark_mode.get()
        style = ttk.Style()
        if dark:
            style.theme_use('clam')
            style.configure('TFrame', background='#151922')
            style.configure('Section.TFrame', background='#23273a')
            style.configure('Header.TFrame', background='#1E2E66')
            style.configure('TLabel', background='#151922', foreground='#e3e8f0')
            style.configure('Section.TLabel', background='#23273a', foreground='#e3e8f0')
            style.configure('Header.TLabel', background='#1E2E66', foreground='#f3f6fa')
            style.configure('Accent.TButton', background='#1E2E66', foreground='#f3f6fa')
            style.map('Accent.TButton', background=[('active', '#16204a')], foreground=[('active', '#f3f6fa')])
            style.configure('TButton', background='#23273a', foreground='#e3e8f0')
            style.map('TButton', background=[('active', '#1E2E66')])
            style.configure('TEntry', fieldbackground='#23273a', foreground='#e3e8f0')
            style.configure('TCheckbutton', background='#151922', foreground='#e3e8f0')
        else:
            self._init_styles()
        # Update scrolledtext backgrounds manually
        bg = '#23273a' if dark else '#fff'
        fg = '#e3e8f0' if dark else '#222'
        for box in [getattr(self, n, None) for n in ['preview_box', 'formula_box', 'prompt_text']]:
            if box:
                box.config(bg=bg, fg=fg, insertbackground=fg)

        # (Prompt action buttons are now handled in the new layout)

        self.prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.json')
        self.prompts = self.load_prompts()
        self.refresh_prompt_list()

    def _add_tooltip(self, widget, text):
        # Simple tooltip for ttk/tk widgets
        def on_enter(event):
            self._tooltip = tk.Toplevel(widget)
            self._tooltip.wm_overrideredirect(True)
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            self._tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self._tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1, font=('Segoe UI', 9))
            label.pack(ipadx=4, ipady=2)
        def on_leave(event):
            if hasattr(self, '_tooltip'):
                self._tooltip.destroy()
                del self._tooltip
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    def remove_variable(self):
        sel = self.vars_list.curselection()
        if not sel:
            return
        idx = sel[0]
        var = self.vars_list.get(idx).split('→')[0].strip()
        self.vars_list.delete(idx)
        if var in self.variables:
            del self.variables[var]
        self.update_sample_entries()

    def toggle_template(self):
        if self.use_default.get():
            self.template_text.config(state='normal')
            self.template_text.delete('1.0', tk.END)
            self.template_text.insert('1.0', self.default_template)
            self.template_text.config(state='disabled')
        else:
            self.template_text.config(state='normal')
            self.template_text.delete('1.0', tk.END)

    def generate_formula(self):
        if self.use_default.get():
            template = self.default_template
            found_vars = set(re.findall(r'\{\{(.*?)\}\}', template))
            missing = found_vars - set(self.variables.keys())
            # Always allow main_keyword if present in the dedicated field
            if 'main_keyword' in found_vars and 'main_keyword' not in self.variables:
                missing = missing - {'main_keyword'}
            if missing:
                messagebox.showwarning("Missing Variables", f"The template uses variables you did not define: {', '.join(missing)}")
                return
        else:
            template = self.template_text.get('1.0', tk.END).strip()
            found_vars = set(re.findall(r'\{\{(.*?)\}\}', template))
            missing = found_vars - set(self.variables.keys())
            if 'main_keyword' in found_vars and 'main_keyword' not in self.variables:
                missing = missing - {'main_keyword'}
            if missing:
                messagebox.showwarning("Missing Variables", f"The template uses variables you did not define: {', '.join(missing)}")
                return
        # Replace variables with cell references
        for var, cell in self.variables.items():
            template = template.replace(f'{{{{{var}}}}}', f'" & {cell} & "')
        # Replace main_keyword if present
        main_kw = self.main_keyword_entry.get().strip()
        if 'main_keyword' in template and main_kw:
            template = template.replace('{{main_keyword}}', f'" & "{main_kw}" & "')
        formula = f'=SUBSTITUTE(SPINTAX(CONCATENATE("{template}")), "", "")'
        self.formula_box.config(state='normal')
        self.formula_box.delete('1.0', tk.END)
        self.formula_box.insert('1.0', formula)
        self.formula_box.config(state='disabled')

    def copy_formula(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.formula_box.get('1.0', tk.END).strip())
        messagebox.showinfo("Copied", "Formula copied to clipboard!")

    def clear_all(self):
        self.variables.clear()
        self.vars_list.delete(0, tk.END)
        self.var_name.delete(0, tk.END)
        self.var_cell.delete(0, tk.END)
        self.formula_box.config(state='normal')
        self.formula_box.delete('1.0', tk.END)
        self.formula_box.config(state='disabled')
        self.use_default.set(True)
        self.toggle_template()

    def clear_all_variables(self):
        self.variables.clear()
        self.vars_list.delete(0, tk.END)
        self.update_sample_entries()

    def clear_spintax_template(self):
        self.template_text.delete('1.0', tk.END)

    # ...existing code...
if __name__ == "__main__":
    root = tk.Tk()
    app = SpintaxTemplateGUI(root)
    root.mainloop()
