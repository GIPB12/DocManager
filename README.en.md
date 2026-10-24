<div align="center">

[🇧🇷 Português](README.md) | **🇺🇸 English**

# DocManager

**Python desktop system for listing files, generating reports, and organizing documents while updating Excel spreadsheets.**

</div>

## About the project

**DocManager** was created to simplify repetitive file-management tasks. Version 1.0 was a single script for listing files and generating reports. In version 2.0, the project evolved into an application with separate modules, a graphical interface, and document processing for expense spreadsheets.

## Features

### File listing

- Select a folder and list the files it contains.
- Optionally include subfolders.
- Export the file list to a TXT report.
- Print a report on Windows.

### Document and spreadsheet organization

- Read documents placed in the `NOVOS` (New) folder.
- Extract the date, description, amount, and service type from filenames.
- Validate extracted information and visually flag invalid data.
- Create monthly spreadsheets from an Excel template.
- Detect potential duplicate entries and request confirmation before registering them.
- Record document information in the appropriate spreadsheets.
- Move processed documents into folders organized by service type, year, and month.
- Keep documents with validation errors in `NOVOS` for correction.
- Archive documents only after the spreadsheet entry has been saved.

## Project evolution

| Version | Description |
| --- | --- |
| **1.0** | Single script for listing files and generating reports. |
| **2.0** | Modular desktop application with document validation, file organization, and Excel spreadsheet integration. |

Version 1.0 and an earlier document-organization module are stored in `Versões Antigas/` (Older Versions). **The three Python files in the project root are the current version's modules.**

## Technologies

- **Python** — application logic.
- **Tkinter / ttk** — graphical user interface.
- **Tksheet** — tabular data display.
- **OpenPyXL** — reading and updating Excel files.
- **Pillow** — support for images embedded in the spreadsheet template.

## Project structure

```text
DocManager/
├── main.py       # Entry point and main interface
├── listador_arquivos.py      # File listing and reports
├── atualizar_planilha.py     # Validation and spreadsheet updates
├── MODELO/                   # Excel template used by the application
├── PLANILHAS/                # Generated spreadsheets (not tracked)
├── Versões Antigas/          # Previous versions and earlier module
├── README.md
├── README.en.md
├── requirements.txt
└── .gitignore
```

During operation, the document workflow uses the `NOVOS` folder and sorts processed files by service type, year, and month. For example:

```text
Sistema/
├── NOVOS/
├── MODELO/
├── PLANILHAS/
├── CONTÁBIL/
│   └── 2026/
│       └── 10/
├── NÃO CONTÁBIL/
└── AUDITORES/
```

Service-type folders are created or used as documents are processed.

## Document naming convention

Automatic processing expects filenames in this format:

```text
dd.mm.yy description (amount) service type.ext
```

Example (using the Portuguese service-type name expected by the application):

```text
11.10.26 descrição teste (100,00) contábil.pdf
```

Supported service types: **CONTÁBIL** (Accounting), **NÃO CONTÁBIL** (Non-accounting), and **AUDITORES** (Auditors). The application expects the original Portuguese labels in filenames. Invalid fields are highlighted in the validation table. The current spreadsheet layout uses rows 9 through 38 for entries in each worksheet.

## Installation and usage

1. Clone the repository and open its directory:

   ```bash
   git clone https://github.com/GIPB12/DocManager.git
   cd DocManager
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Make sure the `MODELO` folder contains **exactly one `.xlsx` file**, with worksheets for CONTÁBIL, NÃO CONTÁBIL and AUDITORES. The `NOVOS` folder is created automatically when the validation screen opens.

4. Start the application:

   ```bash
   python main.py
   ```

> **Compatibility:** the project was developed for Windows. Running it on Windows 7 requires Python and dependency versions compatible with that operating system.

## Notes

- The application window is still titled `Sistema de Documentos` in the current source code. Renaming the repository and entry-point file does not automatically change the window title.
- The spreadsheet naming function still uses a fixed name in the source code; this documentation does not change that behavior.

- Do not upload real documents or spreadsheets containing confidential information.
- The `PLANILHAS` folder contains generated files and does not need to be tracked by Git.
- The clone command assumes the repository will be published as `GIPB12/DocManager`.

## Author

**Giovanni Pinheiro Bonifatto**  
[GitHub](https://github.com/GIPB12) · [LinkedIn](https://www.linkedin.com/in/giovanni-bonifatto)
