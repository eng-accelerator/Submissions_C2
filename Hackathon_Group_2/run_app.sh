#!/bin/bash
# Script to run Streamlit app with the correct virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source myenv/bin/activate

# Check if JIRA is installed
echo "Checking environment..."
python check_environment.py

echo ""
echo "Starting Streamlit app..."
echo "Make sure you're using Python from: $(which python)"
echo ""

# Run Streamlit
streamlit run app.py

