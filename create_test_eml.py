#!/usr/bin/env python3
"""
Test script for EML to PDF converter
Creates a sample .eml file for testing purposes
"""

import os
from pathlib import Path

def create_sample_eml():
    """Create a sample .eml file for testing"""
    sample_eml_content = '''From: sender@example.com
To: recipient@example.com
Subject: Test Email for PDF Conversion
Date: Thu, 14 Nov 2024 10:30:00 -0800
Message-ID: <test123@example.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Hello,

This is a sample email for testing the EML to PDF converter.

The email contains:
- Multiple paragraphs
- Various formatting
- Special characters: áéíóú, ñ, €, £, ¥

Best regards,
Test Sender

P.S. This is a postscript to test line breaks and formatting.
'''
    
    # Create test folder
    test_folder = Path("test_emails")
    test_folder.mkdir(exist_ok=True)
    
    # Create sample EML file
    eml_path = test_folder / "sample_email.eml"
    with open(eml_path, 'w', encoding='utf-8') as f:
        f.write(sample_eml_content)
    
    print(f"Created sample EML file: {eml_path}")
    return test_folder

def main():
    print("Creating test environment...")
    
    # Create sample EML file
    test_folder = create_sample_eml()
    
    print("\nTo test the converter, run:")
    print(f"python eml_to_pdf_converter.py {test_folder} test_pdfs")
    print("\nThis will create a 'test_pdfs' folder with the converted PDF file.")

if __name__ == "__main__":
    main()