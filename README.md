# Multi-Agent AI Platform - Dokumentacja Projektu

## 🚀 Przegląd Projektu

Platforma multi-agentowa wykorzystująca LangGraph do orkiestracji agentów AI z integracją Scaleway i OpenAI. System automatycznie routuje zapytania między różnymi agentami w zależności od charakteru zadania.

## 📁 Architektura Plików

```
play-hackathon-beszketnyky/
├── README.md                          # Ta dokumentacja
├── .env                              # Zmienne środowiskowe
├── .gitignore                        # Pliki ignorowane przez Git
├── docker-compose.yml                # Orkiestracja kontenerów
├── requirements.txt                  # Główne zależności Python
│
├── backend/                          # Backend API (Python + FastAPI + LangGraph)
│   ├── main.py                      # Główna aplikacja FastAPI
│   ├── Dockerfile                   # Kontener backend
│   ├── requirements.txt             # Zależności backend
│   │
│   ├── agents/                      # Konfiguracja agentów LangGraph
│   │   ├── __init__.py
│   │   ├── states.py               # Definicje stanów agentów
│   │   ├── prompts.py              # Prompty dla agentów
│   │   └── langgraph_config.py     # Główna konfiguracja LangGraph
│   │
│   ├── services/                    # Serwisy integracji
│   │   ├── __init__.py
│   │   ├── openai_service.py       # Integracja OpenAI GPT-4o
│   │   ├── scaleway_genai_service.py # Integracja Scaleway GenAI
│   │   ├── object_storage.py       # Scaleway Object Storage
│   │   └── rag_service.py          # RAG z pgvector
│   │
│   ├── database/                    # Konfiguracja bazy danych
│   │   ├── __init__.py
│   │   └── connection.py           # Połączenia z PostgreSQL
│   │
│   └── utils/                       # Narzędzia pomocnicze
│       ├── __init__.py
│       └── config.py               # Konfiguracja aplikacji
│
├── frontend/                        # Frontend (React + TypeScript)
│   ├── package.json                # Zależności Node.js
│   ├── tsconfig.json              # Konfiguracja TypeScript
│   ├── vite.config.ts             # Konfiguracja Vite
│   ├── tailwind.config.js         # Konfiguracja TailwindCSS
│   ├── Dockerfile                 # Kontener frontend
│   ├── .env                       # Zmienne środowiskowe frontend
│   │
│   ├── public/                    # Pliki statyczne
│   └── src/                       # Kod źródłowy React
│       ├── main.tsx              # Punkt wejścia aplikacji
│       ├── App.tsx               # Główny komponent
│       ├── components/           # Komponenty React
│       ├── stores/               # Zustand store management
│       ├── views/                # Widoki/strony
│       └── services/             # Serwisy API
│
└── database/                       # Skrypty bazy danych
    └── init.sql                   # Inicjalizacja PostgreSQL z pgvector
```

## 🤖 Architektura Multi-Agent

### Workflow LangGraph

```
[Użytkownik] → [Supervisor Agent] → [Workforce Agent / Strategist Agent] → [Odpowiedź]
                     ↓                           ↓
               Analiza zapytania         Wybór odpowiedniego
               i routing decision         modelu AI
```

### Agenci

#### 1. **Supervisor Agent**

-   **Rola**: Router i koordynator
-   **Funkcja**: Analizuje zapytania i decyduje o routingu
-   **Logika routingu**:
    -   Słowa kluczowe strategiczne → Strategist Agent
    -   Zadania operacyjne → Workforce Agent
    -   Długie/złożone zapytania → Strategist Agent

#### 2. **Workforce Agent**

-   **Model**: Scaleway GenAI (Mistral)
-   **Przeznaczenie**: Szybkie wykonywanie prostych zadań
-   **Charakterystyka**: Wysoka prędkość, niższy koszt
-   **Przykłady**: Generowanie tekstu, tłumaczenia, proste analizy

#### 3. **Strategist Agent**

-   **Model**: OpenAI GPT-4o
-   **Przeznaczenie**: Głęboka analiza i zadania strategiczne
-   **Charakterystyka**: Wysoka jakość, złożone rozumowanie
-   **Przykłady**: Analizy biznesowe, planowanie, złożone problemy

## 🛠️ Stos Technologiczny

### Backend

-   **Framework**: FastAPI 0.115.0
-   **Orkiestracja AI**: LangGraph 0.2.55
-   **Baza danych**: PostgreSQL z pgvector
-   **AI Models**:
    -   OpenAI GPT-4o (strategist)
    -   Scaleway GenAI Mistral (workforce)
-   **Storage**: Scaleway Object Storage
-   **Cache**: Redis
-   **ORM**: SQLAlchemy + asyncpg

### Frontend

-   **Framework**: React 18 + TypeScript
-   **Bundler**: Vite
-   **Styling**: TailwindCSS
-   **State Management**: Zustand
-   **HTTP Client**: Axios + React Query

### Infrastruktura

-   **Hosting**: Scaleway Serverless Containers
-   **Database**: Scaleway Managed PostgreSQL
-   **Storage**: Scaleway Object Storage
-   **Containerization**: Docker + Docker Compose

## 🚀 Uruchomienie Projektu

### Wymagania

-   Docker & Docker Compose
-   Node.js 18+ (dla lokalnego developmentu frontend)
-   Python 3.11+ (dla lokalnego developmentu backend)

### 1. Klonowanie i konfiguracja

```bash
git clone <repository-url>
cd play-hackathon-beszketnyky

# Skopiuj i wypełnij zmienne środowiskowe
cp .env.example .env
cp frontend/.env.example frontend/.env
```

### 2. Konfiguracja zmiennych środowiskowych

**Główny `.env`:**

```env
# Database
POSTGRES_DB=ai_platform
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Scaleway Configuration
SCALEWAY_ACCESS_KEY=your_scaleway_access_key
SCALEWAY_SECRET_KEY=your_scaleway_secret_key
SCALEWAY_PROJECT_ID=your_project_id
SCALEWAY_REGION=fr-par
SCALEWAY_BUCKET_NAME=your_bucket_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**Frontend `.env`:**

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Platform
VITE_ENVIRONMENT=development
```

### 3. Uruchomienie przez Docker Compose

```bash
# Uruchom wszystkie serwisy
docker-compose up -d

# Sprawdź logi
docker-compose logs -f

# Backend dostępny na: http://localhost:8000
# Frontend dostępny na: http://localhost:3000
# PostgreSQL na: localhost:5432
# Redis na: localhost:6379
```

### 4. Rozwój lokalny

**Backend:**

```bash
cd backend

# Utwórz virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom serwer
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Zainstaluj zależności
npm install

# Uruchom dev server
npm run dev
```

## 📊 RAG (Retrieval-Augmented Generation)

### Funkcjonalności

-   **Embeddingi**: OpenAI text-embedding-ada-002
-   **Vector Search**: PostgreSQL pgvector
-   **Chunking**: Automatyczny podział dokumentów z overlappingiem
-   **Storage**: Scaleway Object Storage jako backup

### Użycie RAG

```python
# Dodanie dokumentu do bazy wiedzy
result = await rag_service.add_document(
    title="Dokumentacja produktu",
    content="Treść dokumentu...",
    source_type="manual"
)

# Wyszukiwanie podobnych dokumentów
results = await rag_service.search_similar_documents(
    query="jak skonfigurować produkt?",
    limit=5,
    similarity_threshold=0.7
)

# Automatyczne użycie w agentach
# Agenci automatycznie korzystają z RAG gdy to potrzebne
```

## 🔌 API Endpoints

### Główne endpointy

**Agent Chat:**

```http
POST /agent
Content-Type: application/json

{
  "message": "Przeanalizuj rynek AI w Polsce",
  "thread_id": "user-session-123"
}
```

**Health Check:**

```http
GET /health
```

**RAG Management:**

```http
POST /rag/documents
GET /rag/search?query=...
```

### Odpowiedzi API

```json
{
	"success": true,
	"response": "Odpowiedź agenta...",
	"agent_used": "strategist",
	"routing_reason": "Wykryto zapytanie strategiczne",
	"rag_used": true,
	"thread_id": "user-session-123"
}
```

## 🗄️ Schema Bazy Danych

### Główne tabele

```sql
-- Użytkownicy i sesje
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Konwersacje multi-agent
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    thread_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokumenty dla RAG
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(100),
    source_reference VARCHAR(500),
    metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Embeddingi z pgvector
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 dimension
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logi działania agentów
CREATE TABLE agent_interactions (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    agent_type VARCHAR(50) NOT NULL,
    input_message TEXT,
    output_message TEXT,
    routing_reason TEXT,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testowanie

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/test_agents.py -v
pytest tests/test_rag.py -v
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests

```bash
# Test pełnego workflow
docker-compose exec backend pytest tests/integration/ -v
```

## 📈 Monitoring i Logi

### Structured Logging

-   **Framework**: structlog
-   **Format**: JSON dla production
-   **Poziomy**: DEBUG, INFO, WARNING, ERROR

### Metryki

-   Response time agentów
-   Użycie tokenów AI
-   Accuracy RAG search
-   Error rates

### Health Checks

```bash
# Sprawdź status wszystkich komponentów
curl http://localhost:8000/health

# Sprawdź konkretny serwis
curl http://localhost:8000/health/scaleway
curl http://localhost:8000/health/openai
curl http://localhost:8000/health/database
```

## 🚢 Deployment

### Scaleway Serverless Containers

**Backend deployment:**

```bash
# Build i push do registry
docker build -t backend:latest ./backend
docker tag backend:latest rg.fr-par.scw.cloud/your-namespace/backend:latest
docker push rg.fr-par.scw.cloud/your-namespace/backend:latest

# Deploy przez Scaleway CLI
scw container container deploy \
  registry-image=rg.fr-par.scw.cloud/your-namespace/backend:latest \
  name=ai-platform-backend \
  port=8000
```

**Frontend deployment:**

```bash
# Build static files
cd frontend && npm run build

# Upload do Scaleway Object Storage
aws s3 sync dist/ s3://your-frontend-bucket --endpoint-url=https://s3.fr-par.scw.cloud
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Production database
POSTGRES_HOST=your-scaleway-postgres.fr-par.scw.cloud
POSTGRES_SSL=require

# Production storage
SCALEWAY_BUCKET_NAME=ai-platform-prod-storage
```

## 🔒 Bezpieczeństwo

### API Security

-   Rate limiting
-   CORS configuration
-   Input validation
-   SQL injection protection

### Secrets Management

-   Scaleway Secret Manager
-   Environment variables
-   No hardcoded credentials

### Database Security

-   SSL connections
-   Connection pooling
-   Prepared statements

## 🐛 Debugging

### Common Issues

**1. Import errors w Python:**

```bash
# Sprawdź czy dependencies są zainstalowane
pip list | grep langgraph
pip install -r requirements.txt
```

**2. Database connection issues:**

```bash
# Sprawdź status PostgreSQL
docker-compose ps
docker-compose logs postgres

# Test connection
psql -h localhost -U postgres -d ai_platform
```

**3. Scaleway API errors:**

```bash
# Sprawdź klucze API
curl -H "X-Auth-Token: $SCALEWAY_SECRET_KEY" \
  https://api.scaleway.com/v1alpha1/regions/fr-par/ai-models/models
```

### Development Tips

-   Użyj `docker-compose logs -f service_name` dla real-time logs
-   Frontend proxy w Vite automatycznie przekierowuje API calls
-   Backend hot reload z `--reload` flag
-   PostgreSQL pgAdmin dostępny na porcie 5050

## 📚 Dodatkowe Zasoby

-   [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
-   [Scaleway GenAI API](https://www.scaleway.com/en/developers/api/ai-inference/)
-   [OpenAI API Documentation](https://platform.openai.com/docs)
-   [pgvector Documentation](https://github.com/pgvector/pgvector)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Rozwój

### Dodawanie nowego agenta

1. Dodaj definicję w `agents/states.py`
2. Stwórz prompt w `agents/prompts.py`
3. Implementuj logikę w `agents/langgraph_config.py`
4. Zaktualizuj routing w `should_continue()`
5. Dodaj testy w `tests/test_agents.py`

### Dodawanie nowego serwisu

1. Stwórz plik w `services/`
2. Dodaj do `requirements.txt` jeśli potrzebne
3. Zaktualizuj konfigurację w `utils/config.py`
4. Dodaj health check w `main.py`

---

## 📄 Licencja

MIT License - zobacz [LICENSE](LICENSE) file for details.

## 👥 Autorzy 🧌

-   **Zespół AI Platform** - Initial work

---

_Dokumentacja została wygenerowana automatycznie na podstawie architektury projektu._
