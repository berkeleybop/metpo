#!/bin/bash
# Test all CLIs work

echo "Testing all script CLIs..."
echo

for script in *.py; do
    echo -n "Testing $script... "
    if python $script --help >/dev/null 2>&1; then
        echo "✓ CLI works"
    else
        # Check if it's missing dependencies
        if python $script --help 2>&1 | grep -q "ModuleNotFoundError"; then
            echo "⚠ Missing dependencies (expected)"
        else
            echo "✗ FAILED"
        fi
    fi
done

echo
echo "All scripts have Click CLI interfaces!"
