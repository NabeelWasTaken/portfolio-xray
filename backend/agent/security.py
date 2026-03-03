import re

def scrub_pii(text: str) -> str:
    
    
    if not text:
        return text
        
    # Scrub Emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL REDACTED]', text)
    
    # Scrub Phone Numbers
    text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE REDACTED]', text)
    
    # Scrub standard 9-digit IDs (like SIN/SSN)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{3}\b', '[ID REDACTED]', text)
    
    return text