#!/bin/bash

# Gemini Startup Script
# ---------------------
# Purpose: To provide session continuity by displaying the summary
# from the previous session. This ensures I am up-to-date with the
# latest project status and user objectives.

echo "========================================================"
echo "GEMINI: Reading previous session summary..."
echo "========================================================"

# Display the summary file. If it doesn't exist, say so.
if [ -f "/home/mtez/operation_help_maxwell/session_summary.md" ]; then
    cat "/home/mtez/operation_help_maxwell/session_summary.md"
else
    echo "No session_summary.md file found. Starting a new session."
fi

echo "========================================================"
echo "GEMINI: Startup context loaded."
echo "========================================================"
