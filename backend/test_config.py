#!/usr/bin/env python3
"""
Test script for Gemini API configuration
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_config():
    """Test if Gemini API is properly configured"""
    print("🔍 Testing Gemini API configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Please add your API key to the .env file")
        return False
    
    if api_key == "your_api_key_here":
        print("❌ Please update your .env file with your actual API key")
        print("   Get your API key from: https://aistudio.google.com/apikey")
        return False
    
    print("✅ API key found in environment")
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Gemini model initialized successfully")
        
        # Test a simple request
        response = model.generate_content("Hello, this is a test message.")
        if response.text:
            print("✅ Gemini API is working correctly")
            print(f"   Test response: {response.text[:50]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring Gemini: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_config()
    if success:
        print("\n🎉 Configuration test passed! You can now run the main application.")
    else:
        print("\n❌ Configuration test failed. Please check your setup.")
        exit(1)
