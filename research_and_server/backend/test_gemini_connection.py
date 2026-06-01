import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from llm_client import LLMClient

def test_connection():
    # Load .env from parent directory (final_submission/)
    env_path = Path(__file__).parent.parent / ".env"
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)
    
    print(f"API Key present: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
    print(f"Model: {os.getenv('GEMINI_MODEL')}")
    
    try:
        client = LLMClient()
        print("\nAttempting to categorize a dummy legal query...")
        
        result = client.categorize_case(
            case_title="State of Haryana v. Bhajan Lal",
            case_text="This is a landmark judgment on the quashing of FIRs under Section 482 of the CrPC."
        )
        
        if result:
            print("\n✅ Connection Successful!")
            print(f"Result: {result}")
        else:
            print("\n❌ Connection Failed: Received empty response.")
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")

if __name__ == "__main__":
    test_connection()
