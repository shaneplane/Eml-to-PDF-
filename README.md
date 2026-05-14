# EML to PDF Converter

A Python script that converts .eml email files to .pdf format while preserving email headers, body content, and attachment information.

## Features

- Converts .eml files to well-formatted PDF documents
- Preserves email headers (Subject, From, To, Date, CC, BCC, Message-ID)
- Handles both plain text and HTML email bodies
- Lists attachment information (filename, type, size)
- Processes entire folders of .eml files
- Clean, professional PDF formatting with proper styling

## Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line
```bash
python eml_to_pdf_converter.py <input_folder> <output_folder>
```

### Example
```bash
python eml_to_pdf_converter.py ./emails ./pdfs
```

This will:
- Read all .eml files from the `./emails` folder
- Convert each one to a PDF file
- Save the PDFs in the `./pdfs` folder (created automatically if it doesn't exist)
- Each PDF will have the same name as the original .eml file but with a .pdf extension

## Sample Usage

1. Create a folder with your .eml files:
   ```
   emails/
   ├── important_email.eml
   ├── meeting_notes.eml
   └── newsletter.eml
   ```

2. Run the converter:
   ```bash
   python eml_to_pdf_converter.py emails pdfs
   ```

3. Get your PDF files:
   ```
   pdfs/
   ├── important_email.pdf
   ├── meeting_notes.pdf
   └── newsletter.pdf
   ```

## Output Format

Each PDF includes:
- **Email Headers**: Subject, From, To, Date, CC, BCC, Message-ID (if present)
- **Message Body**: Full email content with proper formatting
- **Attachments**: List of attachment files with their types and sizes

## Error Handling

The script handles various edge cases:
- Corrupted or malformed .eml files
- Different text encodings
- Missing email headers
- HTML content conversion to text
- Large email bodies

## Requirements

- Python 3.6+
- reportlab library for PDF generation

## Troubleshooting

If you encounter encoding issues with certain .eml files, the script will attempt to handle them gracefully and continue processing other files.

For any files that fail to convert, error messages will be displayed indicating which files couldn't be processed.