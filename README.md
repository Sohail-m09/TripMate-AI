# TripMate AI

TripMate AI is a multi-agent travel planning application built using **LangGraph, Google Gemini, MCP/FastMCP, FastAPI, PostgreSQL, Streamlit, LangSmith, and Docker**.

It converts a natural-language travel request into structured trip information, selects the required specialist agents, searches live travel data, creates a grounded itinerary, stores trip history, and returns the final result through a Streamlit interface.

---

## Key Features

- Natural-language trip planning
- Structured trip extraction using Gemini + Pydantic
- LangGraph-based conditional routing
- Parallel specialist-agent execution
- Flight search using SerpApi / Google Flights
- Hotel search using SerpApi / Google Hotels
- Weather information using Open-Meteo
- Tourist attractions using Google Maps through SerpApi
- MCP/FastMCP tool integration
- Grounded itinerary generation
- PostgreSQL trip history and memory
- FastAPI backend
- Streamlit frontend
- LangSmith tracing and evaluation
- Unit, integration, API, and E2E testing
- Docker and Docker Compose support

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| LLM | Google Gemini |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| Tool Protocol | MCP / FastMCP |
| Structured Output | Pydantic |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Flight / Hotel / Places | SerpApi |
| Weather | Open-Meteo |
| Observability | LangSmith |
| Testing | Pytest |
| Containerization | Docker / Docker Compose |

---

## How the Project Works

TripMate follows this process:

1. The user submits a travel request from the **Streamlit UI**.
2. Streamlit sends the request to the **FastAPI backend**.
3. Gemini extracts structured information such as:
   - Origin
   - Destination
   - Airport codes
   - Travel dates
   - Budget
   - Adults
   - Children
4. The **LangGraph Orchestrator** decides which specialist agents are required.
5. The request is validated before running the agents.
6. Selected specialist agents execute, with independent agents running in parallel where possible:
   - Flight Agent
   - Hotel Agent
   - Weather Agent
   - Places Agent
7. Specialist agents access external services through **MCP/FastMCP tools**.
8. The **Itinerary Agent** combines the available specialist results into a grounded day-by-day plan.
9. Previous trip information can be used as supporting memory.
10. Trip information is saved in **PostgreSQL**.
11. FastAPI returns the result to Streamlit.
12. The user sees the final trip plan, specialist outputs, and saved history.

---

## Agent Responsibilities

### Flight Agent

Searches flight information using the `find_flights` MCP tool and SerpApi Google Flights.

Airport codes are kept separate from city names.

Examples:

```text
Mumbai -> BOM
Delhi -> DEL
Dubai -> DXB
Bangkok -> BKK
Singapore -> SIN
Jeddah -> JED
Paris -> CDG
```

### Hotel Agent

Searches hotels using the actual geographic destination through SerpApi Google Hotels.

### Weather Agent

Retrieves current destination weather using Open-Meteo.

### Places Agent

Finds attractions, landmarks, activities, and other places using SerpApi Google Maps.

### Itinerary Agent

Combines available specialist results into a grounded day-by-day itinerary.

### Orchestrator Agent

Determines which agents are required based on the user's request.

---

## Project Structure

```text
TripMate/
├── src/
│   └── tripmate/
│       ├── agents/
│       ├── api/
│       ├── database/
│       ├── graph/
│       ├── llm/
│       ├── mcp/
│       │   └── servers/
│       ├── providers/
│       ├── services/
│       ├── tools/
│       ├── ui/
│       ├── config.py
│       ├── schemas.py
│       └── state.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── evals/
├── migrations/
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── README.md
```

---

# How to Run the Project

## Prerequisites

Install:

- Python 3.12+
- Git
- PostgreSQL
- Docker Desktop
- Docker Compose

You also need:

- Google Gemini API key
- SerpApi API key
- LangSmith API key if tracing is enabled

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/Sohail-m09/TripMate-AI.git
cd TripMate-AI
```

---

## Step 2 — Create Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Step 3 — Install Dependencies

```powershell
pip install --upgrade pip
pip install -e .
```

For development and testing:

```powershell
pip install -e ".[dev]"
```

---

## Step 4 — Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

SERPAPI_API_KEY=your_serpapi_api_key

DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5433/tripmate_db

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=TripMate-AI
```

Never commit API keys.

Keep these files in `.gitignore`:

```text
.env
.env.docker
.venv/
__pycache__/
```

---

## Step 5 — Create PostgreSQL Database

Create:

```sql
CREATE DATABASE tripmate_db;
```

If your PostgreSQL configuration is different, update:

```text
DATABASE_URL
```

accordingly.

---

## Step 6 — Run Database Migrations

```powershell
alembic upgrade head
```

---

# Option 1 — Run Without Docker

## Step 7 — Start FastAPI

```powershell
uvicorn tripmate.api.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Step 8 — Start Streamlit

Open another terminal.

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
streamlit run src/tripmate/ui/app.py
```

Frontend:

```text
http://localhost:8501
```

---

# Option 2 — Run With Docker

This is the recommended way to run TripMate.

## Step 7 — Create `.env.docker`

Create:

```text
.env.docker
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

SERPAPI_API_KEY=your_serpapi_api_key

DATABASE_URL=postgresql+asyncpg://postgres:your_password@host.docker.internal:5433/tripmate_db

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=TripMate-AI
```

For local execution PostgreSQL uses:

```text
localhost:5433
```

For Docker it uses:

```text
host.docker.internal:5433
```

because `localhost` inside a Docker container refers to the container itself.

---

## Step 8 — Build and Start Containers

```powershell
docker compose up --build -d
```

---

## Step 9 — Check Containers

```powershell
docker compose ps
```

You should see:

```text
tripmate-api
tripmate-ui
```

running.

---

## Step 10 — Test Backend Connection

```powershell
docker exec tripmate-ui python -c "import os,httpx; u=os.getenv('API_BASE_URL'); print(httpx.get(u + '/health').json())"
```

Expected output:

```text
{'status': 'healthy', 'service': 'tripmate-api'}
```

---

## Step 11 — Verify MCP

```powershell
docker exec tripmate-api python -m tripmate.mcp.client
```

Example successful output:

```text
['find_places']
```

---

## Step 12 — Open the Application

Streamlit:

```text
http://localhost:8501
```

FastAPI:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Step 13 — Stop the Project

```powershell
docker compose down
```

---

## Rebuild After Code Changes

Whenever Python source code changes:

```powershell
docker compose down
docker compose up --build -d
```

Then verify:

```powershell
docker compose ps
```

---

# Example Trip Request

Use:

```text
Plan a trip from Delhi to Bangkok, Thailand from 5 December 2026
to 10 December 2026 for 2 adults with a budget of ₹1,20,000.

Find flights, hotels, current weather, tourist attractions,
and create a complete day-by-day itinerary.
```

The extractor should identify information similar to:

```text
Origin: Delhi
Origin Airport: DEL
Destination: Bangkok
Destination Airport: BKK
Destination Country: Thailand
Start Date: 2026-12-05
End Date: 2026-12-10
Adults: 2
Budget: ₹1,20,000
```

The orchestrator can then select:

```text
flight
hotel
weather
places
itinerary
```

---

# Testing

Run all tests:

```powershell
python -m pytest
```

Verbose mode:

```powershell
python -m pytest -v
```

Run unit tests:

```powershell
python -m pytest tests/unit -v
```

Run a specific test:

```powershell
python -m pytest tests/unit/test_agent_inputs.py -v
```

The completed project test suite reached:

```text
122 tests passed
```

---

# LangSmith Evaluation

TripMate uses LangSmith to trace and evaluate Agentic AI behaviour.

Evaluation covers:

- Agent routing
- Trip extraction
- Tool usage
- Agent completion
- Itinerary grounding
- Information coverage
- End-to-end traces
- Experiment comparison

Run routing evaluation:

```powershell
python evals/test_routing_eval.py
```

Run extraction evaluation:

```powershell
python evals/test_extraction_eval.py
```

Run LangSmith experiment:

```powershell
python evals/run_langsmith_experiment.py
```

Evaluation dataset:

```text
TripMate Evaluation Dataset v1
```

---

# Main API Endpoints

```text
GET  /health
POST /trips/plan
GET  /trips/history/{user_id}
```

API documentation:

```text
http://localhost:8000/docs
```

---

# Reliability

TripMate follows several rules to keep responses grounded:

- Flight information comes only from flight-tool results.
- Hotel information comes only from hotel-tool results.
- Weather information comes from Open-Meteo.
- Places information comes from live search results.
- Specialist agents only use tools related to their domain.
- Invalid requests are stopped during validation.
- Failed specialist agents do not automatically stop other agents.
- Partial results can still be returned when one external provider fails.
- The itinerary agent does not invent unavailable travel information.
- Current trip details always take priority over previous trip memory.

---

# What This Project Demonstrates

TripMate demonstrates:

- Agentic AI
- Multi-agent systems
- LangGraph StateGraph
- Conditional routing
- Parallel execution
- Structured LLM outputs
- Tool calling
- MCP / FastMCP
- External API integration
- State management
- Validation
- Error handling
- Agent memory
- PostgreSQL persistence
- FastAPI development
- Streamlit development
- Docker containerization
- LangSmith observability
- LLM evaluation
- Agent evaluation
- Automated testing

---

# Project Status

TripMate AI is completed as a portfolio project.

Implemented:

- LangGraph multi-agent workflow
- Intelligent orchestration
- Parallel specialist agents
- Live travel tools
- MCP/FastMCP integration
- Grounded itinerary generation
- Memory
- PostgreSQL persistence
- FastAPI backend
- Streamlit frontend
- LangSmith tracing
- Agent and LLM evaluation
- Automated testing
- Docker
- Docker Compose
- End-to-end containerized execution

---

## Author

**Momin Sohail Amir**

Computer Engineering Graduate  
AI / Generative AI / Agentic AI Developer

GitHub: [Sohail-m09](https://github.com/Sohail-m09)

---

## Disclaimer

TripMate AI is an educational and portfolio project.

Flight availability, hotel availability, prices, weather information, and attraction details depend on third-party APIs and may change over time. Users should verify important travel information with official providers before making bookings.
