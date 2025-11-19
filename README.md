# Telecomunication Intelligence Platform

Multi-agent system for automated tracking, analysis, and reporting of Poland's telecommunications market and other avaliable information.

![Demo](docs/demo.gif)

## Overview

This platform leverages advanced AI agents to monitor telecom industry news, extract actionable insights, and generate comprehensive market reports with tips and alerts. It combines web scraping, news aggregation, and intelligent analysis to provide real-time market intelligence.

**Key Capabilities:**
- Automated news collection from multiple sources
- AI-powered analysis and synthesis using multi-agent workflows
- Interactive report generation and visualization
- Market trend detection and verification
- Actionable tips and market alerts
- Comprehensive data storage and retrieval

---

## Multi-Agent System

The platform uses a coordinated multi-agent architecture where specialized agents handle different aspects of market analysis:

### Agent Roles

| Agent | Responsibility |
|-------|-----------------|
| **Agent 1: Verification** | Checks if the scraped page fits the stream (right source/topic), filters out obvious noise and errors |
| **Agent 2: Ingestor** | Cleans and normalizes relevant content, rejects irrelevant fragments and prepares data for analysis |
| **Agent 3: Writer** | Structures the preprocessed information into clear narratives/snippets ready for further processing |
| **Agent X: Perplexity** | Calls Perplexity to summarize the latest news and enrich internal data with fresh external context |
| **Agent 4: Category** | Combines Writer + Perplexity outputs and assigns categories/impact levels to each piece of information |
| **Agent 5: Tips + Alerts + Scoring** | Uses the code-based report to generate prioritized tips, alerts and a final impact/importance score |

Each stream represents a separate signal category in the system:

- **Stream A – Legal (Prawna kategoria)**  
- **Stream B – Policy / Regulatory (Polityczna kategoria)**  
- **Stream C – Market / Competitive (Rynkowa kategoria)**  

Together, these streams ensure that legal, political and market signals are processed in parallel and then merged into a single code-based report.


![Architecture](docs/architecture-play.png)

---

## Project Structure

### Backend (`/backend`)
Core Python application handling data processing and AI orchestration.

```
backend/
├── main.py                 # FastAPI application entry point
├── agents/                 # Multi-agent system
│   ├── workflow.py        # Agent orchestration & coordination
│   ├── writer_agent.py    # Content generation
│   ├── keeper_agent.py    # Data management
│   ├── final_summarizer_agent.py  # Report synthesis
│   └── ...                # Additional specialized agents
├── api/
│   └── routes.py          # REST API endpoints
├── services/              # Business logic layer
│   ├── config.py          # Configuration management
│   ├── database_*.py      # Database abstraction layers
│   ├── llm_service.py     # LLM integrations
│   ├── scraper_service.py # Web scraping orchestration
│   ├── http_client.py     # HTTP utilities
│   └── ...
├── rag/                   # Retrieval-Augmented Generation
│   ├── index_builder.py   # Vector index creation
│   ├── retriever.py       # Document retrieval system
│   └── mock_input.json
├── workflows/             # High-level workflow definitions
│   └── main_workflow.py   # Primary data processing pipeline
└── logs/                  # System logs & generated reports
```

### Frontend (`/ui`)
Modern Next.js application for data visualization and interaction.

```
ui/
├── app/                   # Next.js app directory
│   ├── page.tsx          # Homepage
│   └── reports/          # Report viewing interface
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── domain-synthesis.tsx      # Market analysis display
│   ├── tips-alerts.tsx           # Insights & alerts
│   ├── reports-table.tsx         # Report listing
│   └── ...
├── hooks/                 # Custom React hooks
├── styles/                # Global styles & Tailwind config
└── lib/
    └── utils.ts          # Utility functions
```

---
