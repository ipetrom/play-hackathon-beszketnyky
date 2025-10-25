# 📊 Pełna Struktura Projektu: Telecom News Multi-Agent System

## 🎯 Przegląd Wysokopoziomowy

```
play-hackathon-beszketnyky/              # ROOT - Główny folder projektu
│
├── 📦 Konfiguracja i Zarządzanie
│   ├── docker-compose.yml               # Orkiestracja kontenerów (Backend, Frontend, PostgreSQL, Redis)
│   ├── poetry.lock                      # Lock file dla zależności Python
│   ├── pyproject.toml                   # Konfiguracja Poetry (Python Package Manager)
│   ├── .env                             # Zmienne środowiskowe (sekrety, API keys)
│   ├── .env.example                     # Szablon .env
│   ├── .gitignore                       # Pliki ignorowane przez Git
│   └── README.md                        # Główna dokumentacja
│
├── 📁 backend/                          # BACKEND - Python + FastAPI + LangGraph
│   ├── main.py                          # ⭐ Główna aplikacja FastAPI
│   ├── Dockerfile                       # Konteneryzacja backendu
│   ├── start.sh                         # Skrypt uruchamiający backend
│   ├── docker-compose.yml               # Dodatkowy compose dla backendu
│   ├── nginx.conf                       # Konfiguracja Nginx (reverse proxy)
│   ├── env.example                      # Szablon zmiennych dla backendu
│   ├── requirements.txt                 # Zależności (alternatywa dla Poetry)
│   ├── test_system.py                   # Testy systemowe
│   ├── test_pipeline.py                 # Testy pipeline'u
│   ├── example_usage.py                 # Przykład użycia
│   ├── example_pipeline_usage.py        # Przykład pipeline'u
│   │
│   ├── 🤖 agents/                       # Agenci AI (LangGraph)
│   │   ├── workflow.py                  # ⭐ TelecomWorkflow - główny orchestrator
│   │   ├── keeper_agent.py              # Zarządzanie stanem i kontekstem
│   │   ├── writer_agent.py              # Generowanie treści tekstowych
│   │   ├── serper_verification_agent.py # Weryfikacja danych via Serper API
│   │   ├── perplexity_agent.py          # Integracja Perplexity AI
│   │   ├── final_summarizer_agent.py    # Podsumowanie wyników
│   │   └── tips_alerts_generator.py     # Generowanie alertów i rekomendacji
│   │
│   ├── 🔌 api/                          # REST API Endpoints
│   │   └── routes.py                    # ⭐ Definicja wszystkich endpointów (/workflow/run, /reports, itp.)
│   │
│   ├── 🛠 services/                     # Serwisy i Integracje
│   │   ├── config.py                    # ⭐ Settings - centralizowana konfiguracja
│   │   ├── database.py                  # PostgreSQL operacje (CRUD)
│   │   ├── http_client.py               # HTTP Client dla API (Serper, scrapers)
│   │   ├── llm_service.py               # Integracja z LLM (OpenAI, Scaleway)
│   │   ├── perplexity_service.py        # Perplexity API wrapper
│   │   ├── scraper_service.py           # Logika scrapowania stron
│   │   └── report_logger.py             # Logowanie i zapis raportów JSON
│   │
│   ├── 📚 utils/                        # Narzędzia pomocnicze
│   │   └── (puste - do rozszerzenia)
│   │
│   └── 📝 logs/                         # Logi i raporty generowane w runtime
│       ├── tips_alerts_20251025_033152.json
│       └── tips_alerts_20251025_033212.json
│
├── 🖥 frontend/                         # FRONTEND - React + Vite + TypeScript
│   ├── package.json                     # Zależności Node.js (React, Axios, Zustand, TailwindCSS)
│   ├── package-lock.json                # Lock file dla npm
│   ├── index.html                       # HTML entry point
│   ├── vite.config.js                   # ⭐ Konfiguracja Vite build tool
│   ├── eslint.config.js                 # ESLint rules (code style)
│   ├── Dockerfile                       # Konteneryzacja produkc jna
│   ├── Dockerfile.dev                   # Konteneryzacja development
│   ├── nginx.conf                       # Nginx config dla frontendu
│   │
│   ├── src/
│   │   ├── main.jsx                     # ⭐ Bootstrap aplikacji React
│   │   ├── App.jsx                      # ⭐ Główny komponent aplikacji
│   │   │
│   │   ├── 🔌 api/                      # HTTP Clients
│   │   │   └── (API endpoints do komunikacji z backendem)
│   │   │
│   │   └── 🛠 services/                 # Frontend Services
│   │       └── (Zustand store, logika biznesowa)
│   │
│   └── 📁 public/                       # Statyczne assety (obrazy, ikony)
│
├── 💾 database/                         # Schematy i migracje bazy danych
│   └── init.sql                         # ⭐ Inicjalne schematy PostgreSQL
│                                        # (tabele: news, reports, alerts, itp.)
│
├── 🕷 scrapers/                         # Scrapers (alternatywny zestaw)
│   ├── main_scraper.py                  # Główny orchestrator
│   ├── financial_scraper.py             # Scraper wiadomości finansowych
│   ├── political_scraper.py             # Scraper wiadomości politycznych
│   ├── report_generator.py              # Generowanie raportów
│   ├── config.py                        # Konfiguracja scraperów
│   ├── setup.py                         # Setup script
│   ├── requirements.txt                 # Zależności
│   ├── example_usage.py                 # Przykłady
│   ├── demo_env_usage.py                # Demo zmiennych środowiskowych
│   ├── env_template.txt                 # Template zmiennych
│   └── README.md                        # Dokumentacja
│
├── 🕷 scrappers/                        # Scrapers (główny zestaw)
│   │
│   ├── 📱 operators/                    # Scrapers dla operatorów telecom
│   │   ├── orange_scraper.py            # Orange Polska
│   │   ├── play_play_abonament_scraper.py  # Play
│   │   ├── plus_scraper.py              # Plus
│   │   └── tmobile_plans.py             # T-Mobile
│   │
│   └── 🔍 serper/                       # Scraper z Serper API
│       ├── main_scraper.py              # ⭐ Główny scraper
│       ├── telecom_news_scraper.py      # Wiadomości telekomunikacyjne
│       ├── financial_scraper.py         # Wiadomości finansowe
│       ├── political_scraper.py         # Wiadomości polityczne
│       ├── legal_scraper.py             # Wiadomości prawne
│       ├── report_generator.py          # Generator raportów
│       ├── config.py                    # Konfiguracja
│       └── README.md                    # Dokumentacja
│
├── 📝 logs/                             # Logi systemowe
│   └── (raporty i logi runtime)
│
├── 🔬 bin/                              # Binaries i testy
│   ├── test_request.py                  # Test requestów API
│   ├── test_system.py                   # Test systemu
│   ├── test_pipeline.py                 # Test pipeline'u
│   ├── example_usage.py                 # Przykłady użycia
│   ├── example_pipeline_usage.py        # Przykłady pipeline'u
│   │
│   └── 📊 jsons_serper_test/            # Testowe dane JSON
│       ├── telecom_report_20251024_214933.json
│       ├── telecom_news_20251024_183447.json
│       └── telecom_news_20251024_214933.json
│
└── (Pliki głównego katalogu)
    ├── telecom_news_20251024_183447.json    # Dane testowe
    ├── telecom_news_20251024_214933.json    # Dane testowe
    └── telecom_report_20251024_214933.json  # Raport testowy
```

---

## 📋 Szczegółowy Opis Katalogów

### **`/backend` - Python Backend (FastAPI + LangGraph)**

#### **Główne pliki**

| Plik | Funkcja | Technologia |
|------|---------|-------------|
| `main.py` | Główna aplikacja, CORS, middleware, lifespan | FastAPI, asyncio |
| `Dockerfile` | Obrazek kontenerowy | Docker |
| `start.sh` | Skrypt startowy | Shell |
| `docker-compose.yml` | Orkiestracja usług (dodatkowy) | Docker Compose |

#### **`/backend/agents` - Orkiestracja Agentów AI**

| Plik | Rola Agenta | Opis |
|------|-----------|------|
| `workflow.py` | **Orchestrator** | Klasa `TelecomWorkflow` - zarządza całym workflowem, inicjalizuje LangGraph, koordynuje agentów |
| `keeper_agent.py` | **State Manager** | Zarządza stanem konwersacji, historyją, kontekstem |
| `writer_agent.py` | **Content Generator** | Generuje teksty na podstawie danych |
| `serper_verification_agent.py` | **Verification** | Weryfikuje informacje przez Serper API (search) |
| `perplexity_agent.py` | **Advanced Search** | Zaawansowane wyszukiwania przez Perplexity |
| `final_summarizer_agent.py` | **Summarizer** | Podsumowuje wyniki wszystkich agentów |
| `tips_alerts_generator.py` | **Alert Generator** | Tworzy rekomendacje i alerty |

#### **`/backend/api` - REST Endpoints**

| Plik | Zawartość |
|------|-----------|
| `routes.py` | Definicja wszystkich endpointów: `/workflow/run`, `/reports`, `/tips-alerts`, `/domains`, itp. |

#### **`/backend/services` - Serwisy Integracji**

| Plik | Integracja | Opis |
|------|-----------|------|
| `config.py` | Pydantic Settings | Centralizowana konfiguracja (API keys, URL bazy, timeouty, itp.) |
| `database.py` | PostgreSQL | CRUD operacje, store/retrieve rezultatów |
| `http_client.py` | HTTP Client | Komunikacja z zewnętrznymi API (Serper, scrapers) |
| `llm_service.py` | OpenAI + Scaleway | Integracja z modelami LLM |
| `perplexity_service.py` | Perplexity API | Wrapper dla Perplexity API |
| `scraper_service.py` | BeautifulSoup + Selenium | Logika scrapowania stron |
| `report_logger.py` | JSON Logger | Zapisywanie raportów do JSON |

#### **`/backend/utils` - Narzędzia**

| Plik | Opis |
|------|------|
| (puste) | Przewidziane dla przyszłych narzędzi |

#### **`/backend/logs` - Runtime Logi**

Katalog dla logów i raportów generowanych w runtime.

---

### **`/frontend` - React Frontend (Vite + TypeScript)**

#### **Główne pliki**

| Plik | Funkcja | Technologia |
|------|---------|-------------|
| `package.json` | Zależności i skrypty | npm |
| `index.html` | HTML entry point | HTML5 |
| `main.jsx` | React bootstrap | React |
| `App.jsx` | Główny komponent | React |
| `vite.config.js` | Build configuration | Vite |
| `eslint.config.js` | Code linting rules | ESLint |
| `Dockerfile` | Produkcja | Docker |
| `Dockerfile.dev` | Development | Docker |
| `nginx.conf` | Reverse proxy | Nginx |

#### **`/frontend/src` - Kod źródłowy**

```
src/
├── main.jsx                 # Bootstrap
├── App.jsx                  # Root component
├── api/                     # HTTP clients (Axios)
│   └── [API wrappers]       # Komunikacja z backendem
└── services/                # Frontend services
    └── [Zustand stores]     # State management
```

#### **`/frontend/public` - Statyczne Assety**

Katalog dla obrazów, ikon, fontów itp.

---

### **`/database` - Baza Danych**

| Plik | Opis |
|------|------|
| `init.sql` | Inicjalne schematy PostgreSQL (tabele, indeksy, constraints) |

**Zawiera schematy dla:**
- `telecom_news` - wiadomości
- `reports` - raporty
- `alerts` - alerty
- `search_results` - wyniki wyszukiwań
- pgvector - embeddingi dla RAG

---

### **`/scrappers` - Scrapers (Główny zestaw)**

#### **`/scrappers/operators` - Operatorzy Telecom**

| Plik | Operator | Opis |
|------|----------|------|
| `orange_scraper.py` | 🟠 Orange Polska | Scraper danych z Orange.pl |
| `play_play_abonament_scraper.py` | 🔴 Play | Scraper planów abonamentowych Play |
| `plus_scraper.py` | 🟡 Plus | Scraper Plus.pl |
| `tmobile_plans.py` | 🔵 T-Mobile | Scraper planów T-Mobile |

#### **`/scrappers/serper` - Serper API Scrapers**

| Plik | Źródło | Opis |
|------|--------|------|
| `main_scraper.py` | Serper API | ⭐ Główny orchestrator |
| `telecom_news_scraper.py` | Serper | Wiadomości telekomunikacyjne |
| `financial_scraper.py` | Serper | Wiadomości finansowe |
| `political_scraper.py` | Serper | Wiadomości polityczne |
| `legal_scraper.py` | Serper | Wiadomości prawne |
| `report_generator.py` | - | Generator raportów |
| `config.py` | - | Konfiguracja |

---

### **`/scrapers` - Alternatywny Zestaw Scraperów**

Alternatywny zestaw scraperów (starszy lub backupowy):

| Plik | Opis |
|------|------|
| `main_scraper.py` | Główny orchestrator |
| `financial_scraper.py` | Wiadomości finansowe |
| `political_scraper.py` | Wiadomości polityczne |
| `report_generator.py` | Generator raportów |
| `config.py` | Konfiguracja |
| `setup.py` | Setup script |
| `requirements.txt` | Zależności |

---

### **`/bin` - Testy i Binaries**

| Plik | Opis |
|------|------|
| `test_request.py` | Test HTTP requestów do API |
| `test_system.py` | Komprehensywne testy systemu |
| `test_pipeline.py` | Testy pipeline'u |
| `example_usage.py` | Przykład użycia |
| `example_pipeline_usage.py` | Przykład pipeline'u |

#### **`/bin/jsons_serper_test` - Testowe Dane**

Przykładowe JSON'y z rezultatami Serper API do testowania.

---

## 🔄 Przepływ Danych w Systemie

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│                   (React Dashboard)                         │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP Requests (Axios)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND API (FastAPI)                       │
│                    /workflow/run                            │
│                   /reports, /alerts                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            WORKFLOW ORCHESTRATOR (LangGraph)                │
│                 TelecomWorkflow.run()                       │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
        ┌─────────▼────────────┐ ┌───────▼────────────┐
        │  KEEPER AGENT        │ │  SERPER SEARCH     │
        │ (State Manager)      │ │  (Verification)    │
        └──────────────────────┘ └────────────────────┘
                  │
        ┌─────────▼────────────┐
        │  WRITER AGENT        │
        │ (Content Generator)  │
        └────────────┬─────────┘
                     │
        ┌────────────▼─────────┐
        │ PERPLEXITY AGENT     │
        │ (Advanced Search)    │
        └────────────┬─────────┘
                     │
        ┌────────────▼──────────────────┐
        │ FINAL SUMMARIZER AGENT        │
        │ (Podsumowanie wyników)        │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ TIPS & ALERTS GENERATOR       │
        │ (Rekomendacje i alerty)       │
        └────────────┬───────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL + pgvector)               │
│         (Store News, Reports, Alerts, Embeddings)          │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            CACHE (Redis)                                    │
│           (Optimize Performance)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠 Stack Techniczny

### **Backend**
- **Framework**: FastAPI
- **Async**: asyncio, uvicorn
- **Agent Orchestration**: LangGraph
- **LLM Integration**: OpenAI (GPT-4), Scaleway GenAI, Perplexity
- **Database**: PostgreSQL (sqlalchemy, asyncpg) + pgvector (RAG)
- **Cache**: Redis
- **HTTP**: httpx, requests
- **Web Scraping**: BeautifulSoup, Playwright, Trafilatura
- **Configuration**: Pydantic, python-dotenv

### **Frontend**
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: Zustand
- **HTTP**: Axios
- **Animation**: Framer Motion
- **Fonts**: Fontsource Roboto

### **Infrastructure**
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx
- **Package Managers**: Poetry (Python), npm (Node.js)

---

## 🚀 Uruchamianie Projektu

### **Full Stack (Docker Compose)**
```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### **Backend (Development)**
```bash
cd backend
poetry install
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend (Development)**
```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

### **Testy**
```bash
cd bin
python test_system.py
python test_pipeline.py
```

---

## 🔐 Zmienne Środowiskowe (`.env`)

```bash
# API Keys
SERPER_API_KEY=...
PERPLEXITY_API_KEY=...
SCALEWAY_API_KEY=...
SCALEWAY_PROJECT_ID=...
OPENAI_API_KEY=...

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/telecom_news
REDIS_URL=redis://redis:6379

# Application
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Telecom Domains
TELECOM_DOMAINS=orange.pl,play.pl,tmobile.pl,plus.pl,...

# Scaleway (GenAI, Object Storage)
SCALEWAY_REGION=fr-par
```

---

## 📊 API Endpoints

```
GET  /                          # Info o API
GET  /domains                   # Lista monitorowanych domen
POST /workflow/run              # Uruchomienie pełnego workflow'u
POST /pipeline/run              # Uruchomienie scrapingu
GET  /reports                   # Pobieranie raportów
GET  /reports/{report_id}       # Szczegóły raportu
GET  /tips-alerts               # Pobieranie alertów i rekomendacji
GET  /status                    # Status aplikacji
GET  /health                    # Health check
```

---

## 🎯 Podsumowanie Ról Katalogów

| Katalog | Rola | Tech Stack |
|---------|------|-----------|
| `/backend` | API + AI Agents | FastAPI, LangGraph, OpenAI |
| `/frontend` | UI Dashboard | React, Vite, TailwindCSS |
| `/database` | Schema + Init | SQL, PostgreSQL |
| `/scrappers` | Data Collection | BeautifulSoup, Serper API |
| `/bin` | Testing | pytest, Python scripts |
| `/logs` | Runtime Logs | JSON files |

---

**Projekt gotów do hackathonu! 🚀**
