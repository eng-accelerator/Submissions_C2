"""
Quick setup script for Multi-Agent AI Deep Researcher
"""

import os
import subprocess
import sys

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists('.env'):
        env_content = """# OpenRouter API Key (required)
# Get your key from: https://openrouter.ai/keys
OPEN_ROUTER_KEY=your_openrouter_key_here

# Optional: Model selection (OpenRouter format)
# Examples: openai/gpt-4-turbo-preview, anthropic/claude-3-opus
# Default: openai/gpt-4-turbo-preview

# Optional: Other API keys
# NEWS_API_KEY=your_news_api_key_here
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file. Please add your OPEN_ROUTER_KEY")
        print("   Get your key from: https://openrouter.ai/keys")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def check_venv():
    """Check if virtual environment is activated."""
    import sys
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        print("⚠️  WARNING: Virtual environment not detected!")
        print()
        print("It's recommended to use a virtual environment.")
        print("Create one with:")
        print("  Windows: python -m venv venv && venv\\Scripts\\activate")
        print("  macOS/Linux: python3 -m venv venv && source venv/bin/activate")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled. Please activate virtual environment first.")
            sys.exit(0)
    else:
        print("✅ Virtual environment detected")
    print()

def main():
    """Main setup function."""
    print("🚀 Setting up Multi-Agent AI Deep Researcher...")
    print()
    
    check_venv()
    
    create_env_file()
    print()
    
    install_dependencies()
    print()
    
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("1. Get your OpenRouter API key from: https://openrouter.ai/keys")
    print("2. Edit .env file and add your OPEN_ROUTER_KEY")
    print("3. Run: streamlit run app.py")
    print()
    print("📖 For detailed setup instructions, see VIRTUAL_ENV_SETUP.md")
    print()

if __name__ == "__main__":
    main()

