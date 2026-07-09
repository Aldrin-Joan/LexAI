import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding on standard output to prevent Windows console encoding crashes
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Fallback for Python versions that don't support stdout.reconfigure
        pass

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from llm_client import LLMClient  # noqa: E402


def test_connection():
    # Load .env from parent directory
    env_path = Path(__file__).parent.parent / ".env"
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)

    print(f"Groq API Key present: "
          f"{'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
    print(f"Model: {os.getenv('GROQ_MODEL')}")

    try:
        client = LLMClient()
        print("\nAttempting to categorize a dummy legal query with Groq...")

        result = client.categorize_case(
            case_title="State of Haryana v. Bhajan Lal",
            case_text=(
                "This is a landmark judgment on the quashing of FIRs "
                "under Section 482 of the CrPC."
            )
        )

        if result:
            print("\n[OK] Groq Connection Successful!")
            print(f"Result: {result}")
        else:
            print("\n[FAIL] Connection Failed: Received empty response.")

    except Exception as e:
        # Avoid non-ascii chars to prevent encoding errors on standard consoles
        print(f"\n[ERROR] Error during test: {str(e)}")


if __name__ == "__main__":
    test_connection()
