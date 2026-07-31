# NutriMitra

**AI-Powered Personalized Diet Recommendation System for India**

NutriMitra is a final-year ML project that generates personalized daily meal plans using content-based filtering (kNN) with ICMR-NIN public nutrition data. Recommendations are tailored to the user's body metrics, activity level, dietary preferences, and medical conditions.

---

## Features

- **Register / Login** — JWT-based authentication
- **Health Profile** — Age, gender, height, weight, activity level, diet type
- **Medical Safety Layer** — Hard-filter that excludes unsafe foods for conditions like diabetes, hypertension, kidney disease, PCOS, and heart disease
- **AI Recommendations** — k-Nearest Neighbors (cosine distance) finds the closest-matching foods for your daily nutrition targets
- **Nutrition Engine** — Mifflin-St Jeor BMR → TDEE → macro/micronutrient targets
- **Plan History** — Every generated plan is saved automatically; browse, reload, or delete past plans
- **Food Browse** — Search the Indian food database with pagination and category filters
- **Indian Food Database** — Built to ingest the ICMR-NIN Indian food composition dataset

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| **Backend** | Python 3.12 + FastAPI |
| **ML** | scikit-learn (NearestNeighbors), pandas, NumPy |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **Auth** | bcrypt hashing + JWT (python-jose) |

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+

### 1. Backend

```powershell
cd NutriMitra\server
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API + frontend are served together at **http://127.0.0.1:8000**.

### 2. Frontend (Development Mode)

```powershell
cd NutriMitra\client
npm install
npx vite --host 127.0.0.1 --port 5173
```

Opens at **http://127.0.0.1:5173** (proxies API calls to port 8000).

---

## Project Structure

```
NutriMitra/
├── client/                     # React frontend
│   ├── src/
│   │   ├── pages/              # RegisterPage, DashboardPage, FoodBrowsePage
│   │   ├── Layout.tsx          # App shell with nav
│   │   ├── api.ts              # Typed API client
│   │   └── main.tsx            # Entry point with router
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── server/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app (serves API + frontend)
│   │   ├── core/               # Config, DB, Security
│   │   ├── models/             # User, FoodItem, DietPlan ORM
│   │   ├── schemas/            # Pydantic validation
│   │   ├── api/v1/routes/      # auth, users, food, recommendations, plans
│   │   ├── ml/                 # ML engine
│   │   │   ├── nutrient_engine.py   # BMR/TDEE/macro calculator
│   │   │   ├── hard_filter.py       # Medical condition filter
│   │   │   ├── knn_recommender.py   # kNN content-based filtering
│   │   │   └── explainability.py    # Recommendation explanation
│   │   └── data/               # Dataset import + PDF extractor scripts
│   ├── static/                 # Built frontend (auto-served)
│   ├── requirements.txt
│   └── .env.example
│
└── AGENTS.md                   # Agent instructions
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/v1/auth/register` | Create account |
| POST | `/v1/auth/login` | Get JWT token |
| GET | `/v1/users/me` | Current user profile |
| GET | `/v1/food/` | List/search food items (q, category, skip, limit) |
| GET | `/v1/food/categories` | Distinct food categories |
| POST | `/v1/recommendations/` | Generate meal plan (auto-saved to history) |
| GET | `/v1/plans/` | List current user's saved plans |
| GET | `/v1/plans/{id}` | Full saved plan with meal items |
| DELETE | `/v1/plans/{id}` | Delete a saved plan |

---

## ML Pipeline

```
User Profile → Nutrient Engine (BMR/TDEE) → Hard Filter (medical safety)
    → kNN Recommender (cosine similarity) → Explainability → Meal Plan
```

1. **Nutrient Engine** — Calculates BMR (Mifflin-St Jeor), TDEE using activity multiplier, and splits macros based on diet type (balanced / low-carb / high-protein)
2. **Hard Filter** — Strips foods tagged with restriction tags matching the user's medical conditions
3. **kNN Recommender** — Uses scikit-learn `NearestNeighbors` with cosine distance to find foods closest to the user's nutrient target vector
4. **Explainability** — Generates human-readable reasons for each recommendation

---

## Dataset

The project is designed to work with the **ICMR-National Institute of Nutrition (NIN) Indian Food Composition Database**. The database is currently seeded with **1,014 foods** imported from a processed CSV; the seed script auto-detects and maps diverse column name formats. A `pdf_extractor` script is also included for parsing the full **IFCT2017** dataset (585 pages, PDF is gitignored).

```powershell
cd NutriMitra\server
.\venv\Scripts\python -m app.data.seed_foods data/raw/indian_food.csv
```

---

## Status

- ✅ Phase 1: Backend Foundation (auth, DB, models, routes)
- ✅ Phase 2: ML Engine (nutrient targets, hard filter, kNN)
- ✅ Phase 3: Recommendations UI (wire frontend to ML endpoint)
- ✅ Phase 4: Dataset import + food browse
- ✅ Phase 5: Diet plan history
- ⬜ Phase 6: Polish, testing, deployment

---

## License

MIT
