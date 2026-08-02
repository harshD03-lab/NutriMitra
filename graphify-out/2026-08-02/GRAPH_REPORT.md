# Graph Report - Diet System  (2026-07-31)

## Corpus Check
- 50 files · ~16,166 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 639 nodes · 1933 edges · 37 communities (34 shown, 3 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b0479af9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- recommendations.py
- i
- hu
- pc
- devDependencies
- index-CSK9ol_y.js
- api.ts
- wd
- compilerOptions
- compilerOptions
- auth.py
- FoodItem
- vl
- NutriMitra
- main.py
- sl
- dl
- se
- routes/food.py
- opencode.json
- tsconfig.json
- graphify.js
- Kt
- Ge
- pdf_extractor.py
- ds
- hard_filter.py
- Ru
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `i()` - 81 edges
2. `n()` - 57 edges
3. `r()` - 48 edges
4. `t()` - 46 edges
5. `a()` - 37 edges
6. `nc()` - 37 edges
7. `o()` - 30 edges
8. `wd()` - 27 edges
9. `vc()` - 26 edges
10. `cc()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `DashboardPage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `DashboardPage()` --indirect_call--> `v()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `FoodBrowsePage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/FoodBrowsePage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `register()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py
- `login()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py

## Import Cycles
- None detected.

## Communities (37 total, 3 thin omitted)

### Community 0 - "recommendations.py"
Cohesion: 0.14
Nodes (23): ndarray, generate_plan(), Session, _resolve(), explain_recommendation(), FoodItem, get_restriction_tags(), hard_filter() (+15 more)

### Community 1 - "i"
Cohesion: 0.07
Nodes (85): a(), ac(), ao(), at(), b(), ba(), bd(), Br() (+77 more)

### Community 2 - "hu"
Cohesion: 0.08
Nodes (55): aa(), Bc(), be(), bi(), cc(), cf(), componentDidCatch(), ct() (+47 more)

### Community 3 - "pc"
Cohesion: 0.08
Nodes (47): bl(), cl(), dl(), ef(), el(), eo(), fl(), gf() (+39 more)

### Community 4 - "devDependencies"
Cohesion: 0.05
Nodes (39): autoprefixer, dependencies, react, react-dom, react-router-dom, @tailwindcss/vite, devDependencies, autoprefixer (+31 more)

### Community 5 - "index-CSK9ol_y.js"
Cohesion: 0.11
Nodes (38): ae(), An(), Bt(), Cn(), E(), $f(), fn(), ft() (+30 more)

### Community 6 - "api.ts"
Cohesion: 0.08
Nodes (32): deletePlan(), FoodItem, FoodListResponse, getFoodCategories(), getFoods(), getMe(), getPlan(), getPlans() (+24 more)

### Community 7 - "wd"
Cohesion: 0.08
Nodes (27): af(), bn(), Bo(), bs(), df(), Go(), gs(), ho() (+19 more)

### Community 8 - "compilerOptions"
Cohesion: 0.08
Nodes (23): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+15 more)

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 10 - "auth.py"
Cohesion: 0.30
Nodes (12): login(), Session, register(), create_access_token(), hash_password(), verify_password(), LoginRequest, BaseModel (+4 more)

### Community 11 - "FoodItem"
Cohesion: 0.48
Nodes (6): _build_col_map(), _float(), _int_or_none(), load_icmr_data(), _normalise(), ICMR-NIN / Indian Food Nutrition CSV processing script.  Reads a food compositio

### Community 12 - "vl"
Cohesion: 0.14
Nodes (28): ar(), cr(), dr(), Ed(), Er(), fd(), fr(), gr() (+20 more)

### Community 13 - "NutriMitra"
Cohesion: 0.14
Nodes (13): 1. Backend, 2. Frontend (Development Mode), API Endpoints, Dataset, Features, License, ML Pipeline, NutriMitra (+5 more)

### Community 14 - "main.py"
Cohesion: 0.14
Nodes (11): BaseSettings, FastAPI, HTTPAuthorizationCredentials, get_current_user(), Session, read_current_user(), Config, Settings (+3 more)

### Community 15 - "sl"
Cohesion: 0.23
Nodes (16): DeclarativeBase, MealPlan, delete_plan(), get_plan(), list_plans(), _load_meal_plan(), Session, _to_summary() (+8 more)

### Community 16 - "dl"
Cohesion: 0.22
Nodes (16): Au(), Cu(), et(), Eu(), Je(), ju(), ku(), lt() (+8 more)

### Community 17 - "se"
Cohesion: 0.18
Nodes (14): ap(), di(), dp(), fa(), hu(), ip(), kp(), li() (+6 more)

### Community 18 - "routes/food.py"
Cohesion: 0.46
Nodes (6): list_categories(), list_foods(), Session, FoodListResponse, FoodOut, BaseModel

### Community 19 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 30 - "Kt"
Cohesion: 0.22
Nodes (13): cs(), dd(), Fu(), is(), Iu(), jo(), mu(), Nu() (+5 more)

### Community 31 - "Ge"
Cohesion: 0.32
Nodes (8): ci(), fs(), ns(), si(), st(), ts(), ya(), zs()

### Community 32 - "pdf_extractor.py"
Cohesion: 0.39
Nodes (6): extract_tables(), _float(), _match_column(), _normalise(), Extract Indian food composition tables from PDF (ICMR-NIN format) using pdfplumb, records_to_db()

### Community 33 - "ds"
Cohesion: 0.29
Nodes (8): ec(), np(), qa(), rc(), tc(), tp(), wp(), Xa()

### Community 34 - "hard_filter.py"
Cohesion: 0.40
Nodes (6): bu(), He(), render(), ut(), Uu(), vf()

### Community 35 - "Ru"
Cohesion: 0.50
Nodes (5): ad(), Gd(), ke(), od(), ud()

## Knowledge Gaps
- **79 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `$schema`, `typescript`, `oxc` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `i` to `ds`, `hu`, `index-CSK9ol_y.js`, `api.ts`, `wd`, `vl`, `se`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `DashboardPage()` connect `api.ts` to `i`, `vl`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `v()` connect `vl` to `i`, `api.ts`, `wd`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `i()` (e.g. with `ae()` and `b()`) actually correct?**
  _`i()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `n()` (e.g. with `at()` and `bd()`) actually correct?**
  _`n()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `r()` (e.g. with `ac()` and `at()`) actually correct?**
  _`r()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `t()` (e.g. with `DashboardPage()` and `FoodBrowsePage()`) actually correct?**
  _`t()` has 29 INFERRED edges - model-reasoned connections that need verification._