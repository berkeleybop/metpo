#!/bin/bash

echo "===================================================="
echo "Testing key from: /Users/MAM/.cborg-key.luke"
echo "===================================================="

# Read the key from the file
api_key=$(cat "/Users/MAM/.cborg-key.luke")

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
