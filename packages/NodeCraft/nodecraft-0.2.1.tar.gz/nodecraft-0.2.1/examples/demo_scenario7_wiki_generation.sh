#!/bin/bash
# Demo for Scenario 7: Codebase Wiki Generation
# Tests wiki generation from local codebase

set -e

echo "========================================"
echo "Scenario 7: Codebase Wiki Generation"
echo "========================================"
echo ""

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Please set it first:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
fi

# Output directory
OUTPUT_DIR=".ai-snapshots/wiki_output"
mkdir -p "$OUTPUT_DIR"

echo "Step 1: Generate wiki from local codebase"
echo "=========================================="
echo "Using outcomeforge project itself as example..."
echo ""

python cli.py wiki \
  --local-dir . \
  --output "$OUTPUT_DIR" \
  --language english \
  --max-abstractions 8 \
  --include-pattern "*.py" \
  --include-pattern "*.md" \
  --exclude-pattern "**/__pycache__/*" \
  --exclude-pattern "**/tests/*" \
  --exclude-pattern "**/.cloned_repos/*" \
  --model "claude-3-haiku-20240307"

echo ""
echo "========================================"
echo "Results"
echo "========================================"
echo ""

# Find the generated wiki
WIKI_FILE=$(find "$OUTPUT_DIR" -name "TUTORIAL.md" -type f | head -1)

if [ -f "$WIKI_FILE" ]; then
    WIKI_DIR=$(dirname "$WIKI_FILE")
    PROJECT_NAME=$(basename "$WIKI_DIR")

    echo "Wiki generated successfully!"
    echo "  Project: $PROJECT_NAME"
    echo "  Location: $WIKI_DIR"
    echo "  Main file: $WIKI_FILE"
    echo ""

    # Show file size and line count
    SIZE=$(du -h "$WIKI_FILE" | cut -f1)
    LINES=$(wc -l < "$WIKI_FILE")
    echo "  Size: $SIZE"
    echo "  Lines: $LINES"
    echo ""

    # Show first 50 lines
    echo "Preview (first 50 lines):"
    echo "----------------------------------------"
    head -50 "$WIKI_FILE"
    echo "----------------------------------------"
    echo ""

    # List all files in output directory
    echo "Generated files:"
    ls -lh "$WIKI_DIR"
else
    echo "Error: Wiki generation failed or TUTORIAL.md not found"
    exit 1
fi

echo ""
echo "========================================"
echo "Optional: Multi-file mode example"
echo "========================================"
echo ""
echo "To generate multi-file output (index.md + chapters):"
echo "  python cli.py wiki --local-dir . --multi-file --output ./wiki_multifile"
echo ""
echo "To generate Chinese wiki:"
echo "  python cli.py wiki --local-dir . --language chinese"
echo ""
echo "To process GitHub repository:"
echo "  python cli.py wiki --repo https://github.com/The-Pocket/PocketFlow-Rust"
echo ""
echo "Demo completed successfully!"
