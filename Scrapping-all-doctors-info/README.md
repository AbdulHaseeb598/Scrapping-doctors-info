# 🏥 Marham.pk Complete Doctors Database Scraper

## 📋 Project Overview

A comprehensive **Playwright-based** web scraper that automatically extracts **complete doctor information** from **ALL cities** on Marham.pk and saves it to a CSV database. This scraper is designed for building a complete doctors knowledge base across Pakistan.

## ✨ Key Features

### Core Functionality
- ✅ **Automated City Discovery** - Automatically discovers all cities on Marham.pk
- ✅ **Comprehensive Data Extraction** - Extracts 18+ data fields per doctor
- ✅ **Multi-Hospital Support** - Handles doctors with multiple hospital locations
- ✅ **Pagination Support** - Automatically navigates through all pages (up to 8 pages per city)
- ✅ **Resume Capability** - Skips already scraped cities, can resume from where it left off
- ✅ **Profile Deep Dive** - Visits each doctor's profile page to extract weekly schedules
- ✅ **Cloudflare Bypass** - Uses Playwright's browser automation to bypass protections
- ✅ **Stealth Mode** - Implements anti-detection techniques
- ✅ **CSV Database** - Saves all data to a single CSV file with proper formatting

### Data Extracted (18 Fields)

#### Doctor Information
- Full name
- Specialization (e.g., Cardiologist, Gynecologist)
- Qualifications (MBBS, FCPS, MD, etc.)
- Years of experience
- Patient satisfaction rate (%)
- Number of reviews
- Areas of interest (subspecialties)
- Profile URL
- Doctor image URL

#### Hospital & Location Data
- Hospital name
- Hospital address
- Hospital city
- Complete address (with notes)
- Consultation type (Hospital / Video Consultation)

#### Availability & Fees
- Consultation fee (Rs.)
- Weekly availability schedule (Day-wise timings)

#### Metadata
- Source city URL
- Raw source URL for verification

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Step 1: Navigate to Project Directory
```bash
cd "u:\Abdul_Haseeb(BAI)\cui internship\Scrapping-doctors-info"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Install Playwright Browsers
```bash
playwright install chromium
```

## 📦 Dependencies

```txt
playwright>=1.40.0
```

Playwright includes:
- Browser automation (Chromium, Firefox, WebKit)
- Network interception
- Anti-detection capabilities
- Screenshot & PDF generation

## 🎯 Usage Guide

### Basic Usage

1. **Run the scraper:**
   ```bash
   python scrape_doctors.py
   ```

2. **First Run (Important):**
   - Set `HEADLESS = False` in the script (line 14)
   - This opens a visible browser window
   - Manually solve Cloudflare challenge if prompted
   - After successful bypass, you can set `HEADLESS = True` for subsequent runs

3. **The scraper will:**
   - Discover all cities from https://www.marham.pk/doctors
   - Scrape each city page (up to 8 pages per city)
   - Visit each doctor's profile for detailed schedule
   - Save data incrementally to `doctors_knowledge_base.csv`
   - Skip already processed cities on resume

4. **Monitor progress:**
   ```
   Discovered 50 cities; already scraped 10.
   
   === Processing Karachi ===
   Saved 120 rows for Karachi
   
   === Processing Lahore ===
   Saved 95 rows for Lahore
   ```

5. **Output:**
   - File: `doctors_knowledge_base.csv`
   - Incremental saves (data preserved even if interrupted)
   - Can resume anytime

### Configuration Options

Edit these variables in `scrape_doctors.py`:

```python
# Line 13-16
OUTPUT_CSV = "doctors_knowledge_base.csv"  # Output filename
HEADLESS = False                           # False = visible browser (for first run)
CITY_LIMIT: Optional[int] = None           # Limit cities (None = all cities)
DELAY_MIN, DELAY_MAX = 0.8, 2.0           # Random delay between requests
MAX_PAGES_PER_CITY = 8                    # Maximum pagination per city
```

#### Configuration Examples:

**Test run (2 cities only):**
```python
CITY_LIMIT = 2
HEADLESS = False
```

**Production run (all cities):**
```python
CITY_LIMIT = None
HEADLESS = True
MAX_PAGES_PER_CITY = 8
```

**Slower scraping (more polite):**
```python
DELAY_MIN, DELAY_MAX = 2.0, 5.0
```

## 📂 Output Format

### CSV Structure

**Filename:** `doctors_knowledge_base.csv`

**Columns (18 fields):**
```csv
city,name,specialization,qualification,experience,satisfaction_rate,reviews,areas_of_interest,consultation_type,hospital_name,hospital_address,hospital_city,complete address,availability_schedule,fee,profile_url,image_url,raw_source_url
```

### Sample Output

```csv
city,name,specialization,qualification,experience,satisfaction_rate,reviews,areas_of_interest,consultation_type,hospital_name,hospital_address,hospital_city,complete address,availability_schedule,fee,profile_url,image_url,raw_source_url
Lahore,Dr. Aisha Khan,Gynecologist,"MBBS, FCPS",15 yrs,98%,250,"Pregnancy Care, High-Risk Pregnancy",Hospital,XYZ Medical Center,"Model Town, Lahore",Lahore,"Available Mon-Fri","Mon: 09:00 AM - 05:00 PM; Tue: 09:00 AM - 05:00 PM; Wed: 09:00 AM - 05:00 PM",Rs. 2500,https://www.marham.pk/doctors/lahore/gynecologist/dr-aisha-khan-12345,https://cdn.marham.pk/images/dr-aisha.jpg,https://www.marham.pk/doctors/lahore
Karachi,Dr. Ahmed Ali,Cardiologist,"MBBS, FCPS (Cardiology), MRCP",20 yrs,100%,180,"Heart Disease, Cardiac Surgery",Hospital,Aga Khan Hospital,"Stadium Road, Karachi",Karachi,"Walk-in Available","Mon: 10:00 AM - 06:00 PM; Thu: 10:00 AM - 06:00 PM; Fri: 02:00 PM - 08:00 PM",Rs. 3000,https://www.marham.pk/doctors/karachi/cardiologist/dr-ahmed-ali-67890,https://cdn.marham.pk/images/dr-ahmed.jpg,https://www.marham.pk/doctors/karachi
```

### Field Descriptions

| Field | Description | Example |
|-------|-------------|---------|
| `city` | Source city of the listing | Lahore |
| `name` | Doctor's full name | Dr. Aisha Khan |
| `specialization` | Medical specialty | Gynecologist |
| `qualification` | Academic degrees | MBBS, FCPS |
| `experience` | Years of practice | 15 yrs |
| `satisfaction_rate` | Patient satisfaction | 98% |
| `reviews` | Number of reviews | 250 |
| `areas_of_interest` | Subspecialties | Pregnancy Care, High-Risk Pregnancy |
| `consultation_type` | Hospital or Video | Hospital / Video Consultation |
| `hospital_name` | Hospital/clinic name | XYZ Medical Center |
| `hospital_address` | Street address | Model Town, Lahore |
| `hospital_city` | City of hospital | Lahore |
| `complete address` | Additional notes | Available Mon-Fri |
| `availability_schedule` | Weekly timings | Mon: 09:00 AM - 05:00 PM; Tue: 09:00 AM - 05:00 PM |
| `fee` | Consultation fee | Rs. 2500 |
| `profile_url` | Doctor's profile link | https://www.marham.pk/doctors/... |
| `image_url` | Doctor's photo URL | https://cdn.marham.pk/images/... |
| `raw_source_url` | Source listing URL | https://www.marham.pk/doctors/lahore |

## 🔄 Complete Workflow Pipeline

### Phase 1: City Discovery
```
Start Script
      ↓
Visit: https://www.marham.pk/doctors
      ↓
Extract all city links (e.g., /doctors/lahore, /doctors/karachi)
      ↓
Filter valid city pages (path format: /doctors/{city})
      ↓
Sort cities alphabetically
      ↓
Output: List of (city_name, city_url) tuples
```

### Phase 2: Resume Check
```
Read existing CSV file
      ↓
Extract list of already scraped cities
      ↓
Compare with discovered cities
      ↓
Skip cities already in CSV
      ↓
Output: List of cities to scrape
```

### Phase 3: City-Level Scraping
```
For each city:
      ↓
Visit city listing page (e.g., /doctors/lahore)
      ↓
Extract all doctor cards on page
      ↓
For each doctor card:
      ├─ Extract basic info (name, specialization, qualifications)
      ├─ Extract metrics (experience, satisfaction, reviews)
      ├─ Extract areas of interest (chips/tags)
      ├─ Visit doctor's profile page
      │  └─ Extract weekly availability schedules
      ├─ Extract hospital cards (1+ hospitals per doctor)
      │  ├─ Hospital name
      │  ├─ Hospital address
      │  ├─ Consultation fee
      │  ├─ Consultation type (Hospital/Video)
      │  └─ Match schedule from profile
      └─ Create CSV row for each hospital
      ↓
Check for "Next Page" button
      ↓
If exists: Navigate to next page (repeat up to MAX_PAGES_PER_CITY)
      ↓
Save all rows to CSV (append mode)
      ↓
Add random delay (DELAY_MIN to DELAY_MAX seconds)
      ↓
Move to next city
```

### Phase 4: Data Persistence
```
Incremental CSV Writing
      ↓
Append rows after each city completes
      ↓
Data preserved even if script interrupted
      ↓
Resume capability on next run
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    SCRIPT START                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│        Launch Playwright Browser (Chromium)                  │
│        - Apply stealth scripts                               │
│        - Set viewport: 1200x900                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              CITY DISCOVERY MODULE                           │
│  discover_city_links()                                       │
│  - Visit: https://www.marham.pk/doctors                      │
│  - Extract: <a href="/doctors/[city]">                       │
│  - Filter: /doctors/{city} pattern only                      │
│  - Output: [(city_name, url), ...]                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              RESUME CHECK MODULE                             │
│  read_scraped_cities()                                       │
│  - Read existing CSV                                         │
│  - Extract "city" column values                              │
│  - Output: Set of already scraped cities                     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              FILTER CITIES TO SCRAPE                         │
│  Skip cities already in CSV                                  │
│  Apply CITY_LIMIT if configured                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │ FOR EACH CITY (not yet scraped) │
        └────────────────┬────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         PAGINATION HANDLER                                   │
│  scrape_city_with_pagination()                               │
│  - Start with page 1                                         │
│  - Loop up to MAX_PAGES_PER_CITY                             │
│  - Extract doctors from current page                         │
│  - Find "Next" button                                        │
│  - Navigate to next page if exists                           │
│  - Repeat until no more pages                                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         CITY PAGE SCRAPER                                    │
│  extract_doctors_from_city_page()                            │
│  - Find all: div.row.shadow-card (doctor cards)              │
│  - For each card → Extract doctor data                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │  FOR EACH DOCTOR CARD           │
        └────────────────┬────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         CARD DATA EXTRACTION                                 │
│  1. Basic Info:                                              │
│     - Name: <h3>                                             │
│     - Profile URL: <a.dr_profile_opened_from_listing>        │
│     - Image: <picture source> or <img.round-img>             │
│                                                              │
│  2. Label/Metric Extraction:                                 │
│     extract_label_values()                                   │
│     - Parse div.col-4 blocks                                 │
│     - Classify using regex:                                  │
│       • Experience: /\d+ yrs?/                               │
│       • Satisfaction: /\d+%/                                 │
│       • Reviews: /\d{1,3}(,\d{3})*/                          │
│     - Extract specialization: first p.text-sm                │
│     - Extract qualification: second p.text-sm                │
│                                                              │
│  3. Areas of Interest:                                       │
│     - Extract: span.chips-highlight, span.chips              │
│     - Join with commas                                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         PROFILE DEEP DIVE (for schedules)                    │
│  extract_availability_from_profile()                         │
│  - Visit doctor's profile page                               │
│  - Find: section.p-xy .shadow-card (schedule blocks)         │
│  - For each block:                                           │
│    • Extract title: <h3> (hospital name)                     │
│    • Parse table: <tr><td>Day</td><td>Time</td></tr>         │
│    • Build: "Mon: 09:00 AM - 05:00 PM; Tue: ..."            │
│  - Cache results (avoid re-fetching for same doctor)         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │  FOR EACH HOSPITAL CARD         │
        │  (1+ hospitals per doctor)      │
        └────────────────┬────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         HOSPITAL DATA EXTRACTION                             │
│  Extract from: div.product-card attributes                   │
│  - data-hospitalname    → Hospital name                      │
│  - data-hospitalcity    → City                               │
│  - data-hospitaladdress → Address                            │
│  - data-amount          → Fee                                │
│  - data-hospitaltype    → Type (2 = Video)                   │
│                                                              │
│  Parse availability note:                                    │
│  - <p.text-sm> inside card                                   │
│                                                              │
│  Match schedule:                                             │
│  match_schedule_for_hospital()                               │
│  - Find best matching schedule from profile data             │
│  - Use hospital name token matching                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         BUILD CSV ROW                                        │
│  Create dict with all 18 fields:                             │
│  - Doctor info (name, specialization, etc.)                  │
│  - Hospital info (name, address, fee)                        │
│  - Availability (schedule, complete address)                 │
│  - Metadata (URLs, source)                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         ACCUMULATE ROWS                                      │
│  Add row to results list                                     │
│  Continue for all hospitals of this doctor                   │
│  Continue for all doctors on this page                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         SAVE TO CSV                                          │
│  append_rows()                                               │
│  - Open CSV in append mode                                   │
│  - Write header if new file                                  │
│  - Write all rows for this city                              │
│  - Close file (data persisted)                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         RANDOM DELAY                                         │
│  time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))            │
│  - Polite scraping                                           │
│  - Avoid rate limiting                                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
                  [NEXT CITY]
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         ALL CITIES COMPLETE                                  │
│  - Close browser                                             │
│  - Print summary                                             │
│  - Exit successfully                                         │
└──────────────────────────────────────────────────────────────┘
```

## 🔧 Key Functions Reference

### Main Functions

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `main()` | Entry point | None | Coordinates entire scraping process |
| `discover_city_links()` | Find all cities | BrowserContext | List of (city_name, url) tuples |
| `scrape_city_with_pagination()` | Scrape city with pages | City name, URL | List of doctor row dicts |
| `extract_doctors_from_city_page()` | Extract from one page | City name, URL | List of doctor row dicts |
| `extract_availability_from_profile()` | Get weekly schedule | Profile URL | Dict of {hospital: schedule} |
| `extract_label_values()` | Parse card metrics | Card element | Dict of field values |

### Helper Functions

| Function | Purpose |
|----------|---------|
| `apply_stealth()` | Add anti-detection scripts |
| `normalise_href()` | Convert relative URLs to absolute |
| `inner_text_safe()` | Safely extract element text |
| `classify_line_for_metric()` | Identify metric type (experience/reviews/satisfaction) |
| `match_schedule_for_hospital()` | Match profile schedule to hospital |
| `is_reviews_candidate()` | Check if text is a review count |
| `append_rows()` | Write rows to CSV |
| `read_scraped_cities()` | Read already processed cities |
| `rnd_sleep()` | Random delay between requests |

## 🐛 Troubleshooting

### Common Issues

#### 1. Cloudflare Challenge
**Problem:** Browser shows "Checking your browser..." or Cloudflare page

**Solution:**
```python
# Set HEADLESS = False on line 14
HEADLESS = False
```
- Run script
- Wait for browser window to open
- Manually solve challenge if needed
- Script will continue automatically
- For subsequent runs, can set `HEADLESS = True`

#### 2. Empty CSV or No Cities Found
**Problem:** Script completes but CSV is empty

**Solutions:**
- Check internet connection
- Run with `HEADLESS = False` first
- Check if Marham.pk structure changed
- Verify URL: https://www.marham.pk/doctors is accessible

#### 3. Playwright Not Installed
**Problem:** "playwright is not installed"

**Solutions:**
```bash
pip install playwright
playwright install chromium
```

#### 4. Script Interrupted Mid-Run
**Problem:** Script stopped before completing all cities

**Solution:**
- Just run the script again!
- It will automatically skip already scraped cities
- Continue from where it left off

#### 5. Timeout Errors
**Problem:** "Timeout exceeded while waiting for selector"

**Solutions:**
- Increase timeout values in code
- Check internet connection speed
- Reduce `MAX_PAGES_PER_CITY`
- Increase `DELAY_MIN` and `DELAY_MAX`

## 📊 Performance & Limitations

### Performance Metrics
- **City discovery:** ~5-10 seconds
- **Single doctor card:** ~1-2 seconds
- **Profile page visit:** ~2-4 seconds (for schedule)
- **Per city (50 doctors, 8 pages):** ~10-15 minutes
- **Full database (50 cities):** ~8-12 hours

### Optimization Tips
```python
# Faster scraping (less polite)
DELAY_MIN, DELAY_MAX = 0.5, 1.0
MAX_PAGES_PER_CITY = 5

# Slower scraping (more polite, recommended)
DELAY_MIN, DELAY_MAX = 2.0, 4.0
MAX_PAGES_PER_CITY = 10
```

### Known Limitations
1. **Cloudflare:** May require manual intervention on first run
2. **Dynamic Content:** Some data loads via JavaScript (handled by Playwright)
3. **Rate Limiting:** Marham.pk may throttle if too fast (use delays)
4. **Schedule Matching:** Fuzzy matching may not always be 100% accurate
5. **Pagination Limit:** Default 8 pages per city (configurable)

## 🔒 Best Practices

### 1. Responsible Scraping
- Use reasonable delays (`DELAY_MIN = 0.8` or higher)
- Run during off-peak hours
- Don't run multiple instances simultaneously
- Respect website's terms of service

### 2. Data Validation
- Always verify extracted data quality
- Check for null/empty values
- Cross-reference critical information with website

### 3. Code Maintenance
- Keep Playwright updated: `pip install --upgrade playwright`
- Re-run `playwright install chromium` after updates
- Monitor for HTML structure changes on Marham.pk

### 4. Data Usage
- Use data responsibly and ethically
- Don't republish without permission
- Respect patient privacy (reviews are public but sensitive)

## 📁 Project Structure

```
Scrapping-doctors-info/
│
├── scrape_doctors.py              ← MAIN SCRAPER (Playwright-based)
├── doctors_knowledge_base.csv     ← OUTPUT (Generated by scraper)
├── requirements.txt               ← Python dependencies
├── README.md                      ← This documentation
├── PROJECT_SUMMARY.md             ← Quick reference guide
│
├── venv/                          ← Virtual environment (don't commit)
│
└── .git/                          ← Git repository
```

## 🚦 Quick Start

```bash
# 1. Setup
cd "Scrapping-doctors-info"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium

# 2. Configure (optional)
# Edit scrape_doctors.py:
# - Set HEADLESS = False (first run)
# - Set CITY_LIMIT = 2 (test run)

# 3. Run
python scrape_doctors.py

# 4. Output
# Check: doctors_knowledge_base.csv
```

## 📈 Expected Results

### Sample Run Output
```
Discovered 50 cities; already scraped 0.

=== Processing Karachi ===
Saved 120 rows for Karachi

=== Processing Lahore ===
Saved 95 rows for Lahore

=== Processing Islamabad ===
Saved 78 rows for Islamabad

...

✅ Done. Total saved this run: 2850. File: doctors_knowledge_base.csv
```

### Database Size Estimates
- **Per city:** 50-150 rows (doctors × hospitals)
- **All cities:** 2,500-7,500+ rows
- **CSV file size:** 2-5 MB (uncompressed)

## 🔄 Comparison with marham_crawler2.py

| Feature | scrape_doctors.py (This Project) | marham_crawler2.py |
|---------|----------------------------------|-------------------|
| **Scope** | ALL doctors from ALL cities | Specific query (e.g., "gynecologist in lahore") |
| **Automation** | Fully automated city discovery | Requires user input query |
| **Output** | Single CSV with all data | Individual JSON files per doctor |
| **Browser** | Playwright (Chromium) | Crawl4AI (async) |
| **Resume** | Automatic (skips scraped cities) | Manual re-run |
| **Reviews** | Not included | Optional with LLM summary |
| **Use Case** | Building complete database | Targeted doctor search |
| **Run Time** | 8-12 hours (full database) | 30-60 seconds per query |

## 🎯 Use Cases

### 1. Healthcare Database
Build a comprehensive database of all doctors in Pakistan for:
- Medical directories
- Appointment booking systems
- Healthcare analytics platforms

### 2. Market Research
Analyze doctor distribution:
- Specialties per city
- Pricing trends across regions
- Hospital network mapping

### 3. Data Analysis
- Average fees by specialty
- Experience vs satisfaction correlation
- Geographic distribution of specialists

### 4. Integration
Import CSV into:
- SQL databases (PostgreSQL, MySQL)
- NoSQL databases (MongoDB)
- Data warehouses (BigQuery, Snowflake)
- Analytics tools (Tableau, Power BI)

## 📝 CSV Import Examples

### Python Pandas
```python
import pandas as pd
df = pd.read_csv('doctors_knowledge_base.csv')
print(df.head())
print(f"Total doctors: {len(df)}")
```

### PostgreSQL
```sql
COPY doctors_knowledge_base
FROM '/path/to/doctors_knowledge_base.csv'
DELIMITER ','
CSV HEADER;
```

### Excel/Google Sheets
- File → Import → CSV
- Select `doctors_knowledge_base.csv`
- Delimiter: Comma
- Encoding: UTF-8

## 🤝 Contributing

Found an issue or want to improve the scraper?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is for educational purposes. Please respect Marham.pk's terms of service and use responsibly.

## 👨‍💻 Author

**Abdul Haseeb**
- GitHub: [@AbdulHaseeb598](https://github.com/AbdulHaseeb598)
- Repository: [Scrapping-doctors-info](https://github.com/AbdulHaseeb598/Scrapping-doctors-info)

## 🎓 Project Context

Developed as part of CUI Internship project for web scraping and comprehensive data extraction using Playwright browser automation.

## 📅 Version History

### v1.0 (Current)
- ✅ Complete city discovery automation
- ✅ Pagination support (8 pages per city)
- ✅ Profile schedule extraction
- ✅ Multi-hospital support
- ✅ Resume capability
- ✅ Robust metric classification
- ✅ CSV incremental saves
- ✅ Stealth mode anti-detection

---

**🎉 Ready to build a complete doctors database! Run the scraper and collect comprehensive healthcare data from Marham.pk!**

For questions or issues, please open an issue on GitHub.
