# ⚡ LinkedIn Tender & Scheme Tracker

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/API-Mistral%20AI-orange?style=for-the-badge&logo=mistral&logoColor=white" alt="Mistral AI" />
  <img src="https://img.shields.io/badge/Browser-Playwright%20CDP-green?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright" />
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows&logoColor=white" alt="Platform Windows" />
  <img src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge" alt="License Proprietary" />
</p>

An internal automation tool built for **KDI Power Private Limited** to track LinkedIn posts from key industry competitors and partners, filter posts related to electrical wire and cable tenders/contracts, summarize them using Mistral AI, and record them in an Excel tracking sheet.

---

## 🔍 Features

*   **Secure Browsing**: Connects directly to your already active, logged-in Chrome session via Chromium CDP. The script **never** stores or automates login passwords, keeping your account safe from bot restriction flags.
*   **Targeted Competitor Tracking**: Automatically visits the recent activity pages of **10 target profiles** in the wire and cable sector (e.g. Polycab, KEI, Finolex, RR Global, V-Guard, Havells, etc.).
*   **Smart Filtering**: Scrapes recent posts and filters them based on keywords related to tenders, power schemes, distribution grids, and electrification orders.
*   **Direct AI Summarization**: Integrates directly with the **Mistral API** (`mistral-small-latest`) to generate concise 3–5 bullet point summaries.
*   **Double-Click Simplicity**: Runs via a simple double-click on `RunTracker.bat` for everyday office use.
*   **Robust Fault Tolerance**:
    *   *Excel Lock Check*: Detects if `Master_Tracker.xlsx` is open in Microsoft Excel *before* starting the run and alerts you.
    *   *Layout Check*: Warns you if LinkedIn's HTML structure has changed, avoiding silent failures.

---

## 📂 Project Structure

```text
├── docs/                      # Project assignment specs and requirement PDF
├── scripts/                   # Legacy login and pipeline test scripts
│   ├── login.py               # Persistent login setup utility
│   ├── test_mistral.py        # Direct Mistral connection check
│   └── test_pipeline.py       # Full processing verification using mock posts
├── summaries/                 # Locally stored detailed post summary txt files
├── .env                       # Environment configurations (API key, user profile path)
├── .gitignore                 # Files excluded from git tracking
├── config.json                # Editable list of targets and industry keywords
├── main.py                    # Script orchestrator and process launcher
├── processor.py               # Direct Mistral API summarization module
├── scraper.py                 # Playwright CDP scraper module
├── storage.py                 # Excel data manager (pandas/openpyxl)
├── requirements.txt           # Python library dependencies
└── RunTracker.bat             # Desktop batch runner (double-click executable)
```

---

## 🛠️ Setup Instructions

### 1. Pre-requisites
*   **Python 3.12+** installed on Windows.
*   **Google Chrome** installed.

### 2. Install Dependencies
Open a PowerShell terminal in the project directory and run:
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 3. Configure the Environment
Create a `.env` file in the root directory (or edit the existing one):
```ini
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-latest
CHROME_USER_DATA_DIR=C:\Users\<YourUsername>\AppData\Local\Google\Chrome\User Data
```

### 4. Edit Targets and Keywords
Open `config.json` to edit or add target LinkedIn profile links and keyword criteria:
```json
{
  "target_profiles": [
    "https://www.linkedin.com/company/polycab-india-limited/recent-activity/all/",
    ...
  ],
  "keywords": [
    "tender", "cable", "wire", "grid", ...
  ]
}
```

---

## 🚀 Daily Usage

To run the tracker daily, complete these steps:

1.  **Close all Chrome windows** on your machine.
2.  Open **PowerShell** and run Chrome with debugging enabled:
    ```powershell
    & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --profile-directory="Profile 2"
    ```
    *(Note: Replace "Profile 2" with your active profile. Ensure you are logged into LinkedIn in this window)*.
3.  **Double-click** the **[RunTracker.bat](file:///d:/KDI-LinkedIn%20Schema%20Tracker/RunTracker.bat)** file at the root of the project.
4.  The script will automatically run, scrape matching posts, save summaries in the spreadsheet, and print a summary report.

---

## 📄 License
This project is proprietary and built strictly for the internal use of **KDI Power Private Limited**.
