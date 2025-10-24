"""
Configuration file for Telecommunications News Scraper
Contains all sources, keywords, and settings for the scraper system.
"""

# Serper API Configuration
SERPER_API_KEY = "your_serper_api_key_here"  # Set via environment variable SERPER_API_KEY

# Scraping Configuration
DEFAULT_DAYS_BACK = 7
MAX_ARTICLES_PER_QUERY = 20
REQUEST_TIMEOUT = 30
MAX_CONCURRENT_REQUESTS = 5

# Telecommunications Keywords for Relevance Filtering
TELECOM_KEYWORDS = [
    # Core telecom terms
    "telekomunikacja", "telecom", "telecommunications", "telefonia", "telephony",
    "internet", "broadband", "sieć", "network", "sieci", "networks",
    
    # Technology terms
    "5G", "4G", "LTE", "WiFi", "Wi-Fi", "fiber", "fibra", "kabel", "cable",
    "satelita", "satellite", "antenna", "antena", "base station", "stacja bazowa",
    "IoT", "internet rzeczy", "cyfryzacja", "digitalization", "digital",
    
    # Business terms
    "operator", "dostawca", "provider", "abonament", "subscription", "roaming",
    "infrastruktura", "infrastructure", "inwestycja", "investment",
    "konkurencja", "competition", "rynki", "markets", "usługi", "services",
    
    # Regulatory terms
    "regulacja", "regulation", "UKE", "regulator", "spectrum", "widmo",
    "frequency", "częstotliwość", "licencja", "license", "koncesja", "concession",
    "przetarg", "tender", "aukcja", "auction", "decyzja", "decision",
    
    # Polish telecom operators
    "Orange", "Play", "Plus", "T-Mobile", "Vodafone", "Cyfrowy Polsat",
    "UPC", "Vectra", "Multimedia", "Netia", "Dialog"
]

# Legal Sources (Prawo)
LEGAL_SOURCES = [
    # Polish government and legal sources
    "legislacja.rcl.gov.pl",
    "isap.sejm.gov.pl",
    "gov.pl",
    "prezydent.pl",
    "sejm.gov.pl",
    "senat.gov.pl",
    "uke.gov.pl",
    "uokik.gov.pl",
    "trybunal.gov.pl",
    "sn.gov.pl",
    
    # EU legal sources
    "berec.europa.eu",
    "digital-strategy.ec.europa.eu",
    "consilium.europa.eu",
    "europarl.europa.eu",
    "enisa.europa.eu",
    "eur-lex.europa.eu",
    "curia.europa.eu",
    "oecd.org",
    
    # International legal sources
    "itu.int",
    "icann.org",
    "wto.org"
]

# Political Sources (Polityka)
POLITICAL_SOURCES = [
    # International news
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "cnn.com",
    "nbcnews.com",
    "foxnews.com",
    "nytimes.com",
    "washingtonpost.com",
    "apnews.com",
    "theguardian.com",
    "thetimes.co.uk",
    "bbc.com",
    "lemonde.fr",
    "afp.com",
    "dw.com",
    "euronews.com",
    "aljazeera.com",
    
    # Polish news
    "onet.pl",
    "biznes.pap.pl",
    "rp.pl",
    "tvn24.pl",
    "polsatnews.pl",
    "tvn.pl",
    "interia.pl",
    "wp.pl",
    "gazeta.pl",
    "wyborcza.pl",
    
    # EU political sources
    "ec.europa.eu",
    "politico.eu",
    "europarl.europa.eu",
    "consilium.europa.eu",
    
    # Asian sources
    "news.cn",
    "caixinglobal.com",
    "japantimes.co.jp",
    "nhk.or.jp",
    "koreaherald.com",
    
    # Financial news with political content
    "ft.com",
    "wsj.com",
    "bloomberg.com"
]

# Financial Sources (Market)
FINANCIAL_SOURCES = [
    # International financial news
    "reuters.com/markets",
    "bloomberg.com/markets",
    "wsj.com/markets",
    "ft.com/markets",
    "cnbc.com",
    "marketwatch.com",
    "investing.com",
    "yahoo.com/finance",
    "seekingalpha.com",
    
    # Polish financial news
    "biznes.pap.pl",
    "rp.pl",
    "money.pl",
    "bankier.pl",
    "stooq.pl",
    "pulshr.pl",
    "gielda.pl",
    "biznes.interia.pl",
    
    # Central banks and financial institutions
    "nbp.pl",
    "ecb.europa.eu",
    "fred.stlouisfed.org",
    "imf.org",
    "bis.org",
    "worldbank.org",
    
    # Currency and trading
    "oanda.com",
    "xe.com",
    "investing.com/currencies",
    
    # Stock exchanges
    "gpw.pl",
    "nasdaq.com",
    "nyse.com",
    "londonstockexchange.com"
]

# Additional Telecommunications-Specific Sources
TELECOM_SPECIFIC_SOURCES = [
    # Industry publications
    "telecoms.com",
    "lightreading.com",
    "fiercetelecom.com",
    "telecompaper.com",
    "capacitymedia.com",
    "totaltelecom.com",
    "telecomasia.net",
    "telecoms.com",
    
    # Technology publications
    "techcrunch.com",
    "wired.com",
    "arstechnica.com",
    "theverge.com",
    "engadget.com",
    "zdnet.com",
    "computerworld.com",
    
    # Polish tech and telecom
    "komputerswiat.pl",
    "benchmark.pl",
    "doz.pl",
    "chip.pl",
    "pclab.pl",
    "antyweb.pl",
    "spidersweb.pl"
]

# Search Queries by Category
LEGAL_QUERIES = [
    "telekomunikacja regulacja prawo",
    "UKE decyzja",
    "telecom regulation Poland",
    "telefonia prawo",
    "internet regulacja",
    "5G spectrum allocation",
    "telecom law Poland",
    "UOKiK telekomunikacja",
    "konkurencja telekomunikacja",
    "telecom merger Poland",
    "EU telecom regulation",
    "UE regulacja telekomunikacja",
    "BEREC decision",
    "EU digital strategy"
]

POLITICAL_QUERIES = [
    "telecom policy Poland government",
    "telekomunikacja polityka rząd",
    "digital policy Poland",
    "cyfryzacja Polska rząd",
    "5G policy Poland",
    "telecom investment Poland government",
    "telecom infrastructure Poland policy",
    "EU telecom policy",
    "UE polityka telekomunikacja",
    "EU digital strategy",
    "EU 5G policy",
    "telecom international relations Poland",
    "telekomunikacja stosunki międzynarodowe",
    "telecom trade Poland"
]

FINANCIAL_QUERIES = [
    "telecom earnings Poland",
    "telekomunikacja wyniki finansowe",
    "Orange wyniki",
    "Play wyniki",
    "Plus wyniki",
    "telecom revenue Poland",
    "telecom profit Poland",
    "telecom quarterly results",
    "telecom investment Poland",
    "telekomunikacja inwestycja",
    "telecom infrastructure investment",
    "5G investment Poland",
    "telecom stocks Poland",
    "telekomunikacja giełda",
    "telecom market Poland",
    "PLN USD exchange rate",
    "kurs złoty dolar",
    "NBP interest rate"
]

# Impact Level Keywords
HIGH_IMPACT_KEYWORDS = {
    "legal": [
        "ustawa", "law", "rozporządzenie", "regulation", "dyrektywa", "directive",
        "decyzja uke", "uke decision", "kara", "penalty", "sankcje", "sanctions"
    ],
    "political": [
        "ustawa", "law", "rozporządzenie", "regulation", "decyzja", "decision",
        "budżet", "budget", "reforma", "reform", "strategia", "strategy",
        "wybory", "elections", "głosowanie", "voting", "referendum"
    ],
    "financial": [
        "bankructwo", "bankruptcy", "upadłość", "liquidation", "likwidacja",
        "fuzja", "merger", "przejęcie", "acquisition", "sprzedaż", "sale",
        "wyniki finansowe", "financial results", "raport roczny", "annual report",
        "dywidenda", "dividend", "wypłata", "payout"
    ]
}

MEDIUM_IMPACT_KEYWORDS = {
    "legal": [
        "konsultacje", "consultation", "projekt", "draft", "propozycja", "proposal",
        "przetarg", "tender", "aukcja", "auction", "licencja", "license"
    ],
    "political": [
        "projekt", "draft", "propozycja", "proposal", "konsultacje", "consultation",
        "plan", "program", "inwestycja", "investment", "infrastruktura", "infrastructure"
    ],
    "financial": [
        "inwestycja", "investment", "wydatki", "expenses", "koszty", "costs",
        "przychód", "revenue", "dochód", "income", "zysk", "profit",
        "akcje", "stocks", "giełda", "stock exchange"
    ]
}

# Output Configuration
OUTPUT_DIR = "reports"
LOG_LEVEL = "INFO"
SAVE_RAW_DATA = True
SAVE_PROCESSED_DATA = True
GENERATE_SUMMARY = True

# Report Generation Settings
REPORT_TEMPLATES = {
    "weekly": {
        "title": "Weekly Telecommunications Intelligence Report",
        "sections": ["executive_summary", "legal_developments", "political_developments", "financial_developments", "key_insights", "risk_assessment", "action_items"]
    },
    "daily": {
        "title": "Daily Telecommunications Intelligence Brief",
        "sections": ["executive_summary", "top_stories", "market_impact", "regulatory_updates"]
    }
}

# Email Configuration (for automated reports)
EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": "",
    "recipients": []
}
