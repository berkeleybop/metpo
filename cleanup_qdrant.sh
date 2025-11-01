#!/bin/bash
# Cleanup script to identify and remove Qdrant references from PR #275
# Run this script after checking out the enhance-non-ols-ontology-pipeline branch

set -e

BRANCH="enhance-non-ols-ontology-pipeline"
CURRENT_BRANCH=$(git branch --show-current)

echo "=== Qdrant Cleanup Script for PR #275 ==="
echo ""

# Check if we're on the right branch
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "WARNING: You are on branch '$CURRENT_BRANCH'"
    echo "This script is designed to run on '$BRANCH'"
    echo ""
    read -p "Do you want to switch to $BRANCH now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Switching to $BRANCH..."
        git checkout "$BRANCH"
    else
        echo "Aborting. Please run this script on the correct branch."
        exit 1
    fi
fi

echo "Step 1: Identifying Qdrant-related files..."
echo "==========================================="
echo ""

# Find files with 'qdrant' in their name
echo "Files with 'qdrant' in filename:"
find . -type f -iname "*qdrant*" -not -path "./.git/*" | while read file; do
    echo "  - $file"
done
echo ""

# Find files containing qdrant references
echo "Files containing 'qdrant' references:"
grep -r -l -i "qdrant" --exclude-dir=.git --exclude="*.log" --exclude="cleanup_qdrant.sh" . | while read file; do
    count=$(grep -c -i "qdrant" "$file" || true)
    echo "  - $file ($count occurrences)"
done
echo ""

echo "Step 2: Detailed Qdrant references by file..."
echo "=============================================="
echo ""

grep -r -n -i "qdrant" --exclude-dir=.git --exclude="*.log" --exclude="cleanup_qdrant.sh" . || echo "No references found"
echo ""

echo "Step 3: Files to delete..."
echo "==========================="
echo ""

FILES_TO_DELETE=(
    "notebooks/migrate_to_qdrant_resilient.py"
    "notebooks/query_metpo_terms_qdrant.py"
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  [EXISTS] $file"
    else
        echo "  [NOT FOUND] $file"
    fi
done
echo ""

echo "Step 4: Checking pyproject.toml for qdrant dependencies..."
echo "==========================================================="
echo ""

if [ -f "pyproject.toml" ]; then
    if grep -i "qdrant" pyproject.toml > /dev/null 2>&1; then
        echo "Found qdrant in pyproject.toml:"
        grep -n -i "qdrant" pyproject.toml
        echo ""
    else
        echo "No qdrant dependencies found in pyproject.toml"
    fi
else
    echo "pyproject.toml not found"
fi
echo ""

echo "Step 5: Ready to clean up?"
echo "=========================="
echo ""
echo "This script will:"
echo "1. Delete Qdrant-specific files"
echo "2. Remove qdrant-client from pyproject.toml (if present)"
echo "3. Show you files that need manual review for qdrant references"
echo ""
read -p "Proceed with cleanup? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup aborted. No changes made."
    exit 0
fi

echo ""
echo "Executing cleanup..."
echo "===================="
echo ""

# Delete Qdrant files
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✓ Deleted: $file"
    fi
done

# Remove from git if they were tracked
for file in "${FILES_TO_DELETE[@]}"; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        git rm "$file" 2>/dev/null || true
        echo "  ✓ Removed from git: $file"
    fi
done

echo ""
echo "Step 6: Files requiring manual review..."
echo "=========================================="
echo ""
echo "Please manually review and edit these files to remove qdrant references:"
echo ""

# Find files that still contain qdrant (excluding the ones we just deleted)
grep -r -l -i "qdrant" --exclude-dir=.git --exclude="*.log" --exclude="cleanup_qdrant.sh" . 2>/dev/null | while read file; do
    # Skip files we already deleted
    skip=0
    for deleted in "${FILES_TO_DELETE[@]}"; do
        if [ "$file" = "./$deleted" ]; then
            skip=1
            break
        fi
    done

    if [ $skip -eq 0 ]; then
        echo "  - $file"
        echo "    Context:"
        grep -n -i "qdrant" "$file" | head -5 | sed 's/^/      /'
        echo ""
    fi
done

echo ""
echo "Cleanup complete!"
echo "================="
echo ""
echo "Next steps:"
echo "1. Review the files listed above and remove qdrant references"
echo "2. If pyproject.toml was modified, run: uv sync"
echo "3. Test that ChromaDB functionality still works"
echo "4. Commit the changes: git add -A && git commit -m 'Remove Qdrant dependencies, keep ChromaDB only'"
echo ""
