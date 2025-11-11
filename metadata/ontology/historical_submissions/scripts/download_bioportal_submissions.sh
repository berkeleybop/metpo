#!/bin/bash

# Download actual METPO submissions from BiPortal
# Submissions 2-10 have OWL files (submission 1 doesn't)

API_KEY="8b5b7825-538d-40e0-9e9e-5ab9274a9aeb"
BASE_URL="https://data.bioontology.org/ontologies/METPO/submissions"

mkdir -p downloads/bioportal_submissions

for submission in {2..10}; do
    echo "Downloading submission $submission..."
    curl -L -s "${BASE_URL}/${submission}/download?apikey=${API_KEY}" \
         -o "downloads/bioportal_submissions/metpo_submission_${submission}.owl"

    # Check if download was successful
    if [ $? -eq 0 ] && [ -s "downloads/bioportal_submissions/metpo_submission_${submission}.owl" ]; then
        echo "✓ Successfully downloaded submission $submission"
        # Extract version info
        grep -m1 "versionInfo" "downloads/bioportal_submissions/metpo_submission_${submission}.owl" || echo "No version info found"
    else
        echo "✗ Failed to download submission $submission"
    fi

    sleep 1  # Be nice to the API
done

echo "Download complete. Files saved in downloads/bioportal_submissions/"