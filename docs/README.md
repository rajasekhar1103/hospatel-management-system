# Docs README

This folder contains the project report in Markdown format and instructions to create a PDF for printing or submission.

Files:

- `project_report.md` — two-page project report content.

How to convert to PDF (recommended):

1) Using Pandoc (cross-platform):

Install Pandoc (https://pandoc.org/installing.html) and a LaTeX engine such as TinyTeX or TeX Live if you want high-quality PDF output.

Example PowerShell command:

```powershell
pandoc 
  c:\Users\nsrn\Desktop\HMS_22f3001169\docs\project_report.md 
  -o c:\Users\nsrn\Desktop\HMS_22f3001169\docs\project_report.pdf 
  --pdf-engine=xelatex 
  -V geometry:margin=1in 
  -V fontsize=11pt
```

2) Using VS Code: open `project_report.md`, then use the built-in "Print" or "Export to PDF" functionality from the Markdown preview (or install an extension that converts Markdown to PDF).

3) Quick but lower-fidelity method: open the Markdown in a browser or the editor preview and use "Print" → "Save as PDF".

If you want, I can generate the PDF here for you and add it to `docs/` (if you approve), or adjust formatting to a university or submission template.
