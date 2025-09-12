#!/bin/bash
# zone_identifier_cleanup.sh
# Removes all Windows Zone.Identifier ADS junk files in current tree

echo "🧹 Cleaning Zone.Identifier files under: $(pwd)"
count=$(find . -type f -name "*:Zone.Identifier" | wc -l)

if [ "$count" -eq 0 ]; then
    echo "No Zone.Identifier files found."
else
    find . -type f -name "*:Zone.Identifier" -print -delete
    echo "Removed $count Zone.Identifier files."
fi
