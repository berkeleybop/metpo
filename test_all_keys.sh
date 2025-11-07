#!/bin/bash

# Find all files starting with .cborg-key in the home directory
for key_file in ~/.cborg-key.*; do
    # Skip the main .cborg-key file to avoid testing it twice
    if [ "$key_file" == "$HOME/.cborg-key" ]; then
        continue
    fi

    echo "===================================================="
    echo "Testing key from: $key_file"
    echo "===================================================="

    # Read the key from the file
    api_key=$(cat "$key_file")

    echo "--- /user/info ---"
    # Make the curl request to /user/info and pipe to jq
    curl -s -X GET https://api.cborg.lbl.gov/user/info \
        -H "Authorization: Bearer $api_key" | jq .

    echo ""
    echo "--- /key/info ---"
    # Make the curl request to /key/info and pipe to jq
    curl -s -X GET https://api.cborg.lbl.gov/key/info \
        -H "Authorization: Bearer $api_key" | jq .

    echo ""
done
