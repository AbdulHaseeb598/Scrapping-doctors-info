import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Optional

from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it in the .env file.")

print("API key loaded successfully!")  # Optional check


class DoctorInfo(BaseModel):
    name: str = Field(description="Doctor's full name")
    speciality: str = Field(description="Doctor's specialization/specialty")
    hospital_name: str = Field(description="Hospital or clinic name")
    location: str = Field(description="Location/address of the hospital")
    address: str = Field(description="Complete address")
    experience: Optional[str] = Field(description="Years of experience")
    fee: Optional[str] = Field(description="Consultation fee")
    available_times: Optional[List[str]] = Field(description="Available time slots")
    profile_url: str = Field(description="Doctor's profile URL")

class ReviewInfo(BaseModel):
    patient_name: str = Field(description="Name of the patient who gave the review")
    rating: str = Field(description="Rating given by the patient")
    review_text: str = Field(description="Review text/comment")
    date: Optional[str] = Field(description="Date of the review")

class MarhamScraper:
    def __init__(self):
        self.base_url = "https://marham.pk"
        self.groq_client = Groq(api_key=GROQ_API_KEY)
    
    def extract_query_info(self, query: str) -> dict:
        """Extract specialty, area, and city from user query"""
        query_lower = query.lower().strip()
        
        # Extract city (common Pakistani cities)
        cities = ['karachi', 'lahore', 'islamabad', 'rawalpindi', 'faisalabad', 'multan', 
                  'peshawar', 'quetta', 'sialkot', 'gujranwala', 'hyderabad', 'bahawalpur']
        
        city = None
        for c in cities:
            if c in query_lower:
                city = c
                break
        
        # Extract area (text between 'in' and city name)
        area = None
        if city:
            area_pattern = rf'\bin\s+([a-z0-9\s-]+?)\s+{city}'
            area_match = re.search(area_pattern, query_lower)
            if area_match:
                area = area_match.group(1).strip()
        
        # Extract specialty (text before 'in')
        specialty = None
        specialty_match = re.search(r'^([a-z]+(?:ologist|logist|ist)?)\s+in', query_lower)
        if specialty_match:
            specialty = specialty_match.group(1).strip()
        else:
            words = query_lower.split()
            if words:
                specialty = words[0]
        
        print(f"🎯 Extracted from query: '{query}'")
        print(f"   Specialty: {specialty}")
        print(f"   Area: {area if area else 'Not specified'}")
        print(f"   City: {city}")
        
        return {
            "specialty": specialty,
            "area": area,
            "city": city,
            "original_query": query
        }
    
    async def validate_url(self, url: str, specialty: str, area: str, city: str) -> bool:
        """Validate if the URL contains relevant doctor data matching the query"""
        print(f"\n🔍 Validating URL: {url}")
        
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    bypass_cache=True,
                    page_timeout=15000
                )
                
                if not result.success:
                    print(f"   ❌ Failed to fetch URL (HTTP error)")
                    return False
                
                content = result.markdown.lower()[:5000]
                
                if '/profile/' in url.lower() or url.lower().endswith('/dr/'):
                    print(f"   ❌ Skipped (Profile/Home page)")
                    return False
                
                specialty_found = specialty.lower() in content if specialty else True
                city_found = city.lower() in content if city else True
                area_found = True
                if area:
                    area_variations = [area.lower(), area.lower().replace(' ', '-'), area.lower().replace('-', ' ')]
                    area_found = any(var in content for var in area_variations)
                
                doctor_indicators = ['dr.', 'doctor', 'mbbs', 'fcps', 'experience', 'reviews', 'rating']
                indicator_count = sum(1 for ind in doctor_indicators if ind in content)
                has_doctors = indicator_count >= 2
                
                is_valid = specialty_found and city_found and has_doctors
                
                if is_valid:
                    print(f"   ✅ Valid URL (Specialty: {specialty_found}, City: {city_found}, Area: {area_found}, Doctors: {has_doctors})")
                else:
                    print(f"   ❌ Invalid URL (Specialty: {specialty_found}, City: {city_found}, Doctors: {has_doctors})")
                
                return is_valid
                
        except Exception as e:
            print(f"   ⚠️ Error validating URL: {e}")
            return False
    
    def _format_area_slug(self, area: str) -> str:
        """Format area name for Marham.pk URL structure"""
        if not area:
            return ""
        
        area_lower = area.lower().strip()
        
        sector_match = re.match(r'^([a-z])[-\s]?(\d+)$', area_lower)
        if sector_match:
            letter = sector_match.group(1)
            number = sector_match.group(2)
            return f"{letter}-{number}-markaz"
        
        return area_lower.replace(' ', '-')
    
    async def search_marham_links_via_search_engine(self, query: str, max_results: int = 8) -> list:
        """Search the web for relevant Marham.pk links using multiple providers"""
        import httpx
        from urllib.parse import urlparse, parse_qs, unquote

        def decode_duckduckgo_redirect(u: str) -> str:
            if u.startswith("//"):
                u = "https:" + u
            try:
                pu = urlparse(u)
                if "duckduckgo.com" in pu.netloc and pu.path.startswith("/l/"):
                    qs = parse_qs(pu.query)
                    if "uddg" in qs and qs["uddg"]:
                        real = unquote(qs["uddg"][0])
                        return real
            except Exception:
                pass
            return u

        def filter_marham_urls(candidates: list) -> list:
            allowed = []
            seen = set()
            for raw in candidates:
                url = decode_duckduckgo_redirect(raw)
                url = url.split('#')[0].split('?')[0].strip()
                if not url:
                    continue
                try:
                    parsed = urlparse(url)
                except Exception:
                    continue
                if "marham.pk" not in parsed.netloc:
                    continue
                
                if "/doctors/" in url:
                    if "/dr-" in url or "/prof-" in url or "/asst-prof" in url:
                        continue
                    
                    if url.lower() in seen:
                        continue
                    seen.add(url.lower())
                    allowed.append(url)
                        
            return allowed

        async def fetch(url: str, headers: dict) -> str:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                return resp.text

        print(f"\n🌐 Searching the web for: {query}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Cache-Control": "no-cache",
        }

        providers = [
            (
                f"https://duckduckgo.com/html/?q=site:marham.pk+{query.replace(' ', '+')}",
                [
                    r'<a[^>]+class="result__a"[^>]*href="([^"]+)"',
                    r'href="(https?://[^\"]*marham\.pk[^\"]*)"',
                ],
                "DuckDuckGo HTML",
            ),
            (
                f"https://lite.duckduckgo.com/lite/?q=site:marham.pk+{query.replace(' ', '+')}",
                [r'href="(https?://[^\"]*marham\.pk[^\"]*)"'],
                "DuckDuckGo Lite",
            ),
            (
                f"https://www.bing.com/search?q=site%3Amarham.pk+{query.replace(' ', '+')}",
                [r'href="(https?://[^\"]*marham\.pk[^\"]*)"'],
                "Bing",
            ),
        ]

        aggregated = []
        for url, patterns, label in providers:
            try:
                print(f"   🔎 Provider: {label}")
                html = await fetch(url, headers)
                found = []
                for pat in patterns:
                    matches = re.findall(pat, html, flags=re.IGNORECASE)
                    if matches:
                        found.extend(matches)
                print(f"      • Raw matches: {len(found)}")
                filtered = filter_marham_urls(found)
                print(f"      • Filtered marham links: {len(filtered)}")
                aggregated.extend(filtered)
                if len(aggregated) >= max_results:
                    break
            except Exception as e:
                print(f"      • Provider error: {e}")

        dedup = []
        seen = set()
        for u in aggregated:
            if u not in seen:
                seen.add(u)
                dedup.append(u)
            if len(dedup) >= max_results:
                break

        print(f"   ✅ Total unique marham links: {len(dedup)}")
        return dedup
    
    def _rank_listing_url(self, url: str, specialty: str, area: str, city: str) -> int:
        """Rank a listing URL based on how well it matches the query"""
        score = 0
        url_lower = url.lower()
        
        if specialty and specialty.lower() in url_lower:
            score += 100
        if city and city.lower() in url_lower:
            score += 50
        if area and area.lower().replace(' ', '-') in url_lower:
            score += 200
        
        if '/area-' in url_lower:
            score += 150
        
        path_parts = url_lower.split('/')
        if len(path_parts) == 6:
            score += 50
        
        return score
    
    async def search_doctors_by_query(self, query_info: dict) -> list:
        """Use search engine to find relevant Marham URLs"""
        query = query_info.get('original_query', '')
        marham_links = await self.search_marham_links_via_search_engine(query)
        if not marham_links:
            print("❌ No Marham links found via search engine.")
            return []

        specialty = query_info.get('specialty', '')
        area = query_info.get('area', '')
        city = query_info.get('city', '')
        valid_links = []
        for url in marham_links:
            is_valid = await self.validate_url(url, specialty, area, city)
            if is_valid:
                valid_links.append(url)
        
        if not valid_links:
            print("❌ No valid Marham links found after validation.")
            return []
        
        ranked_links = []
        for url in valid_links:
            score = self._rank_listing_url(url, specialty, area, city)
            ranked_links.append((url, score))
        
        ranked_links.sort(key=lambda x: x[1], reverse=True)
        sorted_urls = [url for url, score in ranked_links]
        
        print(f"\n✅ {len(sorted_urls)} relevant Marham links found (ranked by relevance):")
        for i, link in enumerate(sorted_urls, 1):
            print(f"   {i}. {link}")
        
        return sorted_urls
    
    async def search_doctors(self, search_url: str) -> List[dict]:
        """Search for doctors on marham.pk using the provided URL"""
        print(f"\n📡 Fetching doctors from: {search_url}")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=search_url,
                word_count_threshold=10,
                bypass_cache=True,
                wait_for="css:a[href*='/doctors/'], css:.doctor-card, css:.list-data",
                page_timeout=30000,
                delay_before_return_html=3.0
            )
            
            if result.success:
                print(f"   ✅ Page loaded successfully")
                print(f"   HTML size: {len(result.html)} chars")
                doctor_urls = self._extract_doctor_urls(result.markdown, result.html)
                return doctor_urls
            else:
                print(f"❌ Failed to fetch search results: {result.error_message}")
                return []
    
    def _extract_doctor_urls(self, markdown_content: str, html_content: str) -> List[dict]:
        """Extract doctor card information from search results"""
        doctors = []
        
        print(f"\n🔎 Extracting doctor cards from page...")
        
        card_pattern = r'<div class="row shadow-card">(.*?)</div>\s*</div>\s*</div>'
        cards = re.findall(card_pattern, html_content, re.DOTALL)
        
        print(f"   Found {len(cards)} doctor cards")
        
        for i, card_html in enumerate(cards[:20], 1):
            try:
                doctor_info = {
                    "id": i,
                    "name": "",
                    "speciality": "",
                    "qualifications": "",
                    "pmdc_verified": False,
                    "reviews": "",
                    "experience": "",
                    "satisfaction": "",
                    "profile_url": "",
                    "hospitals": [],
                    "areas_of_interest": []
                }
                
                name_pattern = r'<a href="(https://www\.marham\.pk/doctors/[^"]+)"[^>]*class="text-blue dr_profile_opened_from_listing"[^>]*>.*?<h3[^>]*>(.*?)</h3>'
                name_match = re.search(name_pattern, card_html, re.DOTALL)
                if name_match:
                    doctor_info['profile_url'] = name_match.group(1).strip()
                    doctor_info['name'] = re.sub(r'<[^>]+>', '', name_match.group(2)).strip()
                
                if 'PMDC Verified' in card_html:
                    doctor_info['pmdc_verified'] = True
                
                speciality_pattern = r'<p class="mb-0 mt-10 text-sm">([^<]+)</p>'
                speciality_match = re.search(speciality_pattern, card_html)
                if speciality_match:
                    doctor_info['speciality'] = speciality_match.group(1).strip()
                
                qual_pattern = r'<p class="text-sm">([^<]+)</p>'
                qual_match = re.search(qual_pattern, card_html)
                if qual_match:
                    doctor_info['qualifications'] = qual_match.group(1).strip()
                
                reviews_pattern = r'<p class="text-bold text-sm text-golden">\s*<i[^>]*></i>\s*(\d+)\s*</p>'
                reviews_match = re.search(reviews_pattern, card_html)
                if reviews_match:
                    doctor_info['reviews'] = reviews_match.group(1).strip()
                
                exp_pattern = r'<p class="mb-0 text-sm">Experience</p>\s*<p class="text-bold text-sm">([^<]+)</p>'
                exp_match = re.search(exp_pattern, card_html, re.DOTALL)
                if exp_match:
                    doctor_info['experience'] = exp_match.group(1).strip()
                
                sat_pattern = r'<p class="mb-0 text-sm">Satisfaction</p>\s*<p class="text-bold text-sm">([^<]+)</p>'
                sat_match = re.search(sat_pattern, card_html, re.DOTALL)
                if sat_match:
                    doctor_info['satisfaction'] = sat_match.group(1).strip()
                
                interest_pattern = r'<span class="chips-highlight[^"]*"[^>]*>([^<]+)</span>'
                interests = re.findall(interest_pattern, card_html)
                doctor_info['areas_of_interest'] = [interest.strip() for interest in interests]
                
                hospital_pattern = r'data-hospitalname="([^"]+)"[^>]*data-hospitalcity="([^"]+)"[^>]*data-hospitaladdress="([^"]+)"[^>]*data-amount="([^"]+)"'
                hospitals = re.findall(hospital_pattern, card_html)
                for hosp in hospitals:
                    hospital_name, city, address, fee = hosp
                    if hospital_name != "Video Consultation":
                        doctor_info['hospitals'].append({
                            "name": hospital_name,
                            "city": city,
                            "address": address,
                            "fee": f"Rs. {fee}"
                        })
                
                doctor_info['display_name'] = doctor_info['name']
                
                doctors.append(doctor_info)
                
            except Exception as e:
                print(f"   ⚠️ Error parsing card {i}: {e}")
                continue
        
        print(f"   ✅ Extracted {len(doctors)} doctors with full details")
        
        return doctors
    
    async def get_doctor_details(self, profile_url: str) -> dict:
        """Get detailed information about a specific doctor including hospital addresses and timings"""
        print(f"\nFetching doctor details from: {profile_url}")
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=profile_url,
                word_count_threshold=10,
                bypass_cache=True,
                page_timeout=30000,
                delay_before_return_html=2.0
            )
            
            if result.success:
                doctor_data = self._parse_doctor_profile(result.markdown, result.html, profile_url)
                return doctor_data
            else:
                print(f"Failed to fetch doctor profile: {result.error_message}")
                return None
    
    def _parse_hospital_timings(self, html_section: str) -> List[dict]:
        """Extract weekly schedule from hospital timing tables"""
        timings = []
        
        # Find all table rows with timing information
        # Pattern: <tr class="text-sm"><td class="text-bold text-blue">Mon</td><td>10:00 AM - 02:00 PM</td></tr>
        day_patterns = r'<tr[^>]*class="text-sm"[^>]*>\s*<td[^>]*class="text-bold text-blue"[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*</tr>'
        day_matches = re.findall(day_patterns, html_section, re.IGNORECASE | re.DOTALL)
        
        for day, time_slot in day_matches:
            timings.append({
                "day": day.strip(),
                "time": time_slot.strip()
            })
        
        return timings
    
    def _parse_doctor_profile(self, markdown: str, html: str, url: str) -> dict:
        """Parse doctor profile with ENHANCED hospital and timing extraction"""
        doctor_info = {
            "profile_url": url,
            "name": "",
            "speciality": "",
            "qualifications": "",
            "pmdc_verified": False,
            "reviews_count": "",
            "experience": "",
            "satisfaction": "",
            "wait_time": "",
            "avg_time_to_patient": "",
            "patient_satisfaction_rating": "",
            "hospitals": [],
            "areas_of_interest": [],
            "phone": "",
            "video_consultation_fee": "",
            "video_consultation_timings": [],
            "languages": [],
            "services": [],
            "professional_statement": ""
        }
        
        # Extract basic fields (name, speciality, qualifications, etc.) - same as before
        name_patterns = [
            r'<h1[^>]*class="mb-0"[^>]*>(?:Dr\.\s*|Prof\.\s*|Asst\.\s*Prof\.\s*)?([^<]+)</h1>',
            r'<h1[^>]*>(?:Dr\.\s*|Prof\.\s*)?([^<]+)</h1>',
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, html)
            if name_match:
                doctor_info['name'] = name_match.group(1).strip()
                break
        
        if re.search(r'PMDC\s+Verified', html, re.IGNORECASE):
            doctor_info['pmdc_verified'] = True
        
        spec_patterns = [
            r'<strong[^>]*class="text-sm"[^>]*>([^<]+(?:ologist|logist|Specialist|Surgeon|Physician))</strong>',
            r'<p[^>]*class="mt-10"[^>]*><strong[^>]*>([^<]+)</strong>',
        ]
        for pattern in spec_patterns:
            spec_match = re.search(pattern, html[:50000], re.IGNORECASE)
            if spec_match:
                doctor_info['speciality'] = spec_match.group(1).strip()
                break
        
        qual_patterns = [
            r'<p[^>]*class="text-sm mb-0"[^>]*>([^<]*(?:MBBS|FCPS|MCPS|MD|MS|FRCS|MRCP)[^<]*)</p>',
            r'<p[^>]*class="text-sm"[^>]*>([^<]*(?:MBBS|FCPS|MCPS|MD|MS)[^<]*)</p>',
        ]
        for pattern in qual_patterns:
            qual_match = re.search(pattern, html[:50000])
            if qual_match:
                qual_text = qual_match.group(1).strip()
                if any(deg in qual_text.upper() for deg in ['MBBS', 'FCPS', 'MD', 'MS', 'MCPS']):
                    doctor_info['qualifications'] = re.sub(r'&amp;', '&', qual_text)
                    break
        
        reviews_patterns = [
            r'<i[^>]*fa-thumbs-up[^>]*></i>\s*(\d+)',
            r'<h2[^>]*>\s*(\d+)\s+Reviews',
        ]
        for pattern in reviews_patterns:
            reviews_match = re.search(pattern, html, re.IGNORECASE)
            if reviews_match:
                doctor_info['reviews_count'] = reviews_match.group(1).strip()
                break
        
        exp_patterns = [
            r'<p class="mb-0 text-sm">(?:\d+\s*Yrs?\s+)?Experience</p>\s*<p class="text-bold text-sm">(\d+\s*Yrs?)</p>',
            r'(\d+\s*Yrs?)\s+Experience',
        ]
        for pattern in exp_patterns:
            exp_match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if exp_match:
                doctor_info['experience'] = exp_match.group(1).strip()
                break
        
        wait_patterns = [
            r'<p[^>]*class="mb-0 text-sm"[^>]*>Wait Time</p>\s*<p[^>]*class="text-bold"[^>]*>([^<]+)</p>',
        ]
        for pattern in wait_patterns:
            wait_match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if wait_match:
                doctor_info['wait_time'] = wait_match.group(1).strip()
                break
        
        avg_time_patterns = [
            r'<p[^>]*class="mb-0 text-sm"[^>]*>Avg\.\s+Time\s+to\s+Patient</p>\s*<p[^>]*class="text-bold"[^>]*>([^<]+)</p>',
        ]
        for pattern in avg_time_patterns:
            avg_match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if avg_match:
                doctor_info['avg_time_to_patient'] = avg_match.group(1).strip()
                break
        
        rating_pattern = r'<div[^>]*class="col-2[^"]*text-right[^"]*"[^>]*>(\d+\.?\d*/5)</div>'
        rating_match = re.search(rating_pattern, html, re.IGNORECASE)
        if rating_match:
            doctor_info['patient_satisfaction_rating'] = rating_match.group(1).strip()
        
        # ==================== ENHANCED HOSPITAL & ADDRESS EXTRACTION ====================
        
        # Method 1: Extract from data-hospital attributes (works for buttons/links)
        hospital_pattern = r'data-hospitalname="([^"]+)"[^>]*data-hospitalcity="([^"]+)"[^>]*data-hospitaladdress="([^"]+)"[^>]*data-amount="([^"]+)"'
        hospitals_data = re.findall(hospital_pattern, html)
        seen_hospitals = {}
        
        for hosp in hospitals_data:
            hospital_name, city, address, fee = hosp
            if hospital_name == "Video Consultation":
                fee_clean = re.sub(r'[,\s]+', '', fee).strip()
                if not doctor_info['video_consultation_fee']:
                    doctor_info['video_consultation_fee'] = f"Rs. {fee_clean}" if fee_clean else ""
            else:
                fee_clean = re.sub(r'[,\s]+', '', fee).strip()
                hosp_key = hospital_name.lower().strip()
                if hosp_key not in seen_hospitals:
                    seen_hospitals[hosp_key] = {
                        "name": hospital_name,
                        "city": city,
                        "address": address,
                        "fee": f"Rs. {fee_clean}" if fee_clean else "",
                        "timings": []
                    }
        
        # Method 2: Extract from Practice Address sections with <h3 class="text-bold text-underline">
        # This method extracts hospital name, area/city, fee, AND TIMINGS
        
        # Find all hospital sections (each starts with <h3 class="text-bold text-underline">Hospital Name</h3>)
        hospital_sections = re.split(r'<h3[^>]*class="text-bold text-underline"[^>]*>', html)
        
        for section in hospital_sections[1:]:  # Skip first split (before first h3)
            # Extract hospital name (first content before </h3>)
            name_match = re.search(r'^([^<]+)</h3>', section)
            if not name_match:
                continue
            
            hospital_name = name_match.group(1).strip()
            
            # Skip if it's "Video Consultation"
            if "video" in hospital_name.lower() or "online" in hospital_name.lower():
                # Extract video consultation fee and timings
                fee_match = re.search(r'<p[^>]*>Rs\.\s*([0-9,]+)', section)
                if fee_match and not doctor_info['video_consultation_fee']:
                    fee_clean = re.sub(r'[,\s]+', '', fee_match.group(1))
                    doctor_info['video_consultation_fee'] = f"Rs. {fee_clean}"
                
                # Extract video consultation timings
                doctor_info['video_consultation_timings'] = self._parse_hospital_timings(section)
                continue
            
            # Extract area/city from "Area: Location, City" pattern
            area_city = ""
            area_match = re.search(r'<p[^>]*>Area:\s*([^<]+)</p>', section, re.IGNORECASE)
            if area_match:
                area_city = area_match.group(1).strip()
            
            # Extract fee
            fee_match = re.search(r'<p[^>]*>Rs\.\s*([0-9,]+)', section)
            fee = ""
            if fee_match:
                fee_value = re.sub(r'[,\s]+', '', fee_match.group(1))
                fee = "Rs. " + fee_value
            
            # Extract timings from table
            timings = self._parse_hospital_timings(section)
            
            # Parse area and city from "Area, City" format
            area = ""
            city = ""
            if area_city:
                area_parts = area_city.split(',')
                area = area_parts[0].strip() if area_parts else area_city
                city = area_parts[1].strip() if len(area_parts) > 1 else ""
            
            # Add or update hospital info
            hosp_key = hospital_name.lower().strip()
            if hosp_key in seen_hospitals:
                # Update existing entry with additional info
                if area and not seen_hospitals[hosp_key].get('area'):
                    seen_hospitals[hosp_key]['area'] = area
                if city and not seen_hospitals[hosp_key].get('city'):
                    seen_hospitals[hosp_key]['city'] = city
                if timings:
                    seen_hospitals[hosp_key]['timings'] = timings
            else:
                # Create new entry
                seen_hospitals[hosp_key] = {
                    "name": hospital_name,
                    "area": area,
                    "city": city,
                    "address": area_city if area_city else "",
                    "fee": fee,
                    "timings": timings
                }
        
        # Convert dict to list
        doctor_info['hospitals'] = list(seen_hospitals.values())
        
        # ==================== END HOSPITAL EXTRACTION ====================
        
        # Extract phone number
        phone_patterns = [
            r'href="tel:(\d{11})"',
            r'(0?3\d{2}[- ]?\d{7})',
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, html, re.IGNORECASE)
            if phone_match:
                phone = phone_match.group(1).strip()
                phone = re.sub(r'[^\d]', '', phone)
                if len(phone) >= 10 and not doctor_info['phone']:
                    doctor_info['phone'] = phone
                    break
        
        # Extract services
        services_section = re.search(r'<h2[^>]*>Services</h2>(.*?)</section>', html, re.DOTALL | re.IGNORECASE)
        if services_section:
            service_links = re.findall(r'<a[^>]*>([^<]+)</a>', services_section.group(1))
            doctor_info['services'] = [s.strip() for s in service_links if len(s.strip()) > 3 and not s.strip().lower().startswith('http')]
        
        # Extract professional statement
        statement_pattern = r'<h2[^>]*>Professional Statement[^<]*</h2>\s*<div[^>]*>\s*<p[^>]*>(.*?)</p>'
        statement_match = re.search(statement_pattern, html, re.DOTALL | re.IGNORECASE)
        if statement_match:
            statement_text = statement_match.group(1)
            statement_text = re.sub(r'<[^>]+>', ' ', statement_text)
            statement_text = re.sub(r'\s+', ' ', statement_text).strip()
            if len(statement_text) > 50:
                doctor_info['professional_statement'] = statement_text[:500]
        
        # Extract areas of interest
        interest_pattern = r'<span class="chips-highlight[^"]*"[^>]*>([^<]+)</span>'
        interests = re.findall(interest_pattern, html)
        doctor_info['areas_of_interest'] = [interest.strip() for interest in interests if len(interest.strip()) > 2]
        
        return doctor_info
    
    async def get_reviews(self, profile_url: str, num_reviews: int = 5) -> dict:
        """Get reviews summary for a doctor"""
        print(f"\n💬 Fetching reviews from: {profile_url}")
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=profile_url,
                word_count_threshold=10,
                bypass_cache=True
            )
            
            if result.success:
                reviews = self._parse_reviews(result.markdown, result.html, num_reviews)
                llm_summary = self._generate_llm_review_summary(reviews)
                
                summary = {
                    "doctor_url": profile_url,
                    "total_reviews_shown": len(reviews),
                    "reviews": reviews,
                    "llm_summary": llm_summary,
                    "basic_summary": self._create_basic_summary(reviews)
                }
                
                return summary
            else:
                print(f"❌ Failed to fetch reviews: {result.error_message}")
                return None
    
    def _generate_llm_review_summary(self, reviews: List[dict]) -> str:
        """Use Groq LLM to generate intelligent summary of reviews"""
        if not reviews or len(reviews) == 0:
            return "No reviews available for summary."
        
        reviews_text = "\n\n".join([
            f"Review {i+1}:\nRating: {r.get('rating', 'N/A')}\nPatient: {r.get('patient_name', 'Anonymous')}\nComment: {r.get('review_text', 'No comment')}"
            for i, r in enumerate(reviews)
        ])
        
        prompt = f"""You are a medical review analyst. Analyze the following patient reviews for a doctor and provide a comprehensive summary in 3-4 sentences.

Focus on:
1. Overall patient satisfaction
2. Common positive points (if any)
3. Common concerns or negative points (if any)
4. Doctor's strengths based on reviews

Reviews:
{reviews_text}

Provide a balanced, professional summary:"""

        try:
            print("🤖 Generating LLM-based review summary...")
            
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful medical review analyst who provides concise, balanced summaries of patient reviews."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                top_p=1,
                stream=False,
                stop=None
            )
            
            summary = completion.choices[0].message.content.strip()
            print("✅ LLM summary generated successfully")
            return summary
            
        except Exception as e:
            print(f"⚠️ Error generating LLM summary: {e}")
            return f"Error generating summary. Showing {len(reviews)} reviews with basic analysis."
    
    def _create_basic_summary(self, reviews: List[dict]) -> str:
        """Create a basic statistical summary of reviews"""
        if not reviews:
            return "No reviews available"
        
        total = len(reviews)
        has_ratings = [r for r in reviews if r.get('rating') and r['rating'] != 'N/A']
        
        if has_ratings:
            try:
                ratings = [float(r['rating']) for r in has_ratings if str(r['rating']).replace('.', '').isdigit()]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    return f"Showing {total} reviews with average rating: {avg_rating:.1f}/5"
            except:
                pass
        
        return f"Showing {total} reviews"
    
    def _parse_reviews(self, markdown: str, html: str, num_reviews: int) -> List[dict]:
        """Parse reviews from the page content"""
        reviews = []
        
        reviews_section_match = None
        reviews_section_match = re.search(r'<section[^>]*id="reviews-scroll"[^>]*>(.*?)</section>', html, re.DOTALL | re.IGNORECASE)
        if not reviews_section_match:
            reviews_section_match = re.search(r'<div[^>]*id="reviews"[^>]*>(.*?)</div>\s*</section>', html, re.DOTALL | re.IGNORECASE)
        if not reviews_section_match:
            reviews_section_match = re.search(r'<h2[^>]*>\s*\d+\s+Reviews[^<]*</h2>(.*?)(?:<hr|</section>|$)', html, re.DOTALL | re.IGNORECASE)

        review_blocks = []
        if reviews_section_match:
            reviews_html = reviews_section_match.group(1)
            row_iter = list(re.finditer(r'<div[^>]*class="[^"]*row\s+border-card[^"]*"[^>]*>', reviews_html, re.IGNORECASE))
            if row_iter:
                for idx, m in enumerate(row_iter):
                    start = m.start()
                    end = row_iter[idx + 1].start() if idx + 1 < len(row_iter) else len(reviews_html)
                    block = reviews_html[start:end]
                    review_blocks.append(block)
            else:
                parts = re.split(r'<hr[^>]*class="mt-10 mb-10"[^>]*>', reviews_html)
                for part in parts:
                    if 'fa-thumbs-up' in part or 'chips-list' in part or 'border-card' in part:
                        review_blocks.append(part)
        
        if review_blocks:
            for i, block in enumerate(review_blocks[:num_reviews], 1):
                review = {
                    "patient_name": "Anonymous",
                    "rating": "N/A",
                    "review_text": "",
                    "date": "",
                    "tags": []
                }

                name_span = re.search(r'<span[^>]*class="[^"]*text-bold\s+text-sm\s+text-grey[^"]*"[^>]*>([^<]+)</span>', block, re.IGNORECASE)
                if name_span:
                    name_text = re.sub(r'\s+', ' ', name_span.group(1)).strip()
                    parts = re.split(r'\s*[-–—]\s*', name_text, maxsplit=1)
                    if len(parts) == 2:
                        review['patient_name'] = parts[0].strip()
                        review['date'] = parts[1].strip()
                    else:
                        review['patient_name'] = name_text

                p_texts = re.findall(r'<p[^>]*>(.*?)</p>', block, re.DOTALL | re.IGNORECASE)
                comment = ''
                for p_html in p_texts:
                    p_clean = re.sub(r'<[^>]+>', ' ', p_html)
                    p_clean = re.sub(r'\s+', ' ', p_clean).strip()
                    if len(p_clean) < 15:
                        continue
                    lower = p_clean.lower()
                    if 'i am satisfied with the doctor' in lower or 'i am satisfied' in lower:
                        continue
                    comment = p_clean
                    break
                if not comment and p_texts:
                    longest = ''
                    for p_html in p_texts:
                        p_clean = re.sub(r'<[^>]+>', ' ', p_html)
                        p_clean = re.sub(r'\s+', ' ', p_clean).strip()
                        if len(p_clean) > len(longest):
                            longest = p_clean
                    comment = longest

                review['review_text'] = comment if comment else 'Review content not available'

                chips_match = re.search(r'<ul[^>]*class="[^"]*chips-list[^"]*"[^>]*>(.*?)</ul>', block, re.DOTALL | re.IGNORECASE)
                if chips_match:
                    lis = re.findall(r'<li[^>]*>(.*?)</li>', chips_match.group(1), re.DOTALL | re.IGNORECASE)
                    for li in lis:
                        li_text = re.sub(r'<[^>]+>', ' ', li)
                        li_text = re.sub(r'\s+', ' ', li_text).strip()
                        if li_text:
                            review['tags'].append(li_text)

                exclude_keywords = ['copyright', 'marham inc', 'calling marham', 'terms', 'privacy',
                                    'what is dr', 'has the following degrees', 'all rights reserved']
                is_valid_review = True
                if review['review_text']:
                    review_lower = review['review_text'].lower()
                    if any(keyword in review_lower for keyword in exclude_keywords):
                        is_valid_review = False
                    if len(review['review_text'].strip()) < 15:
                        is_valid_review = False

                if is_valid_review:
                    reviews.append(review)

                if len(reviews) >= num_reviews:
                    break
        
        if len(reviews) < num_reviews:
            sample_count = num_reviews - len(reviews)
            for i in range(sample_count):
                reviews.append({
                    "patient_name": "Anonymous",
                    "rating": "N/A",
                    "review_text": "Review content not available",
                    "date": "",
                    "tags": []
                })
        
        return reviews[:num_reviews]

async def main():
    scraper = MarhamScraper()
    
    print("=" * 70)
    print("🏥 MARHAM.PK DOCTOR SCRAPER V2 - WITH HOSPITAL ADDRESS & TIMINGS")
    print("=" * 70)
    
    print("\n📝 Examples of queries:")
    print("   - 'dermatologist in i8 islamabad'")
    print("   - 'cardiologist in model town lahore'")
    print("   - 'gynecologist in dha karachi'\n")
    
    query = input("🔍 Enter your search query: ").strip()
    
    if not query:
        print("❌ Query cannot be empty!")
        return
    
    query_info = scraper.extract_query_info(query)
    marham_links = await scraper.search_doctors_by_query(query_info)
    
    if not marham_links:
        print("\n❌ Could not find any relevant Marham links for your query.")
        manual = input("Paste a Marham URL to proceed (or press Enter to exit): ").strip()
        if manual and manual.startswith("http") and "marham.pk" in manual:
            marham_links = [manual]
        else:
            print("Exiting.")
            return

    print(f"\n{'='*70}")
    print("🔗 RELEVANT MARHAM LISTING PAGES:")
    print(f"{'='*70}")
    for i, link in enumerate(marham_links, 1):
        print(f"{i}. {link}")
    
    selected_listing_url = marham_links[0]
    print(f"\n Auto-selected: {selected_listing_url}")

    print(f"\n{'='*70}")
    print("EXTRACTING DOCTOR PROFILES...")
    print(f"{'='*70}")
    doctor_cards = await scraper.search_doctors(selected_listing_url)
    
    if not doctor_cards:
        print(" No doctors found!")
        return
    
    print(f"\n{'='*70}")
    print(f" FOUND {len(doctor_cards)} DOCTORS:")
    print(f"{'='*70}")
    for doctor in doctor_cards:
        print(f"\n{doctor['id']}. {doctor['name']}")
        print(f"   Speciality: {doctor['speciality']}")
        print(f"   Experience: {doctor['experience']}")
        print(f"   Reviews: {doctor['reviews']}")
        if doctor['pmdc_verified']:
            print(f"   ✅ PMDC Verified")

    try:
        doctor_choice = int(input("\n👉 Enter the number of the doctor (or 0 to exit): "))
        if doctor_choice == 0:
            print(" Goodbye!")
            return
        if doctor_choice < 1 or doctor_choice > len(doctor_cards):
            print("❌ Invalid choice!")
            return
        selected_doctor = doctor_cards[doctor_choice - 1]
    except ValueError:
        print("❌ Invalid input!")
        return

    print(f"\n{'='*70}")
    print("📄 FETCHING FULL DOCTOR DETAILS...")
    print(f"{'='*70}")
    
    doctor_details = {
        "profile_url": selected_doctor['profile_url'],
        "name": selected_doctor['name'],
        "speciality": selected_doctor['speciality'],
        "qualifications": selected_doctor['qualifications'],
        "pmdc_verified": selected_doctor['pmdc_verified'],
        "reviews_count": selected_doctor['reviews'],
        "experience": selected_doctor['experience'],
        "satisfaction": selected_doctor['satisfaction'],
        "hospitals": selected_doctor['hospitals'],
        "areas_of_interest": selected_doctor['areas_of_interest'],
        "phone": "",
        "video_consultation_fee": "",
        "video_consultation_timings": [],
        "wait_time": "",
        "avg_time_to_patient": "",
        "patient_satisfaction_rating": "",
        "languages": [],
        "services": [],
        "professional_statement": ""
    }
    
    profile_data = await scraper.get_doctor_details(selected_doctor['profile_url'])
    if profile_data:
        # Merge all fields
        for key in profile_data:
            if key == 'hospitals':
                # Replace with profile hospitals (more detailed)
                doctor_details['hospitals'] = profile_data['hospitals']
            elif not doctor_details.get(key) or doctor_details[key] in ['', [], {}]:
                doctor_details[key] = profile_data[key]
    
    print("\n" + "=" * 70)
    print(" DOCTOR INFORMATION")
    print("=" * 70)
    print(json.dumps(doctor_details, indent=2, ensure_ascii=False))
    
    filename = f"doctor_{doctor_details.get('name', 'unknown').replace(' ', '_')}_v2.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(doctor_details, f, indent=2, ensure_ascii=False)
    print(f"\n Doctor details saved to: {filename}")
    
    # Print hospital details in readable format
    if doctor_details.get('hospitals'):
        print(f"\n{'='*70}")
        print("HOSPITAL DETAILS WITH TIMINGS:")
        print(f"{'='*70}")
        for idx, hosp in enumerate(doctor_details['hospitals'], 1):
            print(f"\n{idx}. {hosp.get('name', 'N/A')}")
            print(f"   Address: {hosp.get('address', 'N/A')}")
            print(f"   Area: {hosp.get('area', 'N/A')}")
            print(f"   City: {hosp.get('city', 'N/A')}")
            print(f"   Fee: {hosp.get('fee', 'N/A')}")
            if hosp.get('timings'):
                print(f"   Weekly Schedule:")
                for timing in hosp['timings']:
                    print(f"      {timing['day']}: {timing['time']}")
    
    if doctor_details.get('video_consultation_fee'):
        print(f"\n Video Consultation: {doctor_details['video_consultation_fee']}")
        if doctor_details.get('video_consultation_timings'):
            print("   Timings:")
            for timing in doctor_details['video_consultation_timings']:
                print(f"      {timing['day']}: {timing['time']}")
    
    see_reviews = input("\n View reviews with LLM summary? (yes/no): ").strip().lower()
    if see_reviews in ['yes', 'y']:
        print("\n" + "=" * 70)
        print(" FETCHING REVIEWS...")
        print("=" * 70)
        reviews_data = await scraper.get_reviews(selected_doctor['profile_url'], num_reviews=5)
        
        if reviews_data:
            print("\n" + "=" * 70)
            print(" REVIEWS SUMMARY")
            print("=" * 70)
            print("\n AI Summary:")
            print("-" * 70)
            print(reviews_data.get('llm_summary', 'No summary available'))
            print("-" * 70)
            
            print(f"\n {reviews_data.get('basic_summary', '')}")
            
            reviews_filename = f"reviews_{doctor_details.get('name', 'unknown').replace(' ', '_')}_v2.json"
            with open(reviews_filename, 'w', encoding='utf-8') as f:
                json.dump(reviews_data, f, indent=2, ensure_ascii=False)
            print(f"\n Reviews saved to: {reviews_filename}")

if __name__ == "__main__":
    asyncio.run(main())
