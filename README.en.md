<div align="center">

[🇧🇷 Português](README.md) | **🇺🇸 English**

# DocManager

**Python desktop application for file listing, report generation, document organization, Excel spreadsheet updates, and file compression.**

</div>

## About the project

**DocManager** was created to simplify repetitive file and document management tasks. Version 1.0 was a single script for listing files and generating reports. In version 2.0, the project evolved into a modular application with a graphical interface and document processing for expense spreadsheets.

The application brings independent tools together in a main interface, allowing users to list, organize, and compress documents.

## Features

### Main interface

- Main menu providing access to the system modules.
- Module icons arranged side by side.
- Interface adapts to window resizing while keeping the main elements visible.

### File listing

- Select a folder and list the files it contains.
- Optionally include subfolders.
- Export the file list to a TXT report.
- Print a report on Windows.

### Document and spreadsheet organization

- Read documents placed in the `NOVOS` (New) folder.
- Extract the date, description, amount, and service type from filenames.
- Validate extracted information and visually flag invalid data.
- Display identified data for review before processing.
- Create monthly spreadsheets from an Excel template.
- Detect potential duplicate entries and request confirmation before registering them.
- Record document information in the appropriate spreadsheets.
- Move processed documents into folders organized by service type, year, and month.
- Keep documents with validation errors in `NOVOS` for correction.
- Archive documents only after the spreadsheet entry has been saved.

### Document compression

- List the monthly spreadsheets available in the `PLANILHAS` folder.
- Select the spreadsheet to be compressed.
- Generate a ZIP archive containing the selected spreadsheet and its related documents.
- Include documents organized by service type: `CONTÁBIL`, `NÃO CONTÁBIL`, and `AUDITORES`.

## Project evolution

| Version | Description |
| --- | --- |
| **1.0** | Single script for listing files and generating reports. |
| **2.0** | Modular desktop application with document validation, file organization, and Excel spreadsheet integration. |
| **2.x** | Main interface improvements and a compression module for spreadsheets and their related documents. |

Version 1.0 and an earlier document-organization module are stored in `Versões Antigas/`. The Python files in the project root make up the current version.

## Technologies

- **Python** — application logic.
- **Tkinter / ttk** — graphical user interface.
- **Tksheet** — tabular data display.
- **OpenPyXL** — reading and updating Excel files.
- **Pillow** — support for images embedded in the spreadsheet template.
- **Python standard library** — file, directory, and ZIP compression operations.

## Project structure

```text
DocManager/
├── main.py                    # Entry point and main interface
├── listador_arquivos.py      # File listing and reports
├── atualizar_planilha.py     # Validation and spreadsheet updates
├── Versões Antigas/          # Previous versions and earlier module
├── README.md
├── README.en.md
├── requirements.txt
└── .gitignore
```

The `MODELO` folder is required for spreadsheet processing but is not distributed in the repository because it contains the original operational template. Users must provide the appropriate template file locally.

During operation, the document workflow uses the `NOVOS` folder, the `MODELO` folder, and the `PLANILHAS` folder. Processed documents are organized by service type, year, and month. For example:

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

Service-type folders are created or used as documents are processed. The `NOVOS` folder is created automatically when the validation screen is opened.

## Document naming convention

Automatic processing expects filenames in this format:

```text
dd.mm.yy description (amount) service type.ext
```

Example:

```text
11.10.26 descrição teste (100,00) contábil.pdf
```

Supported service types: **CONTÁBIL** (Accounting), **NÃO CONTÁBIL** (Non-accounting), and **AUDITORES** (Auditors). The application expects the original Portuguese labels in filenames. Validation identifies incorrect fields and highlights issues in the table. The current spreadsheet layout uses rows 9 through 38 for entries in each worksheet.

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

3. Provide a local `MODELO` folder containing **exactly one `.xlsx` file**, with worksheets for CONTÁBIL, NÃO CONTÁBIL, and AUDITORES. The original template is not distributed on GitHub. The `NOVOS` folder is created automatically when the validation screen is opened.

4. Start the application:

   ```bash
   python main.py
   ```

> **Compatibility:** the project was developed for Windows. Running it on Windows 7 requires Python and dependency versions compatible with that operating system.

## Notes

- The `PLANILHAS` folder contains generated files and does not need to be tracked by Git.
- Do not upload real documents or spreadsheets containing confidential information.
- The compression module depends on the folder structure and the documents related to the selected spreadsheet.
- The original Excel template is not included in the repository; it must be provided separately to use the spreadsheet update module.

## Author

**Giovanni Pinheiro Bonifatto**  
[GitHub](https://github.com/GIPB12) · [LinkedIn](https://www.linkedin.com/in/giovanni-bonifatto)
