#!/bin/bash

#todo test the correctness of script. Currently does
#not check the $VIRTUAL_ENV correctly.

SCRIPT_NAME="vault.py"
SCRIPT_PATH=$(realpath "$SCRIPT_NAME")
BINARY_NAME="${SCRIPT_NAME%.py}"
INSTALL_DIR="$HOME/.local/bin"
BINARY_PATH="$INSTALL_DIR/$BINARY_NAME"
TEMP_FILE=$(mktemp)

# Determine python interpreter path
if [ -n "$VIRTUAL_ENV" ]; then
  PYTHON_PATH="$VIRTUAL_ENV/bin/python"
else
  PYTHON_PATH=$(which python3)
  if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
  fi
fi

if [ -z "$PYTHON_PATH" ]; then
  echo "Error: Python interpreter not found."
  exit 1
fi

# Check if binary already exists
if [ -f "$BINARY_PATH" ]; then
  echo "Error: Binary already exists in $INSTALL_DIR."
  exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Remove existing shebang and create temp file
sed '1{/^#!/d}' "$SCRIPT_PATH" > "$TEMP_FILE"

# Create shebang and binary
echo "#!${PYTHON_PATH}" > "$BINARY_PATH"
cat "$TEMP_FILE" >> "$BINARY_PATH"
chmod +x "$BINARY_PATH"

# Clean up temp file
rm "$TEMP_FILE"

# Update PATH if needed
if ! grep -q "$INSTALL_DIR" ~/.bashrc; then
  echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
  source ~/.bashrc
fi

echo "$SCRIPT_NAME installed to $INSTALL_DIR and added to PATH."
echo "It should now be runnable from your terminal as $BINARY_NAME"
