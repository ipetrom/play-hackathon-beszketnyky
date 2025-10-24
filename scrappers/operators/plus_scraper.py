# plus_prepaid_scraper.py
import asyncio, json, re, datetime
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

URL = "https://www.plus.pl/lp/telefon-na-karte"
PAGE_TIMEOUT_MS = 45000

NUM = r"(\d[\d\s]*)(?:[.,](\d{1,2}))?"

def _to_float(part: str, frac: Optional[str]) -> float:
    base = float(part.replace(" ", ""))
    return float(f"{int(base)}.{frac}") if frac else base

def parse_all_gb_per30(text: str) -> List[int]:
    return [int(m.group(1).replace(" ", "")) for m in re.finditer(rf"{NUM}\s*GB/30\s*dni", text, re.I)]

def parse_headline_total_gb(text: str) -> Optional[int]:
    """
    Find big 'XXXX GB' headline numbers (NOT '/30 dni' and NOT 'Roaming w UE').
    Handles broken layouts where digits are split by spaces/newlines.
    """
    cands: List[int] = []
    # match numbers followed by 'GB' but not 'GB/30 dni'
    for m in re.finditer(rf"{NUM}\s*GB(?!/30\s*dni)", text, re.I):
        # Skip if this occurrence is clearly part of the roaming line
        span = text[max(0, m.start()-30): m.end()+30]
        if re.search(r"Roaming w UE", span, re.I):
            continue
        # m.group(1) may contain spaces/newlines and even adjacent numbers
        # Extract all digit-only chunks and consider each separately
        for chunk in re.findall(r"\d+", m.group(1)):
            try:
                cands.append(int(chunk))
            except ValueError:
                continue
    return max(cands) if cands else None

def parse_roaming_gb(text: str) -> Optional[float]:
    m = re.search(rf"Roaming w UE\s*{NUM}\s*GB", text, re.I)
    return _to_float(m.group(1), m.group(2)) if m else None

def parse_unlimited_first_months(text: str) -> Optional[int]:
    m = re.search(r"Bez\s*Limitu\s*GB\s*przez\s*(\d+)\s*mies", text, re.I)
    return int(m.group(1)) if m else None

def parse_price_regular(text: str) -> Optional[float]:
    m = re.search(rf"{NUM}\s*zł\b(?![^\n]*pierwsze)", text, re.I)
    return _to_float(m.group(1), m.group(2)) if m else None

def parse_intro_promo(text: str):
    m = re.search(rf"{NUM}\s*zł\s*przez\s*pierwsze\s*(\d+)\s*mies", text, re.I)
    if not m: return None
    return {"price_pln": _to_float(m.group(1), m.group(2)), "months": int(m.group(3))}

def has_rollover(text: str) -> bool:
    return "kumulują" in text.lower()

def has_unlimited_calls(text: str) -> bool:
    return bool(re.search(r"Bez limitu:\s*rozmowy,\s*SMS i MMS", text, re.I))

def make_description(name: str, per30_gb: Optional[int], unlimited_first_m: Optional[int], price: Optional[float]) -> str:
    if unlimited_first_m:
        data_part = f"unlimited GB for {unlimited_first_m} months" + (f", then {per30_gb} GB/30 days" if per30_gb else "")
    else:
        data_part = f"{per30_gb} GB/30 days" if per30_gb else "data bundle"
    return f"Plus {name} prepaid — {data_part}" + (f", PLN {price}/30 days" if price is not None else "")

async def accept_cookies(page):
    # Try common patterns on page
    for pat in [r"(Akceptuj|Zgadzam|Zgoda|Accept|OK)"]:
        try:
            await page.get_by_role("button", name=re.compile(pat, re.I)).first.click(timeout=1500)
            return
        except Exception:
            pass
    # Try inside iframes (TCF-style CMP)
    for frame in page.frames:
        try:
            await frame.get_by_role("button", name=re.compile(r"(Akceptuj|Zgadzam|Accept|OK)", re.I)).first.click(timeout=1500)
            return
        except Exception:
            continue

async def autoscroll(page):
    # Trigger lazy content
    await page.evaluate("""
        async () => {
          const h = () => new Promise(r => requestAnimationFrame(r));
          for (let i=0;i<10;i++){
            window.scrollBy(0, Math.floor(window.innerHeight*0.9));
            await h();
          }
          window.scrollTo(0,0);
        }
    """)

async def get_cards(page):
    # Prefer exact tiles by heading AND local button
    cards = []
    for name in ["ULTRA", "PRO", "MAX", "CHILL"]:
        try:
            heading = page.get_by_text(re.compile(rf"\bPAKIET\s+{name}\b", re.I)).first
            await heading.wait_for(timeout=3000)
            card = heading.locator(
                "xpath=ancestor::section[.//button[contains(.,'Jak włączyć')]] | "
                "ancestor::div[.//button[contains(.,'Jak włączyć')]]"
            ).first
            await card.wait_for(timeout=2000)
            cards.append((name, card))
        except Exception:
            continue

    # Fallback: scan all sections that contain “PAKIET” and “GB/30 dni”
    if not cards:
        candidates = page.locator("section, div").filter(has_text=re.compile(r"PAKIET", re.I))
        count = await candidates.count()
        for i in range(count):
            c = candidates.nth(i)
            t = (await c.inner_text()).strip()
            if re.search(r"GB/30\s*dni", t, re.I):
                m = re.search(r"PAKIET\s+([A-ZĄĆĘŁŃÓŚŻŹ]+)", t, re.I)
                name = (m.group(1) if m else f"PKT{i}").upper()
                cards.append((name, c))
    return cards

async def scrape():
    out = {
        "source_url": URL,
        "scraped_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "currency": "PLN",
        "plans": [],
        "status": "ok"
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu","--no-sandbox","--disable-setuid-sandbox",
                "--disable-dev-shm-usage","--disable-background-networking",
            ],
        )
        ctx = await browser.new_context(
            java_script_enabled=True,
            locale="pl-PL",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )

        # Block heavy stuff but keep stylesheets & scripts
        async def blocker(route, request):
            if request.resource_type in {"image","media","font"}:
                return await route.abort()
            await route.continue_()
        await ctx.route("**/*", blocker)

        page = await ctx.new_page()
        page.set_default_timeout(PAGE_TIMEOUT_MS)

        try:
            await page.goto(URL, wait_until="load", timeout=PAGE_TIMEOUT_MS)
            await accept_cookies(page)
            await autoscroll(page)

            # Wait until any of the keywords appear anywhere
            try:
                await page.wait_for_function(
                    """() => /PAKIET\\s+(ULTRA|PRO|MAX|CHILL)/i.test(document.body.innerText)""",
                    timeout=15000
                )
            except PWTimeout:
                pass  # we'll still try fallback scanning

            cards = await get_cards(page)
            for name, card in cards:
                txt = "\n".join([l.strip() for l in (await card.inner_text()).splitlines() if l.strip()])
                per30_list = parse_all_gb_per30(txt)
                per30_gb = max(per30_list) if per30_list else None
                unlim_first = parse_unlimited_first_months(txt)
                price = parse_price_regular(txt)

                plan = {
                    "plan_code": name,
                    "name": f"Pakiet {name}",
                    "type": "prepaid",
                    "data": {
                        **({"headline_total_gb": parse_headline_total_gb(txt)} if parse_headline_total_gb(txt) else {}),
                        **({"per30_gb": per30_gb} if per30_gb else {}),
                        **({"unlimited_first_months": unlim_first} if unlim_first else {}),
                        "rollover": has_rollover(txt),
                    },
                    "roaming_gb_eu": parse_roaming_gb(txt),
                    "unlimited_calls_sms_mms": has_unlimited_calls(txt),
                    "pricing": {
                        "regular_price_pln_per_30d": price,
                        "intro_promo": parse_intro_promo(txt),
                    },
                    "actions": {"how_to_activate_button": True},
                    "description": make_description(name, per30_gb, unlim_first, price),
                }
                out["plans"].append(plan)

            if not out["plans"]:
                out["status"] = "no_cards_found"

        except PWTimeout:
            out["status"] = "timeout"
        finally:
            await browser.close()
    return out

if __name__ == "__main__":
    data = asyncio.run(scrape())
    with open("plus_prepaid_plans.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved plus_prepaid_plans.json")
