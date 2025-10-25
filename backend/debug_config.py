"""
Debug script to check database configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.config import settings

print("=== Database Configuration Debug ===")
print(f"Database URL: {settings.database_url}")
print(f"Debug mode: {settings.debug}")
print(f"Environment variables:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
print(f"  Current working directory: {os.getcwd()}")
print(f"  .env file exists: {os.path.exists('.env')}")

