import asyncio, json, re, argparse
from pathlib import Path
from typing import Dict, Any, List
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

PLN = "PLN"
PRICE_RE = re.compile(r'(\d+[.,]?\d*)\s*zł', re.I)
GB_RE    = re.compile(r'(\d+[.,]?\d*)\s*GB', re.I)
MONTHS_RE= re.compile(r'(\d+)\s*miesi', re.I)

def money(s: str):
    m = PRICE_RE.search(s or "")
    return float(m.group(1).replace(",", ".")) if m else None

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def parse_common(features: List[str], conditions: List[str]) -> Dict[str, Any]:
    # activation & months
    activation, months = None, None
    for c in conditions:
        if ("aktywacja" in c.lower() or "opłata aktywacyjna" in c.lower()):
            v = money(c)
            if v is not None: activation = v
        m = MONTHS_RE.search(c)
        if m: months = int(m.group(1))

    # data gb (max seen), roaming GB if mentioned
    domestic, roaming = None, None
    for f in features:
        for g in GB_RE.findall(f):
            val = float(g.replace(",", "."))
            domestic = max(domestic or 0, val)
        if re.search(r'roamingu\s*UE', f, re.I):
            m = GB_RE.search(f)
            if m: roaming = float(m.group(1).replace(",", "."))
    return {
        "activation_fee_pln": activation,
        "contract_length_months": months,
        "domestic_data_gb": domestic,
        "roaming_gb": roaming
    }

# --------- Shared helpers for page interaction ---------
async def click_cookies(page):
    # Try common consent buttons
    selectors = [
        'button:has-text("Akceptuj")',
        'button:has-text("Akceptuję")',
        'button:has-text("Zgadzam")',
        '[id*="accept"]', '[data-testid*="accept"]',
        'button:has-text("Rozumiem")',
    ]
    for sel in selectors:
        try:
            await page.locator(sel).first.click(timeout=1200)
            break
        except Exception:
            pass

async def click_all_bullets(page):
    # Scroll to stimulate lazy content
    for _ in range(6):
        await page.mouse.wheel(0, 1200)
        await asyncio.sleep(0.25)

    bullet_selectors = [
        ".swiper-pagination .swiper-pagination-bullet",
        "button[role='tab']",
        "button[aria-label*='slajd']",
        "button[aria-label*='slide']",
    ]
    for sel in bullet_selectors:
        loc = page.locator(sel)
        n = await loc.count()
        if n == 0: continue
        for i in range(n):
            b = loc.nth(i)
            try:
                await b.scroll_into_view_if_needed()
                await b.click()
                await asyncio.sleep(0.35)
            except Exception:
                try:
                    handle = await b.element_handle()
                    if handle: await page.evaluate("(el)=>el.click()", handle)
                    await asyncio.sleep(0.35)
                except Exception:
                    pass

# --------- PLAY scraper ----------
PLAY_URL = "https://www.play.pl/oferta/play-abonament/przejdz-na-abonament"

JS_PLAY_VISIBLE = r"""
() => {
  const norm = s => (s||"").replace(/\s+/g," ").trim();
  const txt  = el => norm(el?.innerText || el?.textContent || "");
  const vis  = el => {
    if (!el) return false;
    const st = getComputedStyle(el);
    if (st.visibility==="hidden"||st.display==="none"||+st.opacity===0) return false;
    const r = el.getBoundingClientRect();
    return r.width>2 && r.height>2;
  };
  const qa = (el,sel)=>Array.from(el.querySelectorAll(sel));

  const headings = qa(document,'h1, h2, h3, h4, [role="heading"]')
    .filter(h=>{
      const t = txt(h);
      return /^Oferta\s+[SML](\+)?$/i.test(t) || /HOMEBOX/i.test(t) || /^Oferta\s+L$/i.test(t);
    })
    .filter(vis);

  const findCard = (h)=>{
    let cur=h;
    for (let i=0;i<8 && cur;i++){
      if (/Oferta\s+zawiera/i.test(txt(cur))) return cur;
      cur = cur.parentElement;
    }
    return h.closest("section, article, div") || h;
  }

  const out=[];
  for (const h of headings){
    const card = findCard(h);
    if (!vis(card)) continue;

    // prices
    let oldP=null, curP=null, note=null;
    const oldEl = card.querySelector("del, s");
    if (oldEl) oldP = txt(oldEl);

    const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT);
    const current = [];
    let n;
    while(n=walker.nextNode()){
      const s = norm(n.nodeValue);
      if(!s || !/zł/i.test(s)) continue;
      let p=n.parentElement, crossed=false;
      while(p){ if (["DEL","S"].includes(p.tagName)) {crossed=true;break;} p=p.parentElement; }
      if(!crossed) current.push(s);
    }
    if(current.length) curP=current[current.length-1];

    const noteEl = qa(card,"*").find(e=>/cena po rabatach/i.test(txt(e)));
    if (noteEl) note=txt(noteEl);

    const listAfter=(re)=>{
      const anchor = qa(card,"*").find(e=>re.test(txt(e)));
      if(!anchor) return [];
      const lists = qa(card,"ul,ol").filter(l=> anchor.compareDocumentPosition(l)&Node.DOCUMENT_POSITION_FOLLOWING);
      if(!lists.length) return [];
      return qa(lists[0],"li").map(li=>txt(li));
    };

    out.push({
      name: txt(h),
      features: listAfter(/Oferta\s+zawiera/i),
      conditions: listAfter(/Warunki\s+oferty/i),
      priceText: curP, oldPriceText: oldP, priceNote: note,
      blob: txt(card)
    });
  }
  return out;
}
"""

async def scrape_play() -> Dict[str, Any]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale="pl-PL")
        page = await ctx.new_page()
        await page.goto(PLAY_URL, wait_until="domcontentloaded", timeout=120000)
        await click_cookies(page)
        first = await page.evaluate(JS_PLAY_VISIBLE)
        await click_all_bullets(page)
        second = await page.evaluate(JS_PLAY_VISIBLE)
        await ctx.close(); await browser.close()

    cards = first + second
    # shape + dedupe by name
    seen, plans = set(), []
    pref = ["Oferta S","Oferta S+","Oferta M","Oferta L","HOMEBOX","Oferta HOMEBOX"]
    order = {n:i for i,n in enumerate(pref)}
    for c in cards:
        name = norm(c["name"])
        if name in seen: continue
        seen.add(name)
        price = money(c.get("priceText"))
        oldp  = money(c.get("oldPriceText"))
        features = c.get("features", [])
        conditions= c.get("conditions", [])
        plans.append({
            "plan_id": name.replace("Oferta","").strip(),
            "name": name,
            "price": None if price is None else {"amount": price, "currency": PLN},
            "old_price": None if oldp  is None else {"amount": oldp , "currency": PLN},
            "price_note": c.get("priceNote"),
            "features": features,
            "conditions": conditions,
            "parsed": parse_common(features, conditions),
            "raw_text_blob": c.get("blob","")
        })
    plans.sort(key=lambda x: (order.get(x["name"], 999), x["name"]))
    return {"url": PLAY_URL, "plans": plans}

# --------- T-MOBILE scraper ----------
TMOBILE_URL = "https://www.t-mobile.pl/c/abonament"

JS_TMOBILE_VISIBLE = r"""
() => {
  const norm = s => (s||"").replace(/\s+/g," ").trim();
  const txt  = el => norm(el?.innerText || el?.textContent || "");
  const vis  = el => {
    if (!el) return false;
    const st = getComputedStyle(el);
    if (st.visibility==="hidden"||st.display==="none"||+st.opacity===0) return false;
    const r = el.getBoundingClientRect();
    return r.width>2 && r.height>2;
  };
  const qa = (el,sel)=>Array.from(el.querySelectorAll(sel));

  // T-Mobile bundles subscriptions in large tiles; we filter for those that look like "Abonament"
  const tiles = qa(document, "section, article, div")
    .filter(el => /Abonament/i.test(txt(el)) && /z rabatami|mies\.|Umowa|Abonament komórkowy/i.test(txt(el)))
    .filter(vis);

  const out=[];
  for (const t of tiles){
    // Title: usually a heading inside the tile (try strongest first)
    const title = [ "h1","h2","h3","[role='heading']" ]
      .map(sel=> t.querySelector(sel))
      .filter(Boolean)
      .map(el=>txt(el))[0] || "Abonament";

    // Price text – biggest number with "zł" in the tile not crossed
    let oldP=null, curP=null;
    const oldEl = t.querySelector("del, s");
    if (oldEl) oldP = txt(oldEl);

    const walker = document.createTreeWalker(t, NodeFilter.SHOW_TEXT);
    const current=[];
    let n;
    while(n=walker.nextNode()){
      const s = norm(n.nodeValue);
      if(!s || !/zł/i.test(s)) continue;
      let p=n.parentElement, crossed=false;
      while(p){ if (["DEL","S"].includes(p.tagName)) {crossed=true;break;} p=p.parentElement; }
      if(!crossed) current.push(s);
    }
    if(current.length) curP=current[current.length-1];

    // Features list (✔ bullets)
    let features=[];
    const lists = qa(t,"ul, ol");
    if (lists.length){
      features = qa(lists[0],"li").map(li=>txt(li));
    }

    // Conditions (look for lines with "Umowa", "rabat", "opłata")
    const lines = txt(t).split(/\n|·|•/).map(norm).filter(Boolean);
    const conditions = lines.filter(x => /(Umowa|rabat|opłata|Aktywacja|mies.)/i.test(x));

    out.push({
      name: title,
      priceText: curP,
      oldPriceText: oldP,
      features, conditions,
      blob: txt(t)
    });
  }
  return out;
}
"""

async def scrape_tmobile() -> Dict[str, Any]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale="pl-PL")
        page = await ctx.new_page()
        await page.goto(TMOBILE_URL, wait_until="domcontentloaded", timeout=120000)
        await click_cookies(page)
        # Scroll a bit to ensure all tiles appear
        for _ in range(6):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(0.25)
        data = await page.evaluate(JS_TMOBILE_VISIBLE)
        await ctx.close(); await browser.close()

    plans, seen = [], set()
    for c in data:
        name = norm(c["name"])
        # keep subscription tiles; skip obvious “second line” promos if you want strictness:
        if not re.search(r'Abonament', name, re.I) and not re.search(r'Kolejny abonament', name, re.I):
            # still allow, but you can tighten this filter if needed
            pass
        if name in seen: continue
        seen.add(name)

        price = money(c.get("priceText"))
        oldp  = money(c.get("oldPriceText"))
        features = c.get("features", [])
        conditions= c.get("conditions", [])
        plans.append({
            "plan_id": name,   # T-Mobile uses marketing names; keep full
            "name": name,
            "price": None if price is None else {"amount": price, "currency": PLN},
            "old_price": None if oldp  is None else {"amount": oldp , "currency": PLN},
            "price_note": None,
            "features": features,
            "conditions": conditions,
            "parsed": parse_common(features, conditions),
            "raw_text_blob": c.get("blob","")
        })
    return {"url": TMOBILE_URL, "plans": plans}

# --------- CLI ---------
async def run(site: str) -> Dict[str, Any]:
    if site == "play":    return await scrape_play()
    if site == "tmobile": return await scrape_tmobile()
    raise SystemExit("Unknown --site. Use 'play' or 'tmobile'.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=["play","tmobile"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = asyncio.run(run(args.site))
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {args.out} with {len(data['plans'])} plans.")

if __name__ == "__main__":
    main()
