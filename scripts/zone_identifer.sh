#!/bin/bash
# remove-zone-identifier.sh
# Deletes all Zone.Identifier files from current directory downward

echo "Scanning for Zone.Identifier files..."
find . -type f -name "*:Zone.Identifier" -print -delete

echo "Cleanup done."
