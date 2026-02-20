#!/bin/bash
# Run the surveillance system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default config
CONFIG="${1:-config/config.yaml}"

echo "Starting surveillance system..."
echo "Config: $CONFIG"
echo ""

python3 src/surveillance_node.py -c "$CONFIG"