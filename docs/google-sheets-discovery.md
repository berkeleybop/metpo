# Google Sheets Discovery and Download

This document describes how to discover and download all tabs from the METPO Google Sheets workbook.

## Overview

The METPO project uses a Google Sheets workbook to manage ontology data across multiple worksheets. We need to periodically download all sheets as TSV files for processing. The challenge is automatically discovering all sheet names and their internal IDs (gids) without complex authentication.

## Solution: Google Apps Script

Google Apps Script provides direct access to spreadsheet metadata without requiring API keys or OAuth setup. It runs directly within the Google Sheets environment.

### Step 1: Access Apps Script

1. Open the METPO Google Sheets workbook: 
   `https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit`

2. Navigate to **Extensions → Apps Script**

3. This opens the Google Apps Script editor in a new tab

### Step 2: Discovery Script

Replace the default `myFunction()` with this discovery script:

```javascript
function listAllSheets() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = spreadsheet.getSheets();
  
  console.log('# Sheet discovery for spreadsheet: ' + spreadsheet.getId());
  console.log('# Total sheets found: ' + sheets.length);
  console.log('');
  
  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    var name = sheet.getName();
    var gid = sheet.getSheetId();
    var safeName = name.toLowerCase().replace(/[^a-z0-9_]/g, '_');
    
    console.log('# ' + name);
    console.log('GID_' + safeName.toUpperCase() + ' = ' + gid);
    console.log('downloads/sheets/' + safeName + '.tsv:');
    console.log('\tcurl -L -s \'$(BASE_URL)?exportFormat=tsv&gid=' + gid + '\' > $@');
    console.log('');
  }
}
```

### Step 3: Run and Extract Output

1. **Save** the script (Ctrl/Cmd + S)
2. **Run** the `listAllSheets` function (click the play button)
3. **View output**: Go to **View → Logs** (or **Ctrl/Cmd + Enter**)
4. **Copy** the Makefile-formatted output from the logs

### Step 4: Update Makefile

Copy the generated variables and targets from the Apps Script logs into the main `Makefile`:

```makefile
# All sheet gids discovered via Google Apps Script (9 total sheets)
GID_MINIMAL_CLASSES = 355012485
GID_PROPERTIES = 2094089867
GID_BACTOTRAITS = 1192666692
GID_MORE_SYNONYMS = 907926993
GID_MORE_CLASSES = 1427185859
GID_METABOLIC_AND_RESPIRATORY = 499077032
GID_TROPHIC_MAPPING_BACDIVE__TBDELETED = 44169923
GID_ATTIC_CLASSES = 1347388120
GID_ATTIC_PROPERTIES = 565614186
```

## Current Sheets (as of 2025-09-24)

The METPO workbook currently contains 9 worksheets:

| Sheet Name | GID | Purpose | Size |
|------------|-----|---------|------|
| minimal classes | 355012485 | Core ontology classes | 200 rows |
| properties | 2094089867 | Object/data properties | 84 rows |
| bactotraits | 1192666692 | Bacterial trait terms | 68 rows |
| more synonyms | 907926993 | Additional synonyms | 1 row |
| more classes | 1427185859 | Extended class definitions | 487 rows |
| metabolic_and_respiratory | 499077032 | Metabolic process terms | 369 rows |
| trophic_mapping_bacdive__tbdeleted | 44169923 | BacDive mapping data | 32 rows |
| attic classes | 1347388120 | Deprecated/archived classes | 56 rows |
| attic properties | 565614186 | Deprecated/archived properties | 8 rows |

## Download Commands

After updating the Makefile with discovered sheet information:

```bash
# Download all sheets
make download-all-sheets

# Download individual sheets
make downloads/sheets/minimal_classes.tsv
make downloads/sheets/properties.tsv
# ... etc

# Clean downloaded sheets
make clean-sheets
```

## Maintenance

When new sheets are added to the workbook or existing sheets are renamed:

1. Re-run the Google Apps Script `listAllSheets()` function
2. Copy the updated output to the Makefile
3. Update the `download-all-sheets` target dependency list
4. Test with `make download-all-sheets`

## Why This Approach?

**Advantages:**
- ✅ No authentication required
- ✅ Direct access to all sheet metadata  
- ✅ Generates Makefile-ready output
- ✅ Works with any Google Sheets document
- ✅ No external dependencies

**Alternatives considered:**
- Google Sheets API: Requires OAuth/API keys
- HTML scraping: Fragile, complex parsing
- Manual extraction: Not scalable, error-prone

## Command Line Alternatives

If you prefer to avoid the browser-based Apps Script editor, here are several command-line approaches:

### Option 1: `clasp` (Google's Apps Script CLI)

**Setup:**
```bash
# Install clasp globally
npm install -g @google/clasp

# Login (opens browser once for authentication)
clasp login
```

**Create and run script:**
```bash
# Create new Apps Script project
clasp create --type standalone --title "METPO Sheet Discovery"

# Write the discovery script
cat > Code.js << 'EOF'
function listAllSheets() {
  // Note: Use openById() instead of getActiveSpreadsheet() for CLI
  var spreadsheet = SpreadsheetApp.openById('1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU');
  var sheets = spreadsheet.getSheets();
  
  console.log('# Sheet discovery for spreadsheet: ' + spreadsheet.getId());
  console.log('# Total sheets found: ' + sheets.length);
  console.log('');
  
  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    var name = sheet.getName();
    var gid = sheet.getSheetId();
    var safeName = name.toLowerCase().replace(/[^a-z0-9_]/g, '_');
    
    console.log('# ' + name);
    console.log('GID_' + safeName.toUpperCase() + ' = ' + gid);
    console.log('downloads/sheets/' + safeName + '.tsv:');
    console.log('\tcurl -L -s \'$(BASE_URL)?exportFormat=tsv&gid=' + gid + '\' > $@');
    console.log('');
  }
}
EOF

# Deploy and run
clasp push
clasp run listAllSheets
```

### Option 2: Google Sheets API (Python)

**Enhanced discovery script using Sheets API:**
```python
# Install dependencies
pip install google-api-python-client google-auth-oauthlib google-auth

# Create enhanced_discover_sheets.py
```

```python
#!/usr/bin/env python3
"""
Enhanced Google Sheets discovery using the Sheets API.
Requires authentication setup but works entirely from command line.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU'

def authenticate():
    """Handle Google Sheets API authentication."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def discover_sheets_api():
    """Discover all sheets using Google Sheets API."""
    creds = authenticate()
    service = build('sheets', 'v4', credentials=creds)
    
    # Get spreadsheet metadata
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    
    print(f"# Sheet discovery for spreadsheet: {SPREADSHEET_ID}")
    print(f"# Total sheets found: {len(spreadsheet['sheets'])}")
    print()
    
    for sheet in spreadsheet['sheets']:
        props = sheet['properties']
        name = props['title']
        gid = props['sheetId']
        safe_name = name.lower().replace(' ', '_').replace('[^a-z0-9_]', '_')
        
        print(f"# {name}")
        print(f"GID_{safe_name.upper()} = {gid}")
        print(f"downloads/sheets/{safe_name}.tsv:")
        print(f"\tcurl -L -s '$(BASE_URL)?exportFormat=tsv&gid={gid}' > $@")
        print()

if __name__ == "__main__":
    discover_sheets_api()
```

**Setup for Sheets API approach:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Google Sheets API
4. Create credentials (OAuth 2.0 client ID for desktop application)
5. Download `credentials.json` to your project directory
6. Run the script - it will open browser once for authentication

### Option 3: Apps Script API (Python)

**Use Apps Script API to run the same JavaScript code:**
```python
from googleapiclient.discovery import build

def run_apps_script():
    service = build('script', 'v1', credentials=creds)
    
    # First deploy the script as shown in Option 1
    script_id = 'YOUR_SCRIPT_ID'  # From clasp or Apps Script editor
    
    request = {"function": "listAllSheets"}
    response = service.scripts().run(scriptId=script_id, body=request).execute()
    
    if 'response' in response:
        print(response['response']['result'])
```

### Option 4: Enhanced Python Discovery (No Auth)

**Improve the existing `discover_sheet_ids.py` with better fallback methods:**

We could enhance our current script to try multiple discovery approaches:
1. Legacy feeds API (current method)
2. HTML parsing of the public sheet URL
3. CSV export introspection

This would keep the "no authentication" benefit while being more robust.

## Comparison of Approaches

| Method | Pros | Cons | Auth Required |
|--------|------|------|---------------|
| Browser Apps Script | Simple, direct access | Requires browser | No |
| `clasp` CLI | Command line, same code | Requires Node.js, one-time auth | Yes (one-time) |
| Sheets API | Full API access, robust | Setup complexity | Yes |
| Apps Script API | Programmatic execution | Complex setup | Yes |
| Enhanced Python | No auth, lightweight | May break with changes | No |

**Recommendation:** Use `clasp` for automated workflows, browser Apps Script for manual discovery.

## Troubleshooting

**"Script execution not enabled"**
- Ensure you're running the script from within the target spreadsheet's Apps Script editor

**"Permission denied"**
- The script runs with your Google account permissions. Ensure you have at least view access to the spreadsheet.

**clasp authentication issues**
- Run `clasp logout` then `clasp login` to refresh credentials
- Ensure Google Apps Script API is enabled in your Google Cloud project

**Empty output**
- Check that the spreadsheet has multiple sheets/tabs
- Verify you're in the correct spreadsheet

**Makefile errors**
- Ensure no trailing spaces in the copied GID variables
- Check that all curl commands have proper syntax