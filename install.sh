#!/bin/bash
# Installation script for egile-mcp-notifier on Linux/Mac

set -e

echo "Installing egile-mcp-notifier..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.10 or later"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install package in editable mode
echo "Installing package..."
pip install -e .

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env template..."
    cat > .env << 'EOF'
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json
DEFAULT_CALENDAR_ID=primary
EOF
    echo ""
    echo ".env template created. Please update with your credentials."
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your email and Google Calendar credentials"
echo "2. Set up Google Calendar API (see README.md for instructions)"
echo "3. Run: egile-mcp-notifier"
echo ""
