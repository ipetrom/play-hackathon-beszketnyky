import asyncio, json, re, sys, datetime
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Locator, Page

URL = "https://www.orange.pl/abonament/przedluz-umowe"

PLAN_HEADERS = {
    "S": re.compile(r"\bPlan\s*S\b", re.I),
    "M": re.compile(r"\bPlan\s*M\b", re.I),
    "L": re.compile(r"\bPlan\s*L\b", re.I),
}

PRICE_RE = re.compile(r"(\d+)\s*zł/mies\.", re.I)
INTRO_RANGE_RE = re.compile(r"od\s*(\d+)\.\s*do\s*(\d+)\.\s*mies\.\s*0\s*zł/mies\.", re.I)
SINGLE_RANGE_RE = re.compile(r"od\s*(\d+)\.\s*do\s*(\d+)\.\s*mies\.", re.I)


def parse_data_cap(line: str) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if re.search(r"bez limit", line, re.I):
        return {"type": "unlimited", "speed_limited": not bool(re.search(r"prędkości", line, re.I))}
    m = re.search(r"(\d+)\s*GB\b", line)
    if m:
        return {"type": "cap", "amount_gb": int(m.group(1))}
    return None


async def get_plan_card(page: Page, code: str) -> Locator:
    heading = page.get_by_text(PLAN_HEADERS[code], exact=False).first
    await heading.wait_for()
    card = heading.locator("xpath=ancestor-or-self::div[.//button[contains(.,'Dodaj telefon')]]").first
    return card


def extract_pricing(text: str) -> List[Dict[str, Any]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pricing: List[Dict[str, Any]] = []
    for line in lines:
        m0 = INTRO_RANGE_RE.search(line)
        if m0:
            pricing.append({"from_month": int(m0.group(1)), "to_month": int(m0.group(2)), "price_pln": 0})
    for i, line in enumerate(lines):
        m = SINGLE_RANGE_RE.search(line)
        if m:
            price_line = line + " " + (lines[i + 1] if i + 1 < len(lines) else "")
            mp = PRICE_RE.search(price_line)
            if mp:
                pricing.append(
                    {"from_month": int(m.group(1)), "to_month": int(m.group(2)), "price_pln": int(mp.group(1))}
                )
    if not pricing:
        for line in lines:
            mp = PRICE_RE.search(line)
            if mp:
                pricing.append({"from_month": 1, "to_month": 24, "price_pln": int(mp.group(1))})
                break
    return pricing


def extract_online_bonus(text: str) -> Optional[str]:
    for l in text.splitlines():
        if re.search(r"\bmies\.\s*abonamentu\s*za\s*0\s*zł\b", l, re.I) or re.search(r"tylko online", l, re.I):
            return l.strip()
    return None


def detect_benefits(text: str) -> List[str]:
    keep: List[str] = []
    for l in text.splitlines():
        if re.search(r"Rozmowy.*bez limitu", l, re.I):
            if "roaming" in l.lower():
                keep.append("Rozmowy, SMS-y i MMS-y bez limitu (PL + roaming UE)")
            else:
                keep.append("Rozmowy, SMS-y i MMS-y bez limitu")
        if re.search(r"Telewizja mobilna", l, re.I):
            keep.append("Telewizja mobilna – Pakiet Podstawowy")
    return sorted(set(keep))


def make_description(code: str, plan_name: str, data_info: Dict[str, Any], pricing: List[Dict[str, Any]]) -> str:
    """Create short English description like 'Orange Plan L for mobile — 5G, unlimited data, PLN 95/month'."""
    if not pricing:
        price_text = ""
    else:
        last_price = pricing[-1]["price_pln"]
        price_text = f", PLN {last_price}/month"
    if not data_info:
        data_text = ""
    elif data_info.get("type") == "unlimited":
        data_text = "unlimited data"
    else:
        data_text = f"{data_info.get('amount_gb')} GB data"
    return f"Orange {plan_name} for mobile — 5G, {data_text}{price_text}"


async def scrape() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "source_url": URL,
        "scraped_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "currency": "PLN",
        "contract_months": 24,
        "notes": {},
        "plans": [],
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(locale="pl-PL")
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded")

        # Accept cookies if shown
        try:
            consent = page.get_by_role("button", name=re.compile(r"(Akceptuj|Zgadzam|Accept|OK)", re.I)).first
            await consent.click(timeout=2000)
        except Exception:
            pass

        # Wait for content area
        try:
            await page.get_by_text(re.compile(r"Ceny uwzględniają m\.in\. rabaty", re.I)).wait_for(timeout=15000)
            out["notes"]["prices_include_discounts_info_bar"] = True
        except Exception:
            out["notes"]["prices_include_discounts_info_bar"] = False

        for code in ("S", "M", "L"):
            card = await get_plan_card(page, code)
            raw = await card.inner_text()
            raw_norm = "\n".join([l.strip() for l in raw.splitlines() if l.strip()])

            header_line = next((l for l in raw_norm.splitlines() if re.search(fr"\bPlan\s*{code}\b", l, re.I)), f"Plan {code}")
            data_line = next((l for l in raw_norm.splitlines() if re.search(r"(GB\b|Bez limit)", l, re.I)), "")
            data_info = parse_data_cap(data_line) or {}

            pricing = extract_pricing(raw_norm)
            description = make_description(code, header_line, data_info, pricing)

            plan: Dict[str, Any] = {
                "plan_code": code,
                "name": header_line.strip(),
                "supports_5g": bool(re.search(r"\b5G\b", raw_norm)),
                "data": data_info,
                "pricing": pricing,
                "online_bonus": extract_online_bonus(raw_norm),
                "actions": {
                    "add_phone": "Dodaj telefon" in raw_norm,
                    "choose_without_phone": "Wybierz bez telefonu" in raw_norm,
                },
                "family_link_text": next((l for l in raw_norm.splitlines() if "Rodzinne numery" in l), None),
                "benefits": detect_benefits(raw_norm),
                "description": description,
            }

            out["plans"].append(plan)

        await browser.close()
    return out

if __name__ == "__main__":
    data = asyncio.run(scrape())
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2))