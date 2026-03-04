#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOWCODE_TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
# Assuming standard workspace structure where repos are siblings
WORKSPACE_ROOT="$(dirname "$LOWCODE_TEMPLATE_ROOT")"
OPS_PLAYBOOK_DIR="$WORKSPACE_ROOT/ops-playbook"

SOURCE_DIR="$OPS_PLAYBOOK_DIR/github/issue_templates/lowcode"
DEST_DIR="$LOWCODE_TEMPLATE_ROOT/.github/ISSUE_TEMPLATE"

echo "Lowcode Template Root: $LOWCODE_TEMPLATE_ROOT"
echo "Source Directory: $SOURCE_DIR"
echo "Destination Directory: $DEST_DIR"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found at $SOURCE_DIR"
    echo "Please ensure ops-playbook is cloned as a sibling directory to lowcode-template"
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating destination directory..."
    mkdir -p "$DEST_DIR"
fi

echo "Syncing 'lowcode' issue templates..."
cp -v "$SOURCE_DIR"/*.yml "$DEST_DIR/"

echo "Sync complete!"
