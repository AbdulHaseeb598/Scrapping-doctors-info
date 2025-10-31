
## 📋 COMPLETE WORKFLOW PIPELINE

### **Step 1: Setup Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Run Scraper**
```bash
python marham_crawler2.py
```

### **Step 3: Input Query**
```
Example queries:
- gynecologist in model town lahore
- cardiologist in dha karachi
- dermatologist in i8 islamabad
- orthopedic in g8 markaz islamabad
```

### **Step 4: Automated Processing**
1. **Query Parsing**
   - Extracts specialty, area, city from query
   
2. **Web Search**
   - Searches DuckDuckGo & Bing for Marham.pk URLs
   - Validates URLs by relevance
   - Ranks URLs by specialty/area/city match
   - Auto-selects best URL
   
3. **Doctor Listing Extraction**
   - Fetches listing page
   - Extracts all doctor cards
   - Displays numbered list with basic info
   
4. **Doctor Selection**
   - User selects doctor number
   
5. **Profile Extraction**
   - Fetches complete profile page
   - Extracts all fields:
     ✓ Name, specialty, qualifications
     ✓ PMDC verification, experience, ratings
     ✓ Hospital names, addresses, fees
     ✓ Weekly timings (Mon-Sun schedules)
     ✓ Video consultation details
     ✓ Services & professional statement
   - Saves to `doctor_[Name]_v2.json`
   
6. **Review Extraction (Optional)**
   - User chooses yes/no for reviews
   - Extracts patient reviews
   - Generates AI summary using Groq LLM
   - Saves to `reviews_[Name]_v2.json`

---

## 📊 DATA FLOW DIAGRAM

```
USER INPUT
   ↓
[Query Parser]
   ↓
Extract: specialty, area, city
   ↓
[Web Search Engine]
   ↓
Multiple providers: DuckDuckGo, Bing
   ↓
Extract Marham URLs
   ↓
[URL Validator]
   ↓
Filter listing pages only
Validate specialty/city/area
   ↓
[URL Ranker]
   ↓
Score each URL by relevance
Auto-select highest score
   ↓
[Listing Page Scraper]
   ↓
Fetch HTML with Crawl4AI
Parse doctor cards
Extract basic info
   ↓
DISPLAY DOCTOR LIST
   ↓
USER SELECTS DOCTOR
   ↓
[Profile Page Scraper]
   ↓
Fetch profile HTML
Parse sections:
  • Basic info
  • Statistics
  • Hospital sections
    └─ Parse timings table
  • Video consultation
  • Services
  • Professional statement
   ↓
Merge card + profile data
   ↓
SAVE: doctor_[Name]_v2.json
   ↓
OPTIONAL: VIEW REVIEWS?
   ↓ (yes)
[Review Scraper]
   ↓
Parse review blocks
Extract: name, date, text, tags
   ↓
[LLM Summary Generator]
   ↓
Send to Groq API
Generate intelligent summary
   ↓
SAVE: reviews_[Name]_v2.json
   ↓
COMPLETE ✅
```

---

## 🔄 EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────┐
│  START: python marham_crawler2.py                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  INPUT: "gynecologist in model town lahore"                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  PARSE QUERY                                                │
│  specialty = "gynecologist"                                 │
│  area = "model town"                                        │
│  city = "lahore"                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  WEB SEARCH                                                 │
│  Query: "site:marham.pk gynecologist model town lahore"     │
│  Providers: DuckDuckGo HTML → DuckDuckGo Lite → Bing       │
│  Result: 3 Marham URLs found                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  VALIDATE & RANK URLs                                       │
│  URL 1: /doctors/lahore/gynecologist/area-model-town       │
│  Score: 3 (specialty✓ city✓ area✓)                         │
│  Auto-selected as best match                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FETCH LISTING PAGE                                         │
│  Crawl4AI: verbose=True, word_count_threshold=10            │
│  Extract doctor cards from HTML                             │
│  Result: 15 doctors found                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY DOCTORS                                            │
│  1. Dr. Aisha Khan - Gynecologist - MBBS, FCPS - 15 Yrs    │
│  2. Dr. Sara Ahmed - Gynecologist - MBBS, MCPS - 10 Yrs    │
│  3. Dr. Fatima Ali - Gynecologist - MBBS, FCPS - 8 Yrs     │
│  ...                                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  USER SELECTS: 1                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FETCH PROFILE PAGE                                         │
│  URL: /doctors/lahore/gynecologist/dr-aisha-khan-12345     │
│  Crawl4AI: Extract full HTML                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  PARSE PROFILE SECTIONS                                     │
│  • Basic: Name, specialty, qualifications, PMDC             │
│  • Stats: Reviews, experience, satisfaction, wait time      │
│  • Hospitals: Loop through practice address sections        │
│    - Extract hospital name                                  │
│    - Parse "Area: Location, City" → split area & city       │
│    - Extract fee from "Rs. Amount"                          │
│    - Parse timings table:                                   │
│      <tr><td>Mon</td><td>09:00 AM - 05:00 PM</td></tr>     │
│      → {day: "Mon", time: "09:00 AM - 05:00 PM"}           │
│  • Video: Fee & timings                                     │
│  • Services: List of medical procedures                     │
│  • Statement: Professional bio                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  MERGE DATA                                                 │
│  Combine card data + profile data                           │
│  Priority: profile data overrides card data                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  SAVE JSON                                                  │
│  File: doctor_Dr._Aisha_Khan_v2.json                        │
│  Content:                                                   │
│  {                                                          │
│    "name": "Dr. Aisha Khan",                                │
│    "speciality": "Gynecologist",                            │
│    "hospitals": [                                           │
│      {                                                      │
│        "name": "XYZ Hospital",                              │
│        "address": "Model Town, Lahore",                     │
│        "fee": "Rs. 2500",                                   │
│        "timings": [                                         │
│          {"day": "Mon", "time": "09:00 AM - 05:00 PM"},    │
│          {"day": "Tue", "time": "09:00 AM - 05:00 PM"},    │
│          ...                                                │
│        ]                                                    │
│      }                                                      │
│    ],                                                       │
│    ...                                                      │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  PROMPT: View reviews? (yes/no)                             │
└────────────────────────┬────────────────────────────────────┘
                         │ (yes)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FETCH REVIEWS                                              │
│  Parse review section from profile page                     │
│  Extract each review block:                                 │
│  • Patient name (initials)                                  │
│  • Date                                                     │
│  • Review text                                              │
│  • Tags (wait time, experience, satisfaction)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  GENERATE LLM SUMMARY                                       │
│  API: Groq (llama-3.3-70b-versatile)                        │
│  Prompt: "Analyze these patient reviews..."                 │
│  Output: Intelligent summary with insights                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  SAVE REVIEWS JSON                                          │
│  File: reviews_Dr._Aisha_Khan_v2.json                       │
│  Content:                                                   │
│  {                                                          │
│    "total_reviews_shown": 10,                               │
│    "reviews": [...],                                        │
│    "llm_summary": "Dr. Aisha Khan receives consistently...",│
│    "basic_summary": "Showing 10 reviews..."                 │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  COMPLETE ✅                                                 │
│  Output files created successfully                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 KEY FEATURES IMPLEMENTED

### ✅ Version 2.0 Enhancements (Current)
- [x] Hospital name extraction
- [x] Complete address parsing (Area + City)
- [x] Weekly timing schedules (day-wise)
- [x] Video consultation timings
- [x] Services list extraction
- [x] Professional statement
- [x] Enhanced error handling
- [x] Multiple extraction methods for robustness

### ✅ Version 1.0 Features (Previous)
- [x] Natural language query processing
- [x] Multi-provider web search
- [x] Doctor listing extraction
- [x] Profile information extraction
- [x] Patient reviews extraction
- [x] AI-powered review summaries
- [x] JSON output format

---

## 📁 RECOMMENDED DIRECTORY STRUCTURE

```
Scrapping-doctors-info/              ← Repository root
│
├── scrapping_doctors_by_Query.py               ← MAIN FILE (KEEP)
├── requirements.txt                 ← Dependencies (KEEP)
├── README.md                        ← Documentation (KEEP)
├── PROJECT_SUMMARY.md               ← This file (KEEP)
├── .gitignore                       ← Git ignore rules (KEEP)
│
├── venv/                            ← Virtual environment (DON'T COMMIT)
│   └── ...
│
├── output/                          ← Output directory (OPTIONAL)
│   ├── doctor_*.json               ← Generated profiles
│   └── reviews_*.json              ← Generated reviews
│
└── docs/                            ← Additional docs (OPTIONAL)
    ├── IMPLEMENTATION_STATUS.md
    ├── PROFILE_STRUCTURE_UPDATE.md
    └── UPDATES_SUMMARY.md
```

---

## 🔒 .gitignore RECOMMENDATIONS

```gitignore
# Virtual environment
venv/
env/
.venv/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Output files (optional - you may want to track these)
doctor_*.json
reviews_*.json
*.csv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Old files
*_backup.py
*_old.py
test_*.py
debug_*.py
```

---

## ⚡ QUICK REFERENCE

### Installation
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run
```bash
python marham_crawler2.py
```

### Query Format
```
[specialty] in [area] [city]
```

### Example Queries
```
gynecologist in model town lahore
cardiologist in dha karachi  
dermatologist in i8 islamabad
orthopedic in g8 markaz islamabad
endocrinologist in bahria town rawalpindi
```

### Output Files
```
doctor_[Name]_v2.json    ← Profile data
reviews_[Name]_v2.json   ← Reviews + AI summary
```

---

## 📊 PROJECT STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Query Parser | ✅ Complete | Extracts specialty, area, city |
| Web Search | ✅ Complete | Multi-provider with fallback |
| URL Validation | ✅ Complete | Ranks by relevance |
| Listing Scraper | ✅ Complete | Extracts doctor cards |
| Profile Scraper | ✅ Complete | All fields implemented |
| Hospital Parser | ✅ Complete | Address + timings working |
| Timings Parser | ✅ Complete | Weekly schedule extraction |
| Review Scraper | ✅ Complete | Reviews + tags |
| LLM Summary | ✅ Complete | Groq API integration |
| Error Handling | ✅ Complete | Comprehensive try-catch |
| Output Format | ✅ Complete | JSON with proper structure |

---

## 🏆 FINAL CHECKLIST

### Before Using
- [x] Virtual environment created
- [x] Dependencies installed (requirements.txt)
- [x] Groq API key configured (in code)
- [x] Internet connection active



### Verification
- [x] Tested with real query
- [x] Hospital addresses extracted
- [x] Weekly timings extracted
- [x] All fields populated
- [x] JSON output valid

---

## 📞 SUPPORT

For issues or questions:
1. Check README.md troubleshooting section
2. Verify query format matches examples
3. Check internet connection
4. Validate Groq API key
5. Open issue on GitHub with error details

---

**🎉 PROJECT COMPLETE & READY TO USE!**

All features implemented, tested, and documented.
Keep the final files and delete old versions to maintain a clean codebase.

---

*Last Updated: October 24, 2025*  
*Version: 2.0*  
*Status: Production Ready ✅*
