import sys
import os

# Adjust sys.path to import workspace files from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from processor import DataProcessor

def test_mistral():
    load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))
    
    # Load configuration
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_model = os.getenv("MISTRAL_MODEL")
    
    print("Testing direct Mistral connection...")
    print(f"Model:    {mistral_model}")
    print(f"API Key:  {'Provided' if mistral_api_key else 'Not Provided'}")
    
    # Initialize processor
    processor = DataProcessor(
        keywords=["tender", "project"],
        api_key=mistral_api_key,
        model=mistral_model
    )
    
    sample_text = (
        "We are pleased to announce a new project proposal yojana contract for green energy initiatives. "
        "The project will begin next month in partnership with local authorities to build sustainable grids. "
        "More details to follow."
    )
    
    summary = processor.generate_summary(sample_text)
    print("\n--- Summary Result ---")
    print(summary)
    print("----------------------")
    
    if "Error" in summary:
        print("FAIL: Summarization returned an error.")
        sys.exit(1)
    else:
        print("SUCCESS: Summary successfully retrieved!")

if __name__ == "__main__":
    test_mistral()
