#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOILERPLATE_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Labs Boilerplate — New Lab"
echo ""

echo "Available templates:"
ls "$BOILERPLATE_ROOT/templates/"
echo ""

read -p "Template: " TEMPLATE
read -p "Lab name (e.g. lab-02-api-testing): " LAB_NAME
read -p "Output directory [../]: " OUTPUT_DIR
OUTPUT_DIR="${OUTPUT_DIR:-../}"

SOURCE="$BOILERPLATE_ROOT/templates/$TEMPLATE"
TARGET="$OUTPUT_DIR/$LAB_NAME"

if [ ! -d "$SOURCE" ]; then
  echo "Template '$TEMPLATE' not found"
  exit 1
fi

cp -r "$SOURCE" "$TARGET"
cd "$TARGET"
git init
git add .
git commit -m "feat: initial lab structure from $TEMPLATE template"

echo ""
echo "Lab created at $TARGET"
echo ""
echo "Next steps:"
echo "  1. Edit docs/instructions.md      <- define the lab exercise"
echo "  2. Edit .grader/checks/           <- write your grading criteria"
echo "  3. Edit src/ if needed            <- add starter code (optional)"
echo "  4. Push to GitHub as a new repo"