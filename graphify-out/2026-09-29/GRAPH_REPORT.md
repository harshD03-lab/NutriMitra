# Graph Report - Diet System  (2026-08-02)

## Corpus Check
- 51 files · ~18,080 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 654 nodes · 1952 edges · 39 communities (36 shown, 3 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `79046278`
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
- lc
- build_feature_matrix

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
- `ProfileCard()` --indirect_call--> `v()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `FoodBrowsePage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/FoodBrowsePage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `register()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py
- `login()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py

## Import Cycles
- None detected.

## Communities (39 total, 3 thin omitted)

### Community 0 - "recommendations.py"
Cohesion: 0.17
Nodes (20): generate_plan(), Session, _resolve(), explain_recommendation(), FoodItem, get_restriction_tags(), hard_filter(), FoodItem (+12 more)

### Community 1 - "i"
Cohesion: 0.07
Nodes (88): a(), at(), b(), ba(), bd(), bn(), Br(), ca() (+80 more)

### Community 2 - "hu"
Cohesion: 0.20
Nodes (18): bi(), cc(), ct(), Du(), fc(), gi(), hi(), lo() (+10 more)

### Community 3 - "pc"
Cohesion: 0.24
Nodes (15): cl(), el(), eo(), fl(), ia(), Il(), jc(), Ll() (+7 more)

### Community 4 - "devDependencies"
Cohesion: 0.05
Nodes (39): autoprefixer, dependencies, react, react-dom, react-router-dom, @tailwindcss/vite, devDependencies, autoprefixer (+31 more)

### Community 5 - "index-CSK9ol_y.js"
Cohesion: 0.10
Nodes (39): ae(), An(), Bt(), Cn(), $f(), fd(), fn(), ft() (+31 more)

### Community 6 - "api.ts"
Cohesion: 0.06
Nodes (38): deletePlan(), FoodItem, FoodListResponse, getFoodCategories(), getFoods(), getMe(), getPlan(), getPlans() (+30 more)

### Community 7 - "wd"
Cohesion: 0.07
Nodes (34): af(), Bo(), bs(), cs(), df(), Go(), gs(), Hd() (+26 more)

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
Cohesion: 0.12
Nodes (32): ProfileCard(), ad(), ar(), cr(), dp(), dr(), Ed(), Er() (+24 more)

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
Cohesion: 0.13
Nodes (29): Au(), bu(), Cu(), et(), Eu(), gu(), He(), hu() (+21 more)

### Community 17 - "se"
Cohesion: 0.21
Nodes (11): ap(), ci(), di(), fs(), ip(), kp(), li(), lt() (+3 more)

### Community 18 - "routes/food.py"
Cohesion: 0.46
Nodes (6): list_categories(), list_foods(), Session, FoodListResponse, FoodOut, BaseModel

### Community 19 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 30 - "Kt"
Cohesion: 0.30
Nodes (15): Bc(), be(), ea(), fe(), Fu(), Ga(), Iu(), Ji() (+7 more)

### Community 31 - "Ge"
Cohesion: 0.16
Nodes (21): aa(), ac(), C(), cf(), componentDidCatch(), Do(), Fi(), gc() (+13 more)

### Community 32 - "pdf_extractor.py"
Cohesion: 0.39
Nodes (6): extract_tables(), _float(), _match_column(), _normalise(), Extract Indian food composition tables from PDF (ICMR-NIN format) using pdfplumb, records_to_db()

### Community 33 - "ds"
Cohesion: 0.22
Nodes (9): ec(), Ic(), np(), qa(), tc(), tp(), wc(), wp() (+1 more)

### Community 34 - "hard_filter.py"
Cohesion: 0.21
Nodes (15): dl(), gl(), jr(), kl(), Nr(), ol(), pa(), Pr() (+7 more)

### Community 35 - "Ru"
Cohesion: 0.20
Nodes (14): bl(), ef(), gf(), Hf(), hl(), If(), jf(), jl() (+6 more)

### Community 37 - "lc"
Cohesion: 0.25
Nodes (11): ao(), dc(), fo(), kr(), ks(), lc(), na(), oa() (+3 more)

### Community 38 - "build_feature_matrix"
Cohesion: 0.67
Nodes (3): ndarray, build_feature_matrix(), FoodItem

## Knowledge Gaps
- **83 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `$schema`, `typescript`, `oxc` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `i` to `ds`, `hu`, `index-CSK9ol_y.js`, `api.ts`, `wd`, `vl`, `se`, `Kt`, `Ge`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `DashboardPage()` connect `api.ts` to `i`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `FoodBrowsePage()` connect `api.ts` to `i`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `i()` (e.g. with `ae()` and `b()`) actually correct?**
  _`i()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `n()` (e.g. with `at()` and `bd()`) actually correct?**
  _`n()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `r()` (e.g. with `ac()` and `at()`) actually correct?**
  _`r()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `t()` (e.g. with `DashboardPage()` and `FoodBrowsePage()`) actually correct?**
  _`t()` has 29 INFERRED edges - model-reasoned connections that need verification._