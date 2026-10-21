# Graph Report - Diet System  (2026-10-21)

## Corpus Check
- 66 files · ~91,954 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 875 nodes · 2383 edges · 67 communities (55 shown, 12 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1ecca4b4`
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
- Ru
- AGENTS.md
- build_feature_matrix
- dl
- medical_rules.py
- a
- FoodBrowsePage.tsx
- devDependencies
- ne
- RegisterPage.tsx
- nutrition.ts
- qt
- Fix Summary: NutriMitra Meal Plan Zero Calories Issue
- If
- vercel.json
- request
- s
- plugins
- NutriMitra Project Charter
- package.json
- scripts
- autoprefixer
- jsdom
- postcss
- @testing-library/user-event
- @types/react
- @types/react-dom
- typescript
- vite
- @vitejs/plugin-react

## God Nodes (most connected - your core abstractions)
1. `i()` - 81 edges
2. `n()` - 57 edges
3. `r()` - 48 edges
4. `t()` - 46 edges
5. `a()` - 37 edges
6. `nc()` - 37 edges
7. `FoodItem` - 30 edges
8. `o()` - 30 edges
9. `wd()` - 27 edges
10. `vc()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `request()` --indirect_call--> `d()`  [INFERRED]
  NutriMitra/client/src/api.ts → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `DashboardPage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `ProfileCard()` --indirect_call--> `v()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `FoodBrowsePage()` --indirect_call--> `t()`  [INFERRED]
  NutriMitra/client/src/pages/FoodBrowsePage.tsx → NutriMitra/server/static/assets/index-Ib34DWp8.js
- `register()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py

## Import Cycles
- None detected.

## Communities (67 total, 12 thin omitted)

### Community 0 - "recommendations.py"
Cohesion: 0.06
Nodes (56): ndarray, explain_recommendation(), FoodItem, build_feature_matrix(), filter_by_meal_type(), KNNRecommender, FoodItem, Rank *candidates* by similarity to *targets*. (+48 more)

### Community 1 - "i"
Cohesion: 0.17
Nodes (21): bd(), cd(), cp(), es(), ke(), mp(), n(), pp() (+13 more)

### Community 2 - "hu"
Cohesion: 0.18
Nodes (12): bn(), bs(), De(), Ee(), Gn(), Go(), le(), w() (+4 more)

### Community 3 - "pc"
Cohesion: 0.09
Nodes (31): classify_food(), food_matches_allergens(), _normalised_phrase(), Dietary compatibility rules for NutriMitra.  The nutrition dataset (ICMR-NIN / I, Classify a food record for diet compatibility.      Returns a dict with the flag, True when the food name indicates it contains one of the allergens., tokenize(), client() (+23 more)

### Community 4 - "devDependencies"
Cohesion: 0.22
Nodes (9): dependencies, react, react-dom, react-router-dom, @tailwindcss/vite, react, react-dom, react-router-dom (+1 more)

### Community 5 - "index-CSK9ol_y.js"
Cohesion: 0.15
Nodes (29): An(), Bt(), dt(), E(), $f(), fn(), ft(), Gt() (+21 more)

### Community 6 - "api.ts"
Cohesion: 0.13
Nodes (15): FoodListResponse, MealItem, MealPlan, MealTotals, PlanSummary, ProfileUpdate, RecommendationResponse, SavedPlan (+7 more)

### Community 7 - "wd"
Cohesion: 0.09
Nodes (29): ad(), af(), cs(), df(), ds(), fs(), Gd(), gs() (+21 more)

### Community 8 - "compilerOptions"
Cohesion: 0.08
Nodes (23): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+15 more)

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 10 - "auth.py"
Cohesion: 0.16
Nodes (22): HTTPAuthorizationCredentials, login(), Session, register(), get_current_user(), Session, Save the profile the user edited on the dashboard., read_current_user() (+14 more)

### Community 11 - "FoodItem"
Cohesion: 0.12
Nodes (34): candidate_data_dirs(), _clean_float(), DatasetError, _deduplicate_foods(), find_dataset(), _food_from_primary(), _food_from_supplement(), _import_foods() (+26 more)

### Community 12 - "vl"
Cohesion: 0.26
Nodes (17): ar(), Br(), cr(), dr(), Ed(), hn(), ir(), mn() (+9 more)

### Community 13 - "NutriMitra"
Cohesion: 0.15
Nodes (12): 1. Backend, 2. Frontend (Development Mode), API Endpoints, Dataset, Features, ML Pipeline, NutriMitra, Prerequisites (+4 more)

### Community 14 - "main.py"
Cohesion: 0.10
Nodes (18): BaseSettings, Exception, Config, Settings, ensure_schema(), get_db(), _get_engine(), Turn the configured DATABASE_URL into a usable SQLAlchemy URL.      ``DATABASE_U (+10 more)

### Community 15 - "sl"
Cohesion: 0.30
Nodes (12): DeclarativeBase, delete_plan(), get_plan(), list_plans(), _load_meal_plan(), MealPlan, Session, _to_summary() (+4 more)

### Community 16 - "dl"
Cohesion: 0.20
Nodes (19): Au(), Cu(), Du(), et(), Eu(), gu(), id(), Je() (+11 more)

### Community 17 - "se"
Cohesion: 0.11
Nodes (25): ap(), at(), bu(), dp(), He(), hu(), ip(), kp() (+17 more)

### Community 18 - "routes/food.py"
Cohesion: 0.31
Nodes (7): FastAPI, list_categories(), list_foods(), Session, FoodListResponse, FoodOut, BaseModel

### Community 19 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 30 - "Kt"
Cohesion: 0.19
Nodes (16): ci(), dd(), Fu(), is(), Iu(), jo(), ms(), ns() (+8 more)

### Community 31 - "Ge"
Cohesion: 0.06
Nodes (80): aa(), ac(), ae(), ao(), ba(), Bc(), be(), bi() (+72 more)

### Community 32 - "pdf_extractor.py"
Cohesion: 0.39
Nodes (6): extract_tables(), _float(), _match_column(), _normalise(), Extract Indian food composition tables from PDF (ICMR-NIN format) using pdfplumb, records_to_db()

### Community 33 - "ds"
Cohesion: 0.24
Nodes (10): ec(), fc(), Ic(), qa(), rc(), tc(), wc(), wi() (+2 more)

### Community 35 - "Ru"
Cohesion: 0.21
Nodes (17): bl(), cl(), el(), eo(), fl(), Hf(), Il(), Ll() (+9 more)

### Community 38 - "build_feature_matrix"
Cohesion: 0.11
Nodes (30): MealItem, _effective_profile(), generate_plan(), Session, Merge the requested profile with the stored one., allergen_tokens(), normalise_allergens(), Split a free text allergy list into supported groups and the rest.      Returns (+22 more)

### Community 39 - "dl"
Cohesion: 0.18
Nodes (17): dl(), gl(), jr(), kl(), Nr(), ol(), pa(), pf() (+9 more)

### Community 40 - "medical_rules.py"
Cohesion: 0.18
Nodes (15): _acid_reflux(), apply_medical_rules(), ConditionRule, _diabetes(), get_restriction_tags(), _heart_disease(), _hypertension(), _kidney_disease() (+7 more)

### Community 41 - "a"
Cohesion: 0.23
Nodes (16): a(), Cn(), d(), dn(), en(), ep(), fe(), jd() (+8 more)

### Community 42 - "FoodBrowsePage.tsx"
Cohesion: 0.19
Nodes (6): FoodItem, getFoodCategories(), getFoods(), fmt(), FoodBrowsePage(), react

### Community 43 - "devDependencies"
Cohesion: 0.15
Nodes (13): devDependencies, oxlint, tailwindcss, @testing-library/jest-dom, @testing-library/react, @types/node, vitest, oxlint (+5 more)

### Community 44 - "ne"
Cohesion: 0.26
Nodes (13): b(), ce(), ie(), m(), ne(), oe(), p(), pn() (+5 more)

### Community 45 - "RegisterPage.tsx"
Cohesion: 0.21
Nodes (7): login(), register(), ThaliRing(), ThaliRingProps, ThaliSegment, HERO_CHIPS, RegisterPage()

### Community 46 - "nutrition.ts"
Cohesion: 0.17
Nodes (11): ACTIVITY_FACTORS, ACTIVITY_LEVELS, DIET_TYPES, EstimatedTargets, estimateTargets(), GENDERS, MACRO_SPLITS, ProfileDraft (+3 more)

### Community 47 - "qt"
Cohesion: 0.22
Nodes (11): ProfileCard(), fd(), Jt(), kt(), Nd(), nn(), pd(), Q() (+3 more)

### Community 48 - "Fix Summary: NutriMitra Meal Plan Zero Calories Issue"
Cohesion: 0.20
Nodes (9): 1. Database Path Configuration (`server/app/core/config.py`), 2. Database Seeding Logic (`server/app/main.py`), 3. Data Seeding Script Enhancement (`server/app/data/seed_foods.py`), Deployment Instructions, Files Modified, Fix Summary: NutriMitra Meal Plan Zero Calories Issue, Root Cause, Specific Issues Fixed (+1 more)

### Community 49 - "If"
Cohesion: 0.27
Nodes (10): ef(), gf(), hl(), If(), jf(), jl(), kf(), Lf() (+2 more)

### Community 50 - "vercel.json"
Cohesion: 0.20
Nodes (9): framework, root, rewrites, $schema, framework, root, services, client (+1 more)

### Community 51 - "request"
Cohesion: 0.36
Nodes (9): deletePlan(), getMe(), getPlan(), getPlans(), getRecommendations(), request(), updateProfile(), validateProfile() (+1 more)

### Community 52 - "s"
Cohesion: 0.31
Nodes (9): Er(), fr(), gr(), hr(), lr(), s(), Tr(), wr() (+1 more)

### Community 53 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 54 - "NutriMitra Project Charter"
Cohesion: 0.22
Nodes (8): Approval & Signature, Deliverables, In Scope, NutriMitra Project Charter, Out of Scope, Project Timeline (90 Days), Purpose & Goals, Technologies Used

### Community 55 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 56 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

## Knowledge Gaps
- **115 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `$schema`, `typescript`, `oxc` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `vl` to `i`, `hu`, `index-CSK9ol_y.js`, `wd`, `a`, `FoodBrowsePage.tsx`, `ne`, `qt`, `se`, `request`, `s`, `Ge`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `DashboardPage()` connect `request` to `nutrition.ts`, `vl`, `api.ts`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `FoodItem` connect `build_feature_matrix` to `pdf_extractor.py`, `recommendations.py`, `pc`, `medical_rules.py`, `FoodItem`, `main.py`, `sl`, `routes/food.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `i()` (e.g. with `ae()` and `b()`) actually correct?**
  _`i()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `n()` (e.g. with `at()` and `bd()`) actually correct?**
  _`n()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `r()` (e.g. with `ac()` and `at()`) actually correct?**
  _`r()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `t()` (e.g. with `DashboardPage()` and `FoodBrowsePage()`) actually correct?**
  _`t()` has 29 INFERRED edges - model-reasoned connections that need verification._