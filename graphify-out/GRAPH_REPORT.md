# Graph Report - .  (2026-07-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 582 nodes · 1796 edges · 30 communities (28 shown, 2 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7772705f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21

## God Nodes (most connected - your core abstractions)
1. `i()` - 90 edges
2. `n()` - 65 edges
3. `t()` - 58 edges
4. `r()` - 54 edges
5. `a()` - 43 edges
6. `pc()` - 40 edges
7. `wd()` - 26 edges
8. `o()` - 25 edges
9. `c()` - 24 edges
10. `hc()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `DashboardPage()` --indirect_call--> `v()`  [INFERRED]
  NutriMitra/client/src/pages/DashboardPage.tsx → NutriMitra/server/static/assets/index-BpIgzvCI.js
- `register()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py
- `login()` --indirect_call--> `User`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/auth.py → NutriMitra/server/app/models/user.py
- `list_foods()` --indirect_call--> `FoodItem`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/food.py → NutriMitra/server/app/models/food_item.py
- `generate_plan()` --indirect_call--> `FoodItem`  [INFERRED]
  NutriMitra/server/app/api/v1/routes/recommendations.py → NutriMitra/server/app/models/food_item.py

## Import Cycles
- None detected.

## Communities (30 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (62): BaseSettings, DeclarativeBase, FastAPI, HTTPAuthorizationCredentials, ndarray, login(), Session, register() (+54 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (85): a(), ae(), an(), as(), b(), bd(), bi(), Bo() (+77 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (61): aa(), Ac(), af(), ao(), bc(), be(), ca(), cf() (+53 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (52): at(), Au(), Bt(), cd(), Cu(), dt(), et(), Eu() (+44 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (39): autoprefixer, dependencies, react, react-dom, react-router-dom, @tailwindcss/vite, devDependencies, autoprefixer (+31 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (24): bs(), componentDidCatch(), ct(), df(), es(), Ge(), He(), hs() (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (18): getMe(), getRecommendations(), login(), register(), request(), DashboardPage(), UserProfile, RegisterPage() (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (28): ad(), ar(), bu(), cr(), dr(), Ed(), fr(), Gd() (+20 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (23): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+15 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (17): cs(), ds(), fs(), Fu(), gs(), Iu(), ks(), mu() (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.18
Nodes (15): bl(), ef(), gf(), Hf(), hl(), If(), jf(), jl() (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.24
Nodes (13): ce(), De(), Ee(), Er(), fe(), ie(), ke(), oe() (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.23
Nodes (12): ba(), ci(), dd(), di(), fi(), Ii(), is(), li() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.23
Nodes (12): dl(), el(), gl(), kl(), ol(), pf(), Qd(), ul() (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.31
Nodes (9): cl(), fl(), gc(), Il(), Ll(), Nl(), no(), pl() (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (7): ap(), dp(), kp(), tp(), un(), wp(), wt()

### Community 17 - "Community 17"
Cohesion: 0.38
Nodes (7): bn(), En(), jn(), Kn(), mn(), pn(), yn()

### Community 18 - "Community 18"
Cohesion: 0.40
Nodes (5): jr(), Mr(), Nr(), Pr(), Ru()

### Community 19 - "Community 19"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Knowledge Gaps
- **67 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `$schema`, `typescript`, `oxc` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `v()` connect `Community 6` to `Community 1`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `i()` (e.g. with `as()` and `b()`) actually correct?**
  _`i()` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `n()` (e.g. with `as()` and `bd()`) actually correct?**
  _`n()` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `t()` (e.g. with `ao()` and `ap()`) actually correct?**
  _`t()` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `r()` (e.g. with `as()` and `bd()`) actually correct?**
  _`r()` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `a()` (e.g. with `it()` and `as()`) actually correct?**
  _`a()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `$schema` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._