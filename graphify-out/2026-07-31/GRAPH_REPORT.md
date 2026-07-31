# Graph Report - Diet System  (2026-07-31)

## Corpus Check
- 48 files · ~15,348 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 622 nodes · 1871 edges · 37 communities (34 shown, 3 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 283 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5f908163`
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
1. `i()` - 89 edges
2. `n()` - 64 edges
3. `t()` - 58 edges
4. `r()` - 52 edges
5. `a()` - 43 edges
6. `pc()` - 40 edges
7. `o()` - 28 edges
8. `wd()` - 26 edges
9. `hc()` - 25 edges
10. `s()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `FoodBrowsePage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/FoodBrowsePage.tsx → NutriMitra/server/static/assets/index-CSK9ol_y.js
- `list_foods()` --indirect_call--> `FoodItem`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/food.py → NutriMitra/server/app/models/food_item.py
- `generate_plan()` --indirect_call--> `FoodItem`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/recommendations.py → NutriMitra/server/app/models/food_item.py
- `User` --uses--> `Base`  [INFERRED]
  NutriMitra/server/app/models/user.py → NutriMitra/server/app/core/database.py
- `KNNRecommender` --uses--> `FoodItem`  [INFERRED]
  NutriMitra/server/app/ml/knn_recommender.py → NutriMitra/server/app/models/food_item.py

## Import Cycles
- None detected.

## Communities (37 total, 3 thin omitted)

### Community 0 - "recommendations.py"
Cohesion: 0.16
Nodes (20): ndarray, generate_plan(), Session, _resolve(), explain_recommendation(), FoodItem, build_feature_matrix(), KNNRecommender (+12 more)

### Community 1 - "i"
Cohesion: 0.06
Nodes (116): a(), an(), as(), at(), b(), bd(), bi(), Bo() (+108 more)

### Community 2 - "hu"
Cohesion: 0.07
Nodes (53): ap(), Au(), ba(), bu(), ci(), Cu(), dd(), di() (+45 more)

### Community 3 - "pc"
Cohesion: 0.09
Nodes (51): aa(), Ac(), ao(), bc(), be(), cf(), dc(), Do() (+43 more)

### Community 4 - "devDependencies"
Cohesion: 0.05
Nodes (39): autoprefixer, dependencies, react, react-dom, react-router-dom, @tailwindcss/vite, devDependencies, autoprefixer (+31 more)

### Community 5 - "index-CSK9ol_y.js"
Cohesion: 0.09
Nodes (21): bn(), ca(), fs(), Fu(), hs(), Io(), Iu(), la() (+13 more)

### Community 6 - "api.ts"
Cohesion: 0.08
Nodes (27): FoodItem, FoodListResponse, getFoodCategories(), getFoods(), getMe(), getRecommendations(), login(), MealItem (+19 more)

### Community 7 - "wd"
Cohesion: 0.12
Nodes (33): ad(), ar(), C(), ce(), cr(), Dn(), dr(), Ed() (+25 more)

### Community 8 - "compilerOptions"
Cohesion: 0.08
Nodes (23): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+15 more)

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 10 - "auth.py"
Cohesion: 0.20
Nodes (18): HTTPAuthorizationCredentials, login(), Session, register(), get_current_user(), Session, read_current_user(), create_access_token() (+10 more)

### Community 11 - "FoodItem"
Cohesion: 0.27
Nodes (10): DeclarativeBase, Base, _build_col_map(), _float(), _int_or_none(), load_icmr_data(), _normalise(), ICMR-NIN / Indian Food Nutrition CSV processing script.  Reads a food compositio (+2 more)

### Community 12 - "vl"
Cohesion: 0.20
Nodes (14): bl(), ef(), gf(), Hf(), hl(), If(), jf(), jl() (+6 more)

### Community 13 - "NutriMitra"
Cohesion: 0.14
Nodes (13): 1. Backend, 2. Frontend (Development Mode), API Endpoints, Dataset, Features, License, ML Pipeline, NutriMitra (+5 more)

### Community 14 - "main.py"
Cohesion: 0.20
Nodes (5): BaseSettings, FastAPI, Config, Settings, lifespan()

### Community 15 - "sl"
Cohesion: 0.26
Nodes (12): cl(), fl(), gc(), Il(), Ll(), Nl(), no(), pl() (+4 more)

### Community 16 - "dl"
Cohesion: 0.23
Nodes (12): dl(), el(), gl(), kl(), ol(), pf(), Qd(), ul() (+4 more)

### Community 17 - "se"
Cohesion: 0.22
Nodes (10): ae(), De(), Ee(), Er(), ke(), le(), os(), re() (+2 more)

### Community 18 - "routes/food.py"
Cohesion: 0.39
Nodes (7): list_categories(), list_foods(), Session, get_db(), FoodListResponse, FoodOut, BaseModel

### Community 19 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 30 - "Kt"
Cohesion: 0.22
Nodes (9): af(), es(), go(), In(), Kt(), of(), qo(), tf() (+1 more)

### Community 31 - "Ge"
Cohesion: 0.22
Nodes (9): bs(), ct(), df(), Ge(), He(), ss(), w(), xa() (+1 more)

### Community 32 - "pdf_extractor.py"
Cohesion: 0.39
Nodes (6): extract_tables(), _float(), _match_column(), _normalise(), Extract Indian food composition tables from PDF (ICMR-NIN format) using pdfplumb, records_to_db()

### Community 33 - "ds"
Cohesion: 0.40
Nodes (5): ds(), gs(), ks(), yf(), ys()

### Community 34 - "hard_filter.py"
Cohesion: 0.67
Nodes (3): get_restriction_tags(), hard_filter(), FoodItem

### Community 35 - "Ru"
Cohesion: 0.50
Nodes (4): jr(), Mr(), Nr(), Ru()

## Knowledge Gaps
- **79 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `$schema`, `typescript`, `oxc` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `i` to `hu`, `pc`, `index-CSK9ol_y.js`, `api.ts`, `wd`, `sl`, `se`, `Kt`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `v()` connect `api.ts` to `i`, `index-CSK9ol_y.js`, `wd`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `FoodBrowsePage()` connect `api.ts` to `i`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `i()` (e.g. with `ae()` and `as()`) actually correct?**
  _`i()` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `n()` (e.g. with `as()` and `bd()`) actually correct?**
  _`n()` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `t()` (e.g. with `FoodBrowsePage()` and `ao()`) actually correct?**
  _`t()` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `r()` (e.g. with `as()` and `bd()`) actually correct?**
  _`r()` has 39 INFERRED edges - model-reasoned connections that need verification._