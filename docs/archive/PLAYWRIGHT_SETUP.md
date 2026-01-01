# Playwright Setup Guide

## Installation

To use the **Future Enhancement** tab's web content extractor, you need to install Playwright and its browser binaries.

### Step 1: Install Playwright Python Package

```bash
pip install playwright
```

### Step 2: Install Browser Binaries

After installing the package, install the Chromium browser:

```bash
playwright install chromium
```

Or install all browsers (Chromium, Firefox, WebKit):

```bash
playwright install
```

## Verification

Test if Playwright is working:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    print(page.title())
    browser.close()
```

## Troubleshooting

### Error: "Executable doesn't exist"

Run the install command again:
```bash
playwright install chromium
```

### Error: "Could not find browser"

Make sure you've installed the browser binaries after installing the package.

### Windows-specific Issues

If you encounter permission errors on Windows, run the command prompt as Administrator.

## Usage in the App

1. Go to the **🚀 Future Enhancement** tab
2. Paste any website URL
3. Click **🔍 Extract Content**
4. View extracted content in organized tabs:
   - Full text content
   - All links found
   - Headings structure
   - Lists
   - Images
5. Export or send to Translation tab

## Features

The extractor provides:
- ✅ Complete text content extraction
- ✅ All links with their text and URLs
- ✅ All images with alt text
- ✅ Page structure (headings, lists, paragraphs)
- ✅ Page metadata (title, description, keywords)
- ✅ Export to file or CSV
- ✅ Direct integration with Translation tab
