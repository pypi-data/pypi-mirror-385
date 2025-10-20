#!/bin/bash
# Quick start script for Nuha development

set -e

echo "🤖 Nuha Quick Start"
echo "===================="
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync
echo ""

# Run setup
echo "⚙️  Running setup..."
uv run nuha setup
echo ""

echo "✅ Setup complete!"
echo ""
echo "Try these commands:"
echo "  uv run nuha --help         # Show help"
echo "  uv run nuha explain --auto # Explain last command"
echo "  make test                  # Run tests"
echo "  make format                # Format code"
echo ""
