#!/usr/bin/env python3
"""
EML to PDF Converter

This script converts .eml email files to .pdf format.
It preserves email headers, body content, and lists any attachments.

Usage:
    python eml_to_pdf_converter.py input_folder output_folder

Requirements:
    - reportlab
    - email (built-in)
    - os, sys (built-in)
"""

import os
import sys
import email
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
import html
import re

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    print("Error: reportlab is required. Install it with: pip install reportlab")
    sys.exit(1)


class EMLToPDFConverter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for better formatting"""
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=6,
            backColor=colors.lightgrey
        )
        
        # Email header style
        self.email_header_style = ParagraphStyle(
            'EmailHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            spaceAfter=3,
            leftIndent=10
        )
        
        # Email content style
        self.email_content_style = ParagraphStyle(
            'EmailContent',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=10,
            rightIndent=10
        )
        
        # Attachment style
        self.attachment_style = ParagraphStyle(
            'Attachment',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=colors.darkgreen,
            leftIndent=20
        )

    def clean_text(self, text):
        """Clean and prepare text for PDF rendering"""
        if not text:
            return ""
        
        # Handle encoding issues
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8', errors='replace')
            except:
                text = str(text)
        
        # Escape HTML entities and clean up
        text = html.escape(str(text))
        
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace line breaks with HTML breaks for proper PDF rendering
        text = text.replace('\n', '<br/>')
        
        return text.strip()

    def parse_eml_file(self, eml_path):
        """Parse an EML file and extract email data"""
        try:
            with open(eml_path, 'rb') as f:
                msg = email.message_from_bytes(f.read())
            
            # Extract headers
            email_data = {
                'subject': self.clean_text(msg.get('Subject', 'No Subject')),
                'from': self.clean_text(msg.get('From', 'Unknown Sender')),
                'to': self.clean_text(msg.get('To', 'Unknown Recipient')),
                'cc': self.clean_text(msg.get('Cc', '')),
                'bcc': self.clean_text(msg.get('Bcc', '')),
                'date': self.clean_text(msg.get('Date', '')),
                'message_id': self.clean_text(msg.get('Message-ID', '')),
                'body': '',
                'attachments': []
            }
            
            # Parse date if available
            if email_data['date']:
                try:
                    parsed_date = email.utils.parsedate_to_datetime(msg.get('Date'))
                    email_data['date'] = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass  # Keep original date string if parsing fails
            
            # Extract body and attachments
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    # Handle text content
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        try:
                            body = part.get_payload(decode=True)
                            if body:
                                email_data['body'] += self.clean_text(body)
                        except:
                            pass
                    
                    elif content_type == 'text/html' and 'attachment' not in content_disposition and not email_data['body']:
                        try:
                            html_body = part.get_payload(decode=True)
                            if html_body:
                                # Simple HTML to text conversion
                                html_text = re.sub(r'<[^>]+>', '', html_body.decode('utf-8', errors='replace'))
                                email_data['body'] = self.clean_text(html_text)
                        except:
                            pass
                    
                    # Handle attachments
                    elif 'attachment' in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            email_data['attachments'].append({
                                'filename': self.clean_text(filename),
                                'content_type': content_type,
                                'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
                            })
            else:
                # Single part message
                try:
                    body = msg.get_payload(decode=True)
                    if body:
                        email_data['body'] = self.clean_text(body)
                except:
                    email_data['body'] = self.clean_text(str(msg.get_payload()))
            
            return email_data
            
        except Exception as e:
            print(f"Error parsing {eml_path}: {str(e)}")
            return None

    def create_pdf(self, email_data, output_path):
        """Create a PDF from email data"""
        try:
            # Convert Path object to string for reportlab compatibility
            output_path_str = str(output_path)
            doc = SimpleDocTemplate(output_path_str, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            story.append(Paragraph("Email Message", self.header_style))
            story.append(Spacer(1, 12))
            
            # Email headers
            headers = [
                ('Subject:', email_data['subject']),
                ('From:', email_data['from']),
                ('To:', email_data['to']),
                ('Date:', email_data['date'])
            ]
            
            if email_data['cc']:
                headers.append(('CC:', email_data['cc']))
            if email_data['bcc']:
                headers.append(('BCC:', email_data['bcc']))
            if email_data['message_id']:
                headers.append(('Message ID:', email_data['message_id']))
            
            # Create table for headers
            header_data = []
            for label, value in headers:
                if value:
                    header_data.append([Paragraph(f"<b>{label}</b>", self.email_header_style),
                                      Paragraph(value, self.email_content_style)])
            
            if header_data:
                header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
                ]))
                story.append(header_table)
                story.append(Spacer(1, 20))
            
            # Email body
            if email_data['body']:
                story.append(Paragraph("<b>Message Body:</b>", self.header_style))
                story.append(Spacer(1, 6))
                
                # Split long text into paragraphs
                body_paragraphs = email_data['body'].split('<br/><br/>')
                for para in body_paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, self.email_content_style))
                        story.append(Spacer(1, 6))
            
            # Attachments
            if email_data['attachments']:
                story.append(Spacer(1, 20))
                story.append(Paragraph("<b>Attachments:</b>", self.header_style))
                story.append(Spacer(1, 6))
                
                for attachment in email_data['attachments']:
                    size_str = f" ({attachment['size']} bytes)" if attachment['size'] > 0 else ""
                    att_text = f"• {attachment['filename']} ({attachment['content_type']}){size_str}"
                    story.append(Paragraph(att_text, self.attachment_style))
                    story.append(Spacer(1, 3))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error creating PDF {output_path}: {str(e)}")
            return False

    def convert_folder(self, input_folder, output_folder):
        """Convert all EML files in input folder to PDF files in output folder"""
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        
        if not input_path.exists():
            print(f"Error: Input folder '{input_folder}' does not exist.")
            return False
        
        # Create output folder if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all EML files
        eml_files = list(input_path.glob('*.eml'))
        if not eml_files:
            print(f"No .eml files found in '{input_folder}'")
            return False
        
        print(f"Found {len(eml_files)} .eml files to convert...")
        
        converted = 0
        failed = 0
        
        for eml_file in eml_files:
            print(f"Processing: {eml_file.name}")
            
            # Parse EML file
            email_data = self.parse_eml_file(eml_file)
            if not email_data:
                print(f"  Failed to parse {eml_file.name}")
                failed += 1
                continue
            
            # Create PDF filename
            pdf_filename = eml_file.stem + '.pdf'
            pdf_path = output_path / pdf_filename
            
            # Convert to PDF
            if self.create_pdf(email_data, pdf_path):
                print(f"  ✓ Created: {pdf_filename}")
                converted += 1
            else:
                print(f"  ✗ Failed to create PDF for {eml_file.name}")
                failed += 1
        
        print(f"\nConversion complete!")
        print(f"Successfully converted: {converted} files")
        print(f"Failed: {failed} files")
        
        return converted > 0


def main():
    if len(sys.argv) != 3:
        print("Usage: python eml_to_pdf_converter.py <input_folder> <output_folder>")
        print("")
        print("Example:")
        print("  python eml_to_pdf_converter.py ./emails ./pdfs")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    converter = EMLToPDFConverter()
    success = converter.convert_folder(input_folder, output_folder)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()