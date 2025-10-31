# 🏥 Marham.pk Doctor Scraper - Complete Documentation

## 📋 Project Overview

A comprehensive Python-based web scraper for extracting detailed doctor information, hospital details, weekly schedules, and patient reviews from Marham.pk - Pakistan's largest healthcare platform.

## ✨ Features

### Core Functionality
- ✅ **Natural Language Query Processing** - Search using plain English (e.g., "gynecologist in model town lahore")
- ✅ **Intelligent Search** - Multi-provider web search (DuckDuckGo, Bing) with automatic URL ranking
- ✅ **Doctor Profile Extraction** - Complete doctor information including qualifications, experience, ratings
- ✅ **Hospital Details** - Hospital names, complete addresses, consultation fees
- ✅ **Weekly Schedules** - Day-wise availability timings for each hospital location
- ✅ **Video Consultation** - Fees and timings for online consultations
- ✅ **Patient Reviews** - Review extraction with sentiment tags
- ✅ **AI-Powered Summaries** - LLM-generated review summaries using Groq API

### Data Extracted

#### Doctor Information
- Full name and title (Dr., Prof., Asst. Prof.)
- Specialty/specialization
- Medical qualifications (MBBS, FCPS, MD, MS, etc.)
- PMDC verification status
- Years of experience
- Patient satisfaction rating
- Reviews count
- Wait time and average consultation time
- Contact phone number
- Professional statement/bio
- Medical services offered
- Languages spoken

#### Hospital Information
- Hospital/clinic name
- Complete address (Area + City)
- Consultation fee
- **Weekly availability schedule** (Day-wise timings)
- Google Maps integration support

#### Reviews & Ratings
- Patient name (initials)
- Review date
- Review text/comments
- Experience tags (wait time, satisfaction, clinic environment)
- AI-generated summary of all reviews

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Step 1: Clone Repository
```bash
git clone https://github.com/AbdulHaseeb598/Scrapping-doctors-info.git
cd cui-internship
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

### Step 5: Verify Installation
```bash
python marham_crawler2.py
```

## 📦 Required Dependencies

Create `requirements.txt` with:
```txt
crawl4ai==0.7.4
httpx
groq
pydantic
asyncio
```

Install using:
```bash
pip install crawl4ai httpx groq pydantic
```

## 🔑 API Configuration

### Groq API Key
The scraper uses Groq LLM for generating intelligent review summaries.

**Setup API Key:**
1. Get a free API key from [Groq Console](https://console.groq.com/)
2. Create a `.env` file in the project root:
   ```bash
   GROQ_API_KEY=your_api_key_here
   ```
3. The script will automatically load it from the `.env` file

**Example `.env` file:**
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## 🎯 Usage Guide

### Basic Usage

1. **Run the scraper:**
   ```bash
   python marham_crawler2.py
   ```

2. **Enter your search query when prompted:**
   ```
   🔍 Enter your search query: gynecologist in model town lahore
   ```

3. **The scraper will:**
   - Extract specialty, area, and city from your query
   - Search for relevant Marham.pk URLs
   - Validate and rank URLs by relevance
   - Auto-select the most relevant listing page
   - Extract doctor profiles from the listing

4. **Select a doctor from the list:**
   ```
   👉 Enter the number of the doctor (or 0 to exit): 1
   ```

5. **View complete details:**
   - Doctor profile information
   - Hospital addresses with weekly schedules
   - Video consultation details (if available)

6. **Optional: View reviews with AI summary:**
   ```
   👉 View reviews with LLM summary? (yes/no): yes
   ```

### Query Examples

| Query | What it extracts |
|-------|------------------|
| `gynecologist in model town lahore` | Gynecologists in Model Town, Lahore |
| `cardiologist in dha karachi` | Cardiologists in DHA, Karachi |
| `dermatologist in i8 islamabad` | Dermatologists in I-8 Markaz, Islamabad |
| `orthopedic in g8 markaz islamabad` | Orthopedic surgeons in G-8 Markaz, Islamabad |
| `endocrinologist in bahria town rawalpindi` | Endocrinologists in Bahria Town, Rawalpindi |

### Query Format
```
[specialty] in [area] [city]
```

**Components:**
- **Specialty**: Doctor type (e.g., cardiologist, dermatologist, gynecologist)
- **Area**: Specific location/sector (e.g., model town, dha, i-8, g-8 markaz)
- **City**: Major city (e.g., lahore, karachi, islamabad, rawalpindi)

## 📂 Output Files

### 1. Doctor Profile JSON
**Filename:** `doctor_[Doctor_Name]_v2.json`

**Sample Output:**
```json
{
  "profile_url": "https://www.marham.pk/doctors/...",
  "name": "Dr. Syed Najmul Hassan",
  "speciality": "Orthopedic Surgeon",
  "qualifications": "MBBS, FCPS (Orthopedic Surgery)",
  "pmdc_verified": true,
  "reviews_count": "7",
  "experience": "13 Yrs",
  "satisfaction": "100%",
  "wait_time": "6 mins",
  "avg_time_to_patient": "7 mins",
  "patient_satisfaction_rating": "5/5",
  "phone": "03111222398",
  "hospitals": [
    {
      "name": "Care+ Medical Center",
      "area": "G-8 Markaz",
      "city": "Islamabad",
      "address": "G-8 Markaz, Islamabad",
      "fee": "Rs. 2000",
      "timings": [
        {"day": "Mon", "time": "05:00 PM - 09:00 PM"},
        {"day": "Tue", "time": "05:00 PM - 09:00 PM"},
        {"day": "Wed", "time": "05:00 PM - 09:00 PM"},
        {"day": "Thu", "time": "05:00 PM - 09:00 PM"},
        {"day": "Fri", "time": "05:00 PM - 09:00 PM"}
      ]
    }
  ],
  "video_consultation_fee": "Rs. 1000",
  "video_consultation_timings": [
    {"day": "Mon", "time": "10:00 AM - 10:00 PM"}
  ],
  "services": [
    "Fracture Treatment",
    "Joint Replacement Surgery",
    "Sports Medicine"
  ],
  "professional_statement": "Dr. Syed Najmul Hassan practices through Marham.pk..."
}
```

### 2. Reviews JSON
**Filename:** `reviews_[Doctor_Name]_v2.json`

**Sample Output:**
```json
{
  "doctor_url": "https://www.marham.pk/doctors/...",
  "total_reviews_shown": 5,
  "reviews": [
    {
      "patient_name": "M.b",
      "rating": "N/A",
      "review_text": "The overall follow up check up was satisfactory by the doctor. Highly recommended.",
      "date": "09/04/2022",
      "tags": [
        "10 min wait time",
        "Great Experience",
        "Good PA / Staff",
        "Good Clinic",
        "20 min meetup"
      ]
    }
  ],
  "llm_summary": "Based on the provided patient reviews, overall patient satisfaction is high...",
  "basic_summary": "Showing 5 reviews with average rating: 4.5/5"
}
```

## 🔄 Complete Pipeline/Workflow

### Phase 1: Query Processing
```
User Input Query
      ↓
Extract Components (Specialty, Area, City)
      ↓
Validate Query Format
```

### Phase 2: URL Discovery
```
Multi-Provider Web Search
      ↓
Extract Marham.pk URLs
      ↓
Filter Listing Pages (exclude individual profiles)
      ↓
Validate URLs (check specialty, city, area)
      ↓
Rank URLs by Relevance
      ↓
Auto-Select Best Match
```

### Phase 3: Doctor Listing Extraction
```
Fetch Listing Page HTML
      ↓
Parse Doctor Cards
      ↓
Extract Basic Info (name, specialty, qualifications, reviews, experience)
      ↓
Extract Hospital Data (name, city, address, fee)
      ↓
Display Doctor List
```

### Phase 4: Profile Extraction
```
User Selects Doctor
      ↓
Fetch Doctor Profile Page
      ↓
Parse Profile Sections:
  ├─ Basic Info (name, specialty, qualifications, PMDC)
  ├─ Stats (reviews, experience, satisfaction, wait time)
  ├─ Hospital Sections (name, address, fee, timings)
  ├─ Video Consultation (fee, timings)
  ├─ Services (medical procedures offered)
  └─ Professional Statement
      ↓
Merge Card Data + Profile Data
      ↓
Save to JSON File
```

### Phase 5: Review Extraction (Optional)
```
User Opts for Reviews
      ↓
Fetch Profile Page (Reviews Section)
      ↓
Parse Review Blocks:
  ├─ Patient Name & Date
  ├─ Review Text
  └─ Tags (wait time, experience, satisfaction)
      ↓
Filter Invalid Reviews
      ↓
Generate LLM Summary (Groq API)
      ↓
Save to JSON File
```

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUT QUERY                        │
│              "gynecologist in model town lahore"            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              QUERY PARSER (extract_query_info)              │
│  Extracts: specialty="gynecologist", area="model town",     │
│            city="lahore"                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│     WEB SEARCH (search_marham_links_via_search_engine)      │
│  Providers: DuckDuckGo HTML, DuckDuckGo Lite, Bing         │
│  Output: List of Marham.pk listing URLs                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        URL VALIDATION & RANKING (validate_url)              │
│  - Check specialty/city/area presence                       │
│  - Verify doctor indicators                                 │
│  - Rank by relevance score                                  │
│  Output: Ranked list of valid URLs                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          AUTO-SELECT BEST URL (highest ranked)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    LISTING PAGE SCRAPING (search_doctors)                   │
│  - Fetch listing page HTML                                  │
│  - Extract doctor cards                                     │
│  - Parse card info (_extract_doctor_urls)                   │
│  Output: List of doctor objects with basic info             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              USER SELECTS DOCTOR                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    PROFILE PAGE SCRAPING (get_doctor_details)               │
│  - Fetch doctor profile page                                │
│  - Parse profile sections (_parse_doctor_profile):          │
│    ├─ Basic info (name, specialty, qualifications)          │
│    ├─ Statistics (reviews, experience, ratings)             │
│    ├─ Hospital sections (with _parse_hospital_timings)      │
│    ├─ Video consultation                                    │
│    ├─ Services & professional statement                     │
│  Output: Complete doctor profile dict                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         MERGE DATA (Card + Profile)                         │
│  Combine information from both sources                      │
│  Priority: Profile data > Card data                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         SAVE DOCTOR JSON FILE                               │
│  Filename: doctor_[Name]_v2.json                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         OPTIONAL: REVIEWS EXTRACTION                        │
│  User choice: View reviews? (yes/no)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ (if yes)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      REVIEWS SCRAPING (get_reviews)                         │
│  - Fetch profile page (reviews section)                     │
│  - Parse review blocks (_parse_reviews)                     │
│  - Extract: name, date, text, tags                          │
│  - Filter invalid reviews                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│   LLM SUMMARY GENERATION (_generate_llm_review_summary)     │
│  - Send reviews to Groq API                                 │
│  - Generate intelligent summary                             │
│  - Analyze sentiment & key points                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         SAVE REVIEWS JSON FILE                              │
│  Filename: reviews_[Name]_v2.json                           │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ File Structure

### ✅ FINAL FILES TO KEEP

#### Primary Files (Essential)
```
marham_crawler2.py          ← MAIN SCRAPER FILE (Latest version with hospital timings)
requirements.txt            ← Python dependencies
README.md                   ← This documentation
```

#### Configuration Files
```
.gitignore                  ← Git ignore rules
```

#### Output Files (Generated during runtime)
```
doctor_[Name]_v2.json       ← Doctor profile data
reviews_[Name]_v2.json      ← Reviews data
```

### ⚠️ FILES TO DELETE (Older versions)

```
❌ marham_crawler.py        ← OLD VERSION (missing hospital timings)
❌ doctor9.py               ← Backup/old version
❌ doctor9_backup.py        ← Backup file
❌ marham_scraper.py        ← Old scraper
❌ test_scraper.py          ← Test file
❌ test_duckduckgo.py       ← Test file
❌ debug_html.py            ← Debug/test file
❌ test_profile_structure.py ← Test file
❌ marham_doctors.json      ← Old output format
❌ oladoc_doctors.json      ← Different website
❌ doctor_Dr._Farrah_Tariq.json      ← Old output (without _v2)
❌ reviews_Dr._Farrah_Tariq.json     ← Old output (without _v2)
❌ doctor_Dr._Adil_Saidullah.json    ← Old output (without _v2)
❌ reviews_Dr._Adil_Saidullah.json   ← Old output (without _v2)
```

### 📁 Recommended Project Structure

```
Scrapping-doctors-info/
│
├── marham_crawler2.py              # Main scraper (KEEP)
├── requirements.txt                # Dependencies (KEEP)
├── README.md                       # Documentation (KEEP)
├── .gitignore                      # Git ignore (KEEP)
│
├── venv/                           # Virtual environment (DON'T COMMIT)
│
├── output/                         # Output directory (optional)
│   ├── doctor_*.json              # Generated doctor files
│   └── reviews_*.json             # Generated review files
│
└── docs/                           # Documentation (optional)
    ├── IMPLEMENTATION_STATUS.md   # Implementation details
    ├── PROFILE_STRUCTURE_UPDATE.md # HTML structure analysis
    ├── UPDATES_SUMMARY.md         # Update changelog
    └── CODE_VERIFICATION_REPORT.md # Verification report
```

## 🔧 Key Functions Reference

### Main Functions

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `extract_query_info()` | Parse user query | Query string | Dict with specialty, area, city |
| `search_marham_links_via_search_engine()` | Web search for URLs | Query string | List of Marham URLs |
| `validate_url()` | Validate URL relevance | URL, specialty, area, city | Boolean |
| `_rank_listing_url()` | Rank URL by relevance | URL, query components | Integer score |
| `search_doctors()` | Extract doctor cards | Listing URL | List of doctor dicts |
| `get_doctor_details()` | Get full profile | Profile URL | Complete doctor dict |
| `_parse_doctor_profile()` | Parse profile HTML | HTML, URL | Doctor dict |
| `_parse_hospital_timings()` | Extract timings | HTML section | List of timing dicts |
| `get_reviews()` | Fetch reviews | Profile URL, count | Reviews dict |
| `_parse_reviews()` | Parse reviews HTML | HTML, count | List of review dicts |
| `_generate_llm_review_summary()` | Generate AI summary | Reviews list | Summary string |

### Helper Functions

| Function | Purpose |
|----------|---------|
| `_format_area_slug()` | Format area name for URL |
| `_extract_doctor_urls()` | Extract doctor cards from listing |
| `_create_basic_summary()` | Create basic review stats |

## 🐛 Troubleshooting

### Common Issues

#### 1. No Search Results Found
**Problem:** "❌ No Marham links found via search engine."

**Solutions:**
- Check internet connection
- Try broader query (e.g., remove area, keep only city)
- Manually paste a Marham.pk listing URL when prompted
- Wait a few minutes and retry (rate limiting)

#### 2. Empty Hospitals Array
**Problem:** Hospitals field is `[]` in output JSON

**Possible Causes:**
- Hospital data loaded via JavaScript (not in static HTML)
- Different HTML structure on some profiles
- `data-hospital` attributes missing

**Solution:** The code uses multiple extraction methods, but some profiles may not have hospital data in accessible format.

#### 3. API Key Errors
**Problem:** "❌ Error generating LLM summary"

**Solutions:**
- Verify Groq API key is valid
- Check API rate limits
- Get new API key from [Groq Console](https://console.groq.com/)

#### 4. Crawl4AI Installation Issues
**Problem:** Installation fails for crawl4ai

**Solutions:**
```bash
pip install --upgrade pip
pip install crawl4ai==0.7.4
```

### Debug Mode

To enable verbose logging, the crawler already uses `verbose=True` for profile fetching. Check terminal output for detailed information.

## 📊 Performance & Limitations

### Performance Metrics
- Average query time: 10-20 seconds
- Listing page extraction: 2-5 seconds
- Profile page extraction: 2-4 seconds
- Review extraction + LLM summary: 3-5 seconds
- Total time per doctor (with reviews): ~20-30 seconds

### Rate Limiting
- Search engines may rate limit after 20-30 searches
- Marham.pk has no strict rate limiting
- Groq API: Free tier allows sufficient requests

### Known Limitations
1. **Dynamic Content:** Some data may load via JavaScript
2. **Hospital Data:** Not all profiles have complete hospital info
3. **Phone Numbers:** May extract Marham helpline instead of doctor's direct number
4. **Reviews:** Limited to visible reviews (no pagination support)
5. **Search Dependency:** Relies on external search engines

## 🔒 Best Practices

### 1. Responsible Scraping
- Don't run excessive concurrent requests
- Respect robots.txt
- Add delays between requests if scraping multiple doctors
- Don't use for commercial purposes without permission

### 2. Data Usage
- Verify critical information with official sources
- Contact information should be used responsibly
- Patient reviews are public information but should be handled sensitively

### 3. Code Maintenance
- Keep crawl4ai updated: `pip install --upgrade crawl4ai`
- Monitor for HTML structure changes on Marham.pk
- Test regularly with different queries

## 📝 Example Use Cases

### 1. Healthcare Directory
Build a local database of doctors with specialties, locations, and availability.

### 2. Appointment Booking System
Integrate extracted data into appointment booking platforms.

### 3. Healthcare Analytics
Analyze doctor distribution, specialties, and patient satisfaction across cities.

### 4. Telemedicine Integration
Use video consultation data for online consultation platforms.

### 5. Patient Decision Support
Help patients find doctors based on location, ratings, and availability.

## 🤝 Contributing

### Reporting Issues
Create an issue on GitHub with:
- Query used
- Error message
- Expected vs actual behavior
- Output files (if any)

### Feature Requests
Suggestions for improvements:
- Additional data fields
- New websites to scrape
- Export formats (CSV, Excel)
- GUI interface

## 📜 License

This project is for educational purposes. Please respect Marham.pk's terms of service and use responsibly.

## 👨‍💻 Author

**Abdul Haseeb**
- GitHub: [@AbdulHaseeb598](https://github.com/AbdulHaseeb598)
- Repository: [Scrapping-doctors-info](https://github.com/AbdulHaseeb598/Scrapping-doctors-info)

## 🎓 Project Context

Developed as part of CUI Internship project for web scraping and data extraction.

## 📅 Version History

### v2.0 (October 24, 2025) - Current
- ✅ Added hospital address extraction
- ✅ Added weekly schedule/timings extraction
- ✅ Added video consultation timings
- ✅ Enhanced hospital section parsing
- ✅ Fixed all extraction patterns
- ✅ Verified output with real data

### v1.0 (Previous)
- Basic doctor profile extraction
- Review extraction with LLM summary
- Search engine integration

## 🔗 Related Documentation

- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Profile Structure Analysis](PROFILE_STRUCTURE_UPDATE.md)
- [Updates Summary](UPDATES_SUMMARY.md)
- [Code Verification Report](CODE_VERIFICATION_REPORT.md)

---

## ⚡ Quick Start

```bash
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install crawl4ai httpx groq pydantic

# 2. Run
python marham_crawler2.py

# 3. Enter query
🔍 Enter your search query: cardiologist in dha karachi

# 4. Select doctor from list
👉 Enter the number of the doctor (or 0 to exit): 1

# 5. View reviews (optional)
👉 View reviews with LLM summary? (yes/no): yes
```

---

**🎉 You're all set! Start scraping doctor information from Marham.pk with complete hospital addresses and weekly schedules!**

For questions or issues, please open an issue on GitHub.
