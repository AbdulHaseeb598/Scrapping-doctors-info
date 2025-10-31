# scrape_doctors_playwright_final_full_fixed.py
import asyncio
import csv
import os
import random
import time
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, BrowserContext, Page, ElementHandle

# ---------------- CONFIG ----------------
OUTPUT_CSV = "doctors_knowledge_base.csv"
HEADLESS = False          # False for first run (handle Cloudflare)
CITY_LIMIT: Optional[int] = None
DELAY_MIN, DELAY_MAX = 0.8, 2.0
MAX_PAGES_PER_CITY = 8
# ----------------------------------------

CSV_COLUMNS = [
    "city", "name", "specialization", "qualification", "experience",
    "satisfaction_rate", "reviews", "areas_of_interest", "consultation_type",
    "hospital_name", "hospital_address", "hospital_city", "complete address",
    "availability_schedule", "fee", "profile_url", "image_url", "raw_source_url"
]


def rnd_sleep():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


# ---------- CSV helpers ----------
def append_rows(rows: List[Dict], filename: str = OUTPUT_CSV):
    if not rows:
        return
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        for r in rows:
            out = {k: (r.get(k) if r.get(k) is not None else "") for k in CSV_COLUMNS}
            writer.writerow(out)


def read_scraped_cities(filename: str = OUTPUT_CSV) -> set:
    if not os.path.isfile(filename):
        return set()
    s = set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c = row.get("city")
                if c:
                    s.add(c)
    except Exception:
        pass
    return s


# ---------------- Stealth ----------------
async def apply_stealth(page: Page):
    await page.add_init_script(
        """() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            window.chrome = window.chrome || { runtime: {} };
        }"""
    )


# ---------------- Utilities ----------------
def normalise_href(href: Optional[str], base: str = "https://www.marham.pk") -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return urljoin(base, href)
    if href.startswith("http"):
        return href
    return urljoin(base, href)


async def inner_text_safe(el: Optional[ElementHandle]) -> Optional[str]:
    if not el:
        return None
    try:
        t = await el.inner_text()
        return t.strip()
    except Exception:
        return None


# ---------------- Discover cities ----------------
async def discover_city_links(context: BrowserContext) -> List[Tuple[str, str]]:
    page = await context.new_page()
    await apply_stealth(page)
    await page.goto("https://www.marham.pk/doctors", wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2500)

    anchors = await page.query_selector_all("a[href*='/doctors/']")
    candidates = []
    for a in anchors:
        try:
            txt = (await a.inner_text() or "").strip()
            href = await a.get_attribute("href")
            if not href or not txt:
                continue
            href = normalise_href(href)
            path = urlparse(href).path.lstrip("/").rstrip("/")
            if path.startswith("doctors/") and path.count("/") == 1:
                if re.search(r'\d', txt):
                    continue
                candidates.append((txt, href))
        except Exception:
            continue

    await page.close()
    unique = list({(c, u) for c, u in candidates})
    unique.sort(key=lambda x: x[0].lower())
    return unique


# ---------------- Profile availability ----------------
async def extract_availability_from_profile(context: BrowserContext, profile_url: str) -> Optional[Dict[str, str]]:
    page = None
    try:
        page = await context.new_page()
        await apply_stealth(page)
        await page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(1200)

        blocks = await page.query_selector_all("section.p-xy .shadow-card, section.p-xy div.shadow-card")
        schedules: Dict[str, str] = {}
        for b in blocks:
            title_el = await b.query_selector("h3")
            title = (await inner_text_safe(title_el) or "").strip()
            if not title:
                continue
            rows = await b.query_selector_all("table tr")
            weekly = []
            for tr in rows:
                cols = await tr.query_selector_all("td")
                if len(cols) >= 2:
                    day = (await inner_text_safe(cols[0]) or "").strip()
                    hours = (await inner_text_safe(cols[1]) or "").strip()
                    if day and hours:
                        weekly.append(f"{day}: {hours}")
            if weekly:
                schedules[title] = "; ".join(weekly)
        await page.close()
        return schedules if schedules else None
    except Exception:
        try:
            if page:
                await page.close()
        except Exception:
            pass
        return None


def match_schedule_for_hospital(hospital_name: str, schedules: Optional[Dict[str, str]]) -> Optional[str]:
    if not schedules or not hospital_name:
        return None
    lname = hospital_name.lower()
    for t, s in schedules.items():
        tt = t.lower()
        if tt == lname or tt in lname or lname in tt:
            return s
    h_tokens = set(re.findall(r"[a-z0-9]+", hospital_name.lower()))
    best, best_score = None, 0
    for t in schedules:
        t_tokens = set(re.findall(r"[a-z0-9]+", t.lower()))
        score = len(h_tokens & t_tokens)
        if score > best_score:
            best_score = score
            best = t
    return schedules.get(best) if best else None


# ----------- Metric parsing helpers -----------
def is_reviews_candidate(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    if re.search(r'yr|year', s, re.I) or '%' in s:
        return False
    m = re.search(r'(\d{1,3}(?:,\d{3})*)', s)
    if m and not re.search(r'[A-Za-z]', s):
        return True
    return False


def classify_line_for_metric(line: str) -> Optional[Tuple[str, str]]:
    if not line:
        return None
    s = line.strip()
    if re.search(r'(\d+\s*(?:yrs?|years?|yr))', s, re.I):
        return ("experience", re.search(r'(\d+\s*(?:yrs?|years?|yr))', s, re.I).group(1).strip())
    if re.search(r'(\d{1,3}\s*%)', s):
        return ("satisfaction_rate", re.search(r'(\d{1,3}\s*%)', s).group(1).strip())
    if is_reviews_candidate(s):
        m = re.search(r'(\d{1,3}(?:,\d{3})*)', s)
        return ("reviews", m.group(1).strip()) if m else ("reviews", s)
    return None


# -------------- Label parsing --------------
async def extract_label_values(card: ElementHandle) -> Dict[str, str]:
    mapping: Dict[str, str] = {}

    # --- extract experience/satisfaction/reviews ---
    metric_blocks = await card.query_selector_all("div.row > div.col-4, div.col-4")
    for m in metric_blocks:
        txt = (await inner_text_safe(m) or "").strip()
        if not txt:
            continue
        lines = [ln.strip() for ln in re.split(r'\r?\n', txt) if ln.strip()]
        if len(lines) >= 2:
            value = lines[1]
            cls = classify_line_for_metric(value)
            if cls:
                mapping[cls[0]] = cls[1]
        else:
            cl = classify_line_for_metric(lines[0])
            if cl:
                mapping[cl[0]] = cl[1]

    # --- FIX: regex cleanup for misaligned experience/reviews ---
    if "reviews" in mapping:
        rev_val = mapping["reviews"].strip()
        if re.search(r"\b\d+\s*(?:yrs?|years?)\b", rev_val, re.I):
            mapping.pop("reviews", None)
            mapping["experience"] = re.search(r"\b\d+\s*(?:yrs?|years?)\b", rev_val, re.I).group(0)
        elif re.search(r"\b\d{1,3}\s*%", rev_val):
            mapping.pop("reviews", None)
            mapping["satisfaction_rate"] = re.search(r"\b\d{1,3}\s*%", rev_val).group(0)
        elif re.search(r"[A-Za-z]", rev_val) and not re.match(r"^\d+(?:,\d{3})*$", rev_val):
            mapping.pop("reviews", None)
    if "reviews" in mapping:
        val = mapping["reviews"]
        if not re.match(r"^\d{1,3}(?:,\d{3})*$", val.strip()):
            mapping.pop("reviews", None)

    # --- extract specialization and qualification robustly ---
    specialization = ""
    qualification = ""

    # specialization (first p tag after name)
    spec_el = await card.query_selector("p.mb-0.mt-10.text-sm, p.mb-0.text-sm")
    if not spec_el:
        spec_el = await card.query_selector("div.col-9.col-md-10 p.text-sm")
    if spec_el:
        specialization = (await inner_text_safe(spec_el) or "").strip()

    # qualification (next text-sm after specialization)
    qual_els = await card.query_selector_all("p.text-sm")
    if len(qual_els) >= 2:
        # typically the 2nd text-sm element is qualification
        qualification = (await inner_text_safe(qual_els[1]) or "").strip()
    elif len(qual_els) == 1 and not specialization:
        # fallback: sometimes only one element contains both
        qualification = (await inner_text_safe(qual_els[0]) or "").strip()

    if specialization:
        mapping["specialization"] = specialization
    if qualification:
        mapping["qualification"] = qualification

    return mapping

    mapping: Dict[str, str] = {}
    metric_blocks = await card.query_selector_all("div.row > div.col-4, div.col-4")
    for m in metric_blocks:
        txt = (await inner_text_safe(m) or "").strip()
        if not txt:
            continue
        lines = [ln.strip() for ln in re.split(r'\r?\n', txt) if ln.strip()]
        if len(lines) >= 2:
            label = lines[0].lower()
            value = lines[1]
            cls = classify_line_for_metric(value)
            if cls:
                mapping[cls[0]] = cls[1]
        else:
            cl = classify_line_for_metric(lines[0])
            if cl:
                mapping[cl[0]] = cl[1]

    # --- FIX: regex-driven cleanup (correct alignment) ---
    if "reviews" in mapping:
        rev_val = mapping["reviews"].strip()
        if re.search(r"\b\d+\s*(?:yrs?|years?)\b", rev_val, re.I):
            mapping.pop("reviews", None)
            mapping["experience"] = re.search(r"\b\d+\s*(?:yrs?|years?)\b", rev_val, re.I).group(0)
        elif re.search(r"\b\d{1,3}\s*%", rev_val):
            mapping.pop("reviews", None)
            mapping["satisfaction_rate"] = re.search(r"\b\d{1,3}\s*%", rev_val).group(0)
        elif re.search(r"[A-Za-z]", rev_val) and not re.match(r"^\d+(?:,\d{3})*$", rev_val):
            mapping.pop("reviews", None)
    if "reviews" in mapping:
        val = mapping["reviews"]
        if not re.match(r"^\d{1,3}(?:,\d{3})*$", val.strip()):
            mapping.pop("reviews", None)
    # ------------------------------------------------------

    return mapping


# ------------- Extract doctors -------------
async def extract_doctors_from_city_page(context: BrowserContext, city_name: str, city_url: str) -> List[Dict]:
    page = await context.new_page()
    await apply_stealth(page)
    try:
        await page.goto(city_url, wait_until="domcontentloaded", timeout=30000)
    except Exception:
        await page.close()
        return []

    try:
        await page.wait_for_selector("div.row.shadow-card", timeout=8000)
    except Exception:
        pass

    cards = await page.query_selector_all("div.row.shadow-card")
    results: List[Dict] = []
    profile_cache: Dict[str, Optional[Dict[str, str]]] = {}

    for card in cards:
        try:
            name = await inner_text_safe(await card.query_selector("h3")) or ""
            profile_anchor = await card.query_selector("a.dr_profile_opened_from_listing, a.text-blue, a.dr_profile_open_frm_listing_btn_vprofile")
            profile_href = await (profile_anchor.get_attribute("href") if profile_anchor else None)
            profile_href = normalise_href(profile_href) if profile_href else None

            img_src = None
            src_el = await card.query_selector("picture source[media*='min-width'], picture source")
            if src_el:
                img_src = await src_el.get_attribute("srcset")
            if not img_src:
                im = await card.query_selector("img.round-img")
                if im:
                    img_src = await im.get_attribute("src")

            label_map = await extract_label_values(card)
            specialization = label_map.get("specialization", "")
            qualification = label_map.get("qualification", "")
            experience = label_map.get("experience", "")
            reviews = label_map.get("reviews", "")
            satisfaction = label_map.get("satisfaction_rate", "")

            chips = await card.query_selector_all("span.chips-highlight, span.chips")
            areas = [await inner_text_safe(c) for c in chips]
            areas_of_interest = ", ".join([a for a in areas if a])

            product_cards = await card.query_selector_all("div.product-card, div.card-hospital, div.selectAppointmentOrOc")
            profile_timings = None
            if profile_href:
                if profile_href not in profile_cache:
                    profile_cache[profile_href] = await extract_availability_from_profile(context, profile_href)
                profile_timings = profile_cache.get(profile_href)

            for pc in product_cards:
                d_hospitalname = await pc.get_attribute("data-hospitalname")
                d_hospitalcity = await pc.get_attribute("data-hospitalcity")
                d_hospitaladdress = await pc.get_attribute("data-hospitaladdress")
                d_amount = await pc.get_attribute("data-amount")
                d_type = await pc.get_attribute("data-hospitaltype")

                hosp_name = (d_hospitalname or "").strip() or "Unknown"
                hosp_addr = (d_hospitaladdress or "").strip()
                hosp_city = (d_hospitalcity or "").strip() or city_name
                fee = (d_amount or "").strip()
                consult_type = "Hospital"
                if ("video" in hosp_name.lower()) or (d_type and d_type.strip() == "2"):
                    consult_type = "Video Consultation"

                avail_el = await pc.query_selector("p.text-sm.text-wrap, p.text-sm, p")
                avail_note = (await inner_text_safe(avail_el) or "").strip()
                schedule = match_schedule_for_hospital(hosp_name, profile_timings) if profile_timings else None

                row = {
                    "city": hosp_city, "name": name, "specialization": specialization,
                    "qualification": qualification, "experience": experience,
                    "satisfaction_rate": satisfaction, "reviews": reviews,
                    "areas_of_interest": areas_of_interest, "consultation_type": consult_type,
                    "hospital_name": hosp_name, "hospital_address": hosp_addr,
                    "hospital_city": hosp_city, "complete address": avail_note,
                    "availability_schedule": schedule or "", "fee": fee,
                    "profile_url": profile_href or "", "image_url": img_src or "",
                    "raw_source_url": city_url
                }
                results.append(row)
        except Exception as e:
            print(f"[card parse error] {e}")
            continue

    await page.close()
    return results


# ---------- Pagination ----------
async def scrape_city_with_pagination(context: BrowserContext, city_name: str, city_url: str) -> List[Dict]:
    all_rows: List[Dict] = []
    current = city_url
    for _ in range(MAX_PAGES_PER_CITY):
        rows = await extract_doctors_from_city_page(context, city_name, current)
        if not rows:
            break
        all_rows.extend(rows)
        temp = await context.new_page()
        await apply_stealth(temp)
        try:
            await temp.goto(current, wait_until="domcontentloaded", timeout=20000)
            next_el = await temp.query_selector("a[rel='next'], a.next, li.next a")
            if not next_el:
                await temp.close()
                break
            href = await next_el.get_attribute("href")
            if not href:
                await temp.close()
                break
            next_href = normalise_href(href)
            if not next_href or next_href == current:
                await temp.close()
                break
            current = next_href
            await temp.close()
            rnd_sleep()
        except Exception:
            await temp.close()
            break
    return all_rows


# ---------- Main ----------
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(viewport={"width": 1200, "height": 900})

        cities = await discover_city_links(context)
        if not cities:
            print("No cities discovered — run with HEADLESS=False to bypass Cloudflare.")
            await browser.close()
            return

        if CITY_LIMIT:
            cities = cities[:CITY_LIMIT]

        scraped = read_scraped_cities()
        print(f"Discovered {len(cities)} cities; already scraped {len(scraped)}.")

        total_saved = 0
        for cname, curl in cities:
            if cname in scraped:
                print(f"Skipping already scraped: {cname}")
                continue
            print(f"\n=== Processing {cname} ===")
            try:
                rows = await scrape_city_with_pagination(context, cname, curl)
                if rows:
                    append_rows(rows)
                    total_saved += len(rows)
                    print(f"Saved {len(rows)} rows for {cname}")
                else:
                    print(f"No rows for {cname}")
            except Exception as e:
                print(f"Failed {cname}: {e}")
            rnd_sleep()

        await browser.close()
        print(f"\n✅ Done. Total saved this run: {total_saved}. File: {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
