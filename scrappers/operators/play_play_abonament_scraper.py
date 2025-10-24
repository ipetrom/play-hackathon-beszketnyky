# play_play_abonament_scraper.py
import asyncio, json, re, argparse
from pathlib import Path
from typing import Dict, Any, List
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

URL_DEFAULT = "https://www.play.pl/oferta/play-abonament/przejdz-na-abonament"

def norm_currency_amount(s: str):
    m = re.search(r'(\d+[.,]?\d*)\s*zł', s, flags=re.I)
    return float(m.group(1).replace(",", ".")) if m else None

JS_EXTRACT_VISIBLE_CARDS = r"""
() => {
  // Utilities
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const txt = (el) => norm(el?.innerText || el?.textContent || "");
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.visibility === "hidden" || style.display === "none" || parseFloat(style.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const q = (el, sel) => el.querySelector(sel);
  const qa = (el, sel) => Array.from(el.querySelectorAll(sel));

  // Find “card container” as nearest ancestor that also contains "Oferta zawiera"
  const findCardContainer = (start) => {
    let cur = start;
    for (let i = 0; i < 8 && cur; i++) {
      const t = txt(cur);
      if (/Oferta zawiera/i.test(t)) return cur;
      cur = cur.parentElement;
    }
    return start.closest("section, article, div") || start;
  };

  // Collect all headings that look like plan titles
  // (Oferta S|S+|M|L) or HOMEBOX (Play uses various heading levels)
  const headings = qa(document, 'h1, h2, h3, h4, h5, [role="heading"]')
    .filter(h => {
      const t = txt(h);
      return /^Oferta\s+[SML](\+)?$/i.test(t) || /HOMEBOX/i.test(t) || /^Oferta\s+L$/i.test(t);
    });

  // Deduplicate headings visible on screen (multiple duplicates can exist inside carousels)
  const visibleHeadings = [];
  const seen = new Set();
  for (const h of headings) {
    if (!isVisible(h)) continue;
    const key = txt(h) + "::" + JSON.stringify(h.getBoundingClientRect());
    if (!seen.has(key)) {
      seen.add(key);
      visibleHeadings.push(h);
    }
  }

  // Extract info per visible card
  const results = [];
  for (const h of visibleHeadings) {
    const card = findCardContainer(h);
    if (!card || !isVisible(card)) continue;

    // Title
    const name = txt(h);

    // Prices
    let oldPrice = null;
    let price = null;
    let priceNote = null;

    // old price usually in <del>/<s>
    const oldCandidates = qa(card, "del, s").map(e => txt(e)).filter(t => /zł/i.test(t));
    if (oldCandidates.length) oldPrice = oldCandidates.map(t => t)[0];

    // current prices: any text fragment with zł but NOT inside del/s
    const allWithZL = [];
    const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT, null);
    let node;
    while (node = walker.nextNode()) {
      const s = norm(node.nodeValue || "");
      if (!s || !/zł/i.test(s)) continue;
      let parent = node.parentElement;
      let isDel = false;
      while (parent) {
        if (["DEL","S"].includes(parent.tagName)) { isDel = true; break; }
        parent = parent.parentElement;
      }
      if (!isDel) allWithZL.push(s);
    }
    if (allWithZL.length) price = allWithZL[allWithZL.length - 1];

    // price note like "cena po rabatach"
    const noteEl = qa(card, "*").find(e => /cena po rabatach/i.test(txt(e)));
    if (noteEl) priceNote = txt(noteEl);

    // Sections: "Oferta zawiera" and "Warunki oferty"
    const listAfterAnchor = (anchorRe) => {
      // find heading or label element
      const anchorEl = qa(card, "*").find(e => anchorRe.test(txt(e)));
      if (!anchorEl) return [];
      // find nearest subsequent UL/OL within the card
      // Search within the same container subtree
      const root = anchorEl;
      // first UL/OL following anchor inside the card
      const lists = qa(card, "ul, ol").filter(l => {
        // ensure list appears after anchor in DOM order
        return root.compareDocumentPosition(l) & Node.DOCUMENT_POSITION_FOLLOWING;
      });
      if (!lists.length) return [];
      return qa(lists[0], "li").map(li => norm(li.innerText));
    };

    const features = listAfterAnchor(/Oferta\s+zawiera/i);
    const conditions = listAfterAnchor(/Warunki\s+oferty/i);

    results.push({
      name,
      cardText: txt(card),
      prices: { price, oldPrice, priceNote },
      features,
      conditions,
    });
  }

  return results;
}
"""

def dedupe_and_shape(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    seen = set()
    for c in cards:
        name = c.get("name") or ""
        key = name.strip().upper()
        if key in seen:
            continue
        seen.add(key)

        price_amount = norm_currency_amount(c["prices"].get("price") or "")
        old_amount   = norm_currency_amount(c["prices"].get("oldPrice") or "")

        # Parse conditions for activation fee & months
        activation = None
        months = None
        for it in c.get("conditions", []):
            amt = norm_currency_amount(it)
            if amt is not None and ("aktywacja" in it.lower() or "opłata aktywacyjna" in it.lower()):
                activation = amt
            m = re.search(r'(\d+)\s*miesi', it, flags=re.I)
            if m:
                months = int(m.group(1))

        # Parse GB from features (domestic & roaming)
        roaming_gb = None
        domestic_gb = None
        for f in c.get("features", []):
            gb = re.findall(r'(\d+[.,]?\d*)\s*GB', f, flags=re.I)
            if gb:
                for g in gb:
                    val = float(g.replace(",", "."))
                    domestic_gb = max(domestic_gb or 0, val)
            if re.search(r'roamingu\s*UE', f, flags=re.I):
                m = re.search(r'(\d+[.,]?\d*)\s*GB', f, flags=re.I)
                if m:
                    roaming_gb = float(m.group(1).replace(",", "."))

        out.append({
            "plan_id": name.replace("Oferta", "").strip(),  # "S", "S+", "M", "L", "HOMEBOX"…
            "name": name,
            "price": None if price_amount is None else {"amount": price_amount, "currency": "PLN"},
            "old_price": None if old_amount is None else {"amount": old_amount, "currency": "PLN"},
            "price_note": c["prices"].get("priceNote"),
            "features": c.get("features", []),
            "conditions": c.get("conditions", []),
            "parsed": {
                "activation_fee_pln": activation,
                "contract_length_months": months,
                "domestic_data_gb": domestic_gb,
                "roaming_gb": roaming_gb,
            },
            "raw_text_blob": c.get("cardText", ""),
        })
    return out

async def click_cookies(page):
    # Try a few common consent buttons
    selectors = [
        'button:has-text("Akceptuj")',
        'button:has-text("Akceptuję")',
        'button:has-text("Zgadzam")',
        'button:has-text("Akceptuję i przechodzę")',
        '[id*="accept"]',
        '[data-testid*="accept"]',
    ]
    for sel in selectors:
        try:
            await page.locator(sel).first.click(timeout=1500)
            break
        except PWTimeout:
            pass
        except Exception:
            pass

async def click_all_bullets(page):
    """
    Many plans sit inside a Swiper carousel. We click through ALL bullets found on the page.
    We also tolerate multiple carousels.
    """
    # Some bullets are created on scroll; ensure page is scrolled to load everything
    await page.wait_for_load_state("networkidle")
    for _ in range(6):
        await page.mouse.wheel(0, 1200)
        await asyncio.sleep(0.3)

    # Try several bullet selectors
    bullet_selectors = [
        ".swiper-pagination .swiper-pagination-bullet",
        '[role="tablist"] button[role="tab"]',
        'button[aria-label*="slajdu"]',
        'button[aria-label*="slide"]',
    ]

    clicked = 0
    for sel in bullet_selectors:
        loc = page.locator(sel)
        count = await loc.count()
        if count == 0: 
            continue
        # Click each bullet, wait for content to settle
        for i in range(count):
            bullet = loc.nth(i)
            try:
                await bullet.scroll_into_view_if_needed()
                await bullet.click()
                await asyncio.sleep(0.4)
                clicked += 1
            except Exception:
                # try JS click
                try:
                    await page.evaluate("(el)=>el.click()", await bullet.element_handle())
                    await asyncio.sleep(0.4)
                    clicked += 1
                except Exception:
                    pass
    return clicked

async def scrape(url: str) -> Dict[str, Any]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale="pl-PL", user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123 Safari/537.36"
        ))
        page = await ctx.new_page()
        await page.goto(url, wait_until="load", timeout=120000)

        await click_cookies(page)

        # First pass on initially visible slide(s)
        first_cards = await page.evaluate(JS_EXTRACT_VISIBLE_CARDS)

        # Click through all bullets (carousels) to reveal other plans (L, HOMEBOX etc.)
        await click_all_bullets(page)

        # Second pass after interactions
        after_cards = await page.evaluate(JS_EXTRACT_VISIBLE_CARDS)

        await ctx.close()
        await browser.close()

    # Merge & shape
    cards = first_cards + after_cards
    shaped = dedupe_and_shape(cards)

    # Keep only expected plans if present; otherwise return all found
    preferred_order = ["Oferta S", "Oferta S+", "Oferta M", "Oferta L", "HOMEBOX", "Oferta HOMEBOX"]
    ordered = sorted(shaped, key=lambda x: (preferred_order.index(x["name"]) if x["name"] in preferred_order else 999, x["name"]))
    return {"url": url, "plans": ordered}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=URL_DEFAULT)
    ap.add_argument("--out", default="play_plans.json")
    args = ap.parse_args()
    data = asyncio.run(scrape(args.url))
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} with {len(data['plans'])} plans.")

if __name__ == "__main__":
    main()
