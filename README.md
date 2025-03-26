# 🔍 Logo-Scraper

**Logo-Scraper** is a Python tool that scrapes logos (favicons) from websites listed in a file called `data.csv`, and groups visually similar ones using perceptual hashing (pHash). It's fast, automated, and ideal for large-scale domain logo discovery and clustering.


# 🔑 Key Concepts

### 🔍 How logos are retrieved

Logo-Scraper attempts to find and download the most relevant logo for each domain using a layered fallback strategy:
- Parses the HTML for declared favicons or logo images
- Queries external services like Clearbit and DuckDuckGo
- Attempts default favicon locations (`/favicon.ico`) with multiple variants
- Validates and converts the downloaded files if needed (e.g., SVG → PNG)

### 🧠 How logos are grouped
- Each logo is hashed using perceptual hashing (`imagehash.phash`)
- Hamming distance is calculated between each pair of hashes
- Logos with similar visual structure (distance ≤ 25) are grouped together

## 🚀 How to Use

### 📦 Installation

Make sure you have **Python 3.9+** installed, then run:

```bash
make install
```

This will:

- Create a virtual environment in ./venv
- Install all required dependencies from requirements.txt

💡 Tip: After running `make install`, activate the virtual environment with:

```bash
source venv/bin/activate
```
### ▶️ Running the scraper & grouper

To run the full pipeline (logo scraping + grouping):

```bash
make run
```

---

### 🛠️ Other Makefile Commands

| Command        | Description                                       |
|----------------|---------------------------------------------------|
| `make install` | Set up virtual environment and install dependencies |
| `make run`     | Run both the scraper and the grouping logic       |                |
| `make clean`   | Remove all generated output files                 |

---

---
### 📁 Output Files

| File                      | Description                                      |
|---------------------------|--------------------------------------------------|
| `logo_hashes.json`        | Maps each domain to its perceptual hash         |
| `logo_groups.json`        | Groups of visually similar domains              |
| `failed_logos.txt`        | List of domains where scraping failed           |
| `logo_scraping_results.txt` | Full scraping log with debug output           |

---

### 📊 Example Statistics

From a test run on 3,416 unique domains:

- Logos retrieved: 3,377  
- Logos failed: 39  
- Logo groups created: 63  
- Runtime: ~5 minutes


# 📂 Project Structure

| Fisier | Descriere |
 |---------------|-----------| 
 | `client.c` | Main implementation of the client application | 
 | `helpers.c` | Utility functions for string manipulation and network connections | 
 | `buffer.c` | Functions for handling dynamic memory buffers used in communication |

### 🕸️ In-Depth: How Logo Scraping Works

Logo-Scraper uses a prioritized strategy to extract logos from websites:

**1. HTML Parsing (Preferred)**  
- Loads the homepage using `requests`  
- Parses HTML using `BeautifulSoup`  
- Searches for:
  - `<link rel="icon" href="...">`
  - `<img>` tags whose `src`, `alt`, or class attributes contain the word "logo"

**2. Clearbit API**  
- Tries to retrieve a logo from:  
  `https://logo.clearbit.com/<domain>`  
- High-quality logos for many known companies

**3. Direct Favicon Attempt**  
- Tries to fetch:  
  - `https://<domain>/favicon.ico`  
  - `https://www.<domain>/favicon.ico`  
- Standard web convention

**4. DuckDuckGo Favicon API**  
- Uses:  
  `https://icons.duckduckgo.com/ip3/<domain>.ico`  
- Provides small, cached icons for many domains

**5. Manual Fallback Favicon**  
- Retries favicon fetch using custom headers and relaxed SSL  
- Handles edge cases and domains with non-standard setups

**6. Validation & Conversion**  
- All images are validated using Pillow  
- SVGs are converted to PNG using cairosvg  
- Images are discarded if unreadable or corrupt
 
 ### 🧠 In-Depth: How Logo Grouping Works

**1. Perceptual Hashing**  
- Each image is converted to a `phash` using the `imagehash` library  
- pHash generates a fingerprint that represents visual content  
- Resilient to small changes in size, color, compression, etc.

**2. Similarity Comparison**  
- Each hash is compared to every other using Hamming distance  
- If the distance between two hashes is below the threshold (default: 25), they are considered visually similar

**3. Clustering**  
- Similar domains are grouped together in `logo_groups.json`  
- Each group contains a unique `group_id` and a list of matching domains

**Example Group Output:**

```json
{
  "group_id": 42,
  "domains": [
    "github.com",
    "gist.github.com",
    "github.blog"
  ]
}
```

## 🏃 Running Example (command: make run)

![Image](https://github.com/user-attachments/assets/95bc617b-c529-42af-b42f-27b02aa13737)
