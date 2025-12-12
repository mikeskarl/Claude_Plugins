#!/bin/bash

echo "=== Quiz Maker Plugin Installation ==="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPTS_PATH="$SCRIPT_DIR/skills/quiz-maker/scripts"

echo "Plugin directory: $SCRIPT_DIR"
echo "Scripts directory: $SCRIPTS_PATH"
echo ""

# Make all Python scripts executable
echo "Making Python scripts executable..."
chmod +x "$SCRIPTS_PATH"/*.py
echo "✓ Scripts are now executable"
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found $PYTHON_VERSION"
else
    echo "ERROR: python3 not found. Please install Python 3.7 or later."
    exit 1
fi
echo ""

# Run initial configuration
echo "=== Initial Configuration ==="
echo ""
echo "The plugin needs to know where to save quiz files."
echo ""

python3 "$SCRIPTS_PATH/config.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Installation Complete ==="
    echo ""
    echo "The quiz-maker plugin is ready to use!"
    echo ""
    echo "Usage:"
    echo "  In Claude Code, use the skill:"
    echo "  • /quiz-maker"
    echo "  • Or: 'Use the quiz-maker skill to create a quiz'"
    echo ""
    echo "Commands:"
    echo "  • Reconfigure: python3 $SCRIPTS_PATH/config.py --reconfigure"
    echo "  • Check config: python3 $SCRIPTS_PATH/config.py --check"
    echo ""
    echo "Documentation:"
    echo "  • README: $SCRIPT_DIR/README.md"
    echo "  • Skill docs: $SCRIPT_DIR/skills/quiz-maker/skill.md"
    echo ""
else
    echo ""
    echo "ERROR: Configuration failed"
    echo "Please run: python3 $SCRIPTS_PATH/config.py"
    exit 1
fi
