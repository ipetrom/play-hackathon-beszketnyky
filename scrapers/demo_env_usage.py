"""
Demo script showing how to use .env file with the telecommunications intelligence scraper
"""

import os
from dotenv import load_dotenv

def demo_env_usage():
    """Demonstrate .env file usage"""
    print("Telecommunications Intelligence Scraper - .env Usage Demo")
    print("=" * 60)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("Please run: python setup.py")
        print("Or create .env file manually:")
        print("SERPER_API_KEY=your_actual_serper_api_key_here")
        return False
    
    print("✅ .env file found")
    
    # Check API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ SERPER_API_KEY not found in .env file")
        return False
    elif api_key == "your_serper_api_key_here":
        print("⚠️  SERPER_API_KEY is set to placeholder value")
        print("Please edit .env file and set your actual API key")
        return False
    else:
        print("✅ SERPER_API_KEY is configured")
        print(f"API Key: {api_key[:10]}...{api_key[-4:]}")  # Show partial key for security
    
    # Check other optional environment variables
    optional_vars = [
        "EMAIL_SMTP_SERVER",
        "EMAIL_SENDER", 
        "DATABASE_URL",
        "LOG_LEVEL"
    ]
    
    print("\nOptional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚪ {var}: not set (optional)")
    
    print("\n" + "=" * 60)
    print("✅ Environment configuration is ready!")
    print("You can now run: python main_scraper.py")
    
    return True

if __name__ == "__main__":
    demo_env_usage()
