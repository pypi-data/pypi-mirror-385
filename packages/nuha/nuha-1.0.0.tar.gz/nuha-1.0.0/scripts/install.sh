#!/bin/bash
# Nuha installation script for Unix-like systems

set -e

echo "🤖 Installing Nuha - AI-Powered Terminal Assistant"
echo ""

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

# Determine binary name
if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        BINARY_NAME="nuha-macos-arm64"
    else
        BINARY_NAME="nuha-macos-x64"
    fi
elif [ "$OS" = "Linux" ]; then
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        BINARY_NAME="nuha-linux-arm64"
    else
        BINARY_NAME="nuha-linux-x64"
    fi
else
    echo "Unsupported operating system: $OS"
    exit 1
fi

# Download URL
GITHUB_REPO="nuha-ai/nuha"
DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/latest/download/${BINARY_NAME}"

echo "Detected: $OS $ARCH"
echo "Downloading: $BINARY_NAME"
echo ""

# Create temporary directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Download binary
if command -v curl > /dev/null 2>&1; then
    curl -L "$DOWNLOAD_URL" -o nuha
elif command -v wget > /dev/null 2>&1; then
    wget "$DOWNLOAD_URL" -O nuha
else
    echo "Error: curl or wget is required"
    exit 1
fi

# Make executable
chmod +x nuha

# Install to /usr/local/bin (may require sudo)
INSTALL_DIR="/usr/local/bin"

if [ -w "$INSTALL_DIR" ]; then
    mv nuha "$INSTALL_DIR/"
    echo "✓ Installed to $INSTALL_DIR/nuha"
else
    echo "Installing to $INSTALL_DIR requires sudo permissions"
    sudo mv nuha "$INSTALL_DIR/"
    echo "✓ Installed to $INSTALL_DIR/nuha"
fi

# Clean up
cd -
rm -rf "$TMP_DIR"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Get started with:"
echo "  nuha setup     # Configure your API keys"
echo "  nuha --help    # See available commands"
echo ""
