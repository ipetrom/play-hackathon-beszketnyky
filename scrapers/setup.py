"""
Setup script for Telecommunications Intelligence Scraper
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["reports", "logs", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists("env_template.txt"):
            import shutil
            shutil.copy("env_template.txt", ".env")
            print("✓ Created .env file from template")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("SERPER_API_KEY=your_serper_api_key_here\n")
            print("✓ Created basic .env file")
    else:
        print("✓ .env file already exists")

def check_api_key():
    """Check if Serper API key is set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key or api_key == "your_serper_api_key_here":
        print("⚠️  SERPER_API_KEY not configured in .env file")
        print("Please edit .env file and set your actual API key")
        return False
    else:
        print("✓ SERPER_API_KEY is configured in .env file")
        return True

def main():
    """Main setup function"""
    print("Setting up Telecommunications Intelligence Scraper...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check API key
    api_key_configured = check_api_key()
    
    print("=" * 50)
    if api_key_configured:
        print("✓ Setup completed successfully!")
        print("You can now run: python main_scraper.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please configure your SERPER_API_KEY before running the scraper")

if __name__ == "__main__":
    main()
