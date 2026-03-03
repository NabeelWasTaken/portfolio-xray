from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize the engines globally so they only load into memory once when the server starts
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text: str) -> str:
    """
    Scans the extracted PDF text and masks sensitive information 
    (names, emails, phone numbers, etc.) before it is sent to the LLM.
    """
    # Define the specific entities we want to redact to protect the client
    entities = [
        "PERSON", 
        "EMAIL_ADDRESS", 
        "PHONE_NUMBER", 
        "CREDIT_CARD", 
        "IBAN_CODE", 
        "US_BANK_NUMBER",
        "UK_NHS" # Adding a few generic ones to catch account-like numbers
    ]
    
    # 1. Analyze the text to find the PII
    results = analyzer.analyze(text=text, entities=entities, language='en')
    
    # 2. Anonymize the text (replaces the sensitive data with <ENTITY_TYPE>)
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    
    return anonymized_result.text

# A quick way to test the file directly
if __name__ == "__main__":
    sample_text = "Client John Doe holds 500 shares of AAPL. Contact him at john.doe@wealthsimple.com or 555-0198."
    print("--- Original Text ---")
    print(sample_text)
    print("\n--- Scrubbed Text ---")
    print(scrub_pii(sample_text))