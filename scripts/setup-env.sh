#!/bin/bash
set -e

# This script helps set up the environment for the first time

echo "========================================="
echo "  Spokojne Decyzje - Environment Setup"
echo "========================================="
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  Warning: .env file already exists!"
    echo ""
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Existing .env file preserved."
        exit 0
    fi
fi

# Copy from example
if [ ! -f .env.example ]; then
    echo "❌ Error: .env.example file not found!"
    echo "Please ensure you're running this script from the project root directory."
    exit 1
fi

echo "Creating .env file from .env.example..."
cp .env.example .env

echo ""
echo "✓ .env file created!"
echo ""
echo "========================================="
echo "  Important: Update Your Credentials"
echo "========================================="
echo ""
echo "Please edit the .env file and update these values:"
echo ""
echo "  1. POSTGRES_PASSWORD - Change from default password"
echo "  2. SECRET_KEY - Set a strong random secret key (min 32 chars)"
echo "  3. OPENAI_API_KEY - Add your OpenAI API key"
echo ""
echo "You can edit the file now with:"
echo "  nano .env    # or vim .env, code .env, etc."
echo ""

read -p "Do you want to edit .env now? (Y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # Try different editors
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v vi &> /dev/null; then
        vi .env
    elif command -v code &> /dev/null; then
        code .env
    else
        echo "No suitable editor found. Please edit .env manually."
    fi
fi

echo ""
echo "========================================="
echo "  Next Steps"
echo "========================================="
echo ""
echo "1. Ensure Docker is running"
echo "2. Start the development environment:"
echo "     docker compose --profile dev up --build"
echo ""
echo "3. Access the application:"
echo "     Frontend: http://localhost:3000"
echo "     API: http://localhost:8000"
echo "     API Docs: http://localhost:8000/docs"
echo ""
echo "For troubleshooting, see: docs/POSTGRES-TROUBLESHOOTING.md"
echo ""
