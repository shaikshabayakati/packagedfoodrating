"""
Utility functions for text processing and general helpers
"""
import re


def clean_markdown(text):
    """Clean markdown formatting from text"""
    if not text:
        return text
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # `code` -> code
    text = re.sub(r'#+\s*(.*)', r'\1', text)      # # Header -> Header
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # [link](url) -> link
    text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)  # Remove bullet points
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
    text = re.sub(r'\n{2,}', '\n\n', text)        # Multiple newlines -> double newline
    
    return text.strip()


def validate_file_upload(file):
    """Validate uploaded file"""
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension (optional)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if f'.{file_ext}' not in allowed_extensions:
        return False, f"File type .{file_ext} not supported. Please upload an image file."
    
    return True, None