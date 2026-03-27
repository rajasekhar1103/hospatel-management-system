Submission and Packaging Instructions

This file explains how to generate the final PDF, create a submission ZIP, and upload to your course portal.

1) Generate PDF from Markdown (Pandoc recommended)

Install Pandoc and a LaTeX engine (TinyTeX / TeX Live). Then run (PowerShell):

```powershell
pandoc \\"c:\\Users\\nsrn\\Desktop\\HMS_22f3001169\\docs\\project_report.md\" \
  -o \\"c:\\Users\\nsrn\\Desktop\\HMS_22f3001169\\docs\\project_report.pdf\" \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt
```

Or open `project_report.md` in VS Code and use Print → Save as PDF from the Markdown preview.

2) Create a submission ZIP containing source and report

PowerShell commands to create `project_submission.zip` in the workspace root:

```powershell
Set-Location -Path "c:\Users\nsrn\Desktop\HMS_22f3001169"
Compress-Archive -Path backend,frontend,docs -DestinationPath project_submission.zip -Force
```

This will include `backend/`, `frontend/`, and `docs/` (report + diagram + README).

3) Upload to the portal

- Log in to your course portal and follow assignment upload instructions.
- If the portal provides an API or you want me to attempt automated upload, provide the endpoint and API credentials (note: I cannot access external portals without credentials and explicit permission).

4) Provide presentation video Drive link

- If you give the Google Drive link, I will insert it into `docs/project_report.md` and regenerate the PDF.

If you want, I can now:
- Generate the PDF and add it to `docs/` (I will run Pandoc here if available).  
- Create `project_submission.zip` in the repo.  
- Insert your Drive link and regenerate the PDF.

Tell me which actions you want me to perform now.