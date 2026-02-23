# Mozambique Policy Scenarios - Expected Job Impacts

## Three Scenarios Overview

### 1. Agricultural Focus 🌾
**Strategy**: Strengthen agriculture productivity and rural value chains (cashews, sugar, cotton)

**Policy Levers**:
- Agriculture tariff: +10%
- Food processing tariff: +8%
- Agriculture subsidy: +15% GDP
- Food processing subsidy: +10% GDP
- SME stimulus: 1.5% GDP
- Productivity investment: 2% GDP
- Time horizon: 3 years (medium)

**Expected Employment Impact**: MODERATE
- Agriculture has very high labor intensity (168 jobs per $1M)
- But limited backward linkages (indirect effects)
- Low wages → low induced consumption effects
- High informality (88%)
- Primarily benefits existing agricultural workforce (69.5% of employment)

---

### 2. Commodity Extraction ⛏️
**Strategy**: Develop natural gas, coal, and mineral extraction sectors

**Policy Levers**:
- Mining tariff: 0% (no protection)
- Mining subsidy: +12% GDP
- Utilities subsidy: +8% GDP
- Transport subsidy: +6% GDP
- SME stimulus: 0.5% GDP (lowest)
- Productivity investment: 5% GDP
- Time horizon: 5 years (long)

**Expected Employment Impact**: LOWEST
- Mining is extremely capital-intensive (only 8 jobs per $1M)
- Natural gas/coal sectors employ very few workers
- Limited local linkages (equipment mostly imported)
- Benefits concentrated among skilled workers and foreign companies
- Some spillover to construction (infrastructure) and transport

**Reality Check**: This reflects Mozambique's actual challenge with the LNG boom - high revenues but minimal job creation in the extractives sector itself.

---

### 3. Industrialization Drive 🏭
**Strategy**: Push for manufacturing, textiles, and higher value-added production

**Policy Levers**:
- Manufacturing tariff: +20%
- Textiles tariff: +18%
- Food processing tariff: +12%
- Construction tariff: +10%
- Manufacturing subsidy: +25% GDP (highest)
- Textiles subsidy: +20% GDP
- Food processing subsidy: +15% GDP
- Construction subsidy: +12% GDP
- SME stimulus: 2.5% GDP (highest)
- Productivity investment: 7% GDP (highest)
- Time horizon: 5 years (long)

**Expected Employment Impact**: HIGHEST

**Why this creates the most jobs:**

1. **Labor-Intensive Sectors Targeted**:
   - Textiles: 124 jobs per $1M (predominantly female, youth)
   - Construction: 84 jobs per $1M (infrastructure for industry)
   - Food processing: 72 jobs per $1M (links agriculture to industry)
   - Manufacturing: 55 jobs per $1M (diverse products)

2. **Strongest Policy Support**:
   - Highest subsidies across multiple sectors
   - Highest SME stimulus (supports small manufacturers)
   - Highest productivity investment (builds capacity)

3. **Multiplier Effects**:
   - Manufacturing has stronger backward linkages than agriculture
   - Construction creates immediate jobs during buildup
   - Textiles employ large numbers of youth and women
   - Food processing creates bridge between agriculture and industry

4. **Structural Transformation**:
   - Moves workers from low-productivity agriculture (informal, low wages) to higher-productivity manufacturing (more formal, higher wages)
   - Creates induced consumption effects (manufacturing wages → spending → more jobs)
   - Builds industrial base for long-term growth

5. **Formalization**:
   - Manufacturing: 74% informal → potential for formalization
   - Textiles: 68% informal → potential for formalization
   - Better than agriculture's 88% informality

---

## Employment Multipliers Reference (Mozambique)

Direct jobs per $1 million final demand:

| Sector | Direct Jobs | Type II Multiplier | Informal % | Female % | Youth % |
|--------|-------------|-------------------|------------|----------|---------|
| Agriculture | 168 | 195 | 88% | 48% | 24% |
| Textiles | 124 | 154 | 68% | 76% | 32% |
| Construction | 84 | 113 | 78% | 6% | 34% |
| Food Processing | 72 | 119 | 64% | 52% | 28% |
| Manufacturing | 55 | 82 | 74% | 38% | 26% |
| Mining | 8 | 22 | 24% | 6% | 8% |

---

## Model Validation

If the model is working correctly, simulating all three scenarios should show:

1. **Total Jobs Created**: Industrialization > Agriculture > Extraction
2. **Youth Jobs**: Industrialization (textiles, construction) > Agriculture > Extraction
3. **Female Jobs**: Industrialization (textiles, food processing) > Agriculture > Extraction
4. **Formal Jobs**: Industrialization > Extraction > Agriculture
5. **Fiscal Cost**: Industrialization (highest) > Agriculture > Extraction

---

## Policy Implications for Mozambique

**Agricultural Focus**:
- ✅ Builds on existing strengths (69.5% employment)
- ✅ Improves food security
- ❌ Keeps workers in low-productivity, informal sector
- ❌ Limited structural transformation

**Commodity Extraction**:
- ✅ High revenues for government (natural gas boom)
- ✅ Foreign exchange earnings
- ❌ Minimal job creation (capital-intensive)
- ❌ Risk of "resource curse"
- ❌ Benefits concentrated among elites

**Industrialization Drive**:
- ✅ Highest job creation potential
- ✅ Structural transformation toward higher productivity
- ✅ Better jobs (more formal, higher wages)
- ✅ Broad-based development (multiple sectors)
- ❌ Requires highest fiscal investment
- ❌ Longest time to see results
- ❌ Requires complementary policies (infrastructure, skills, governance)

---

## Testing the Scenarios

After restarting the servers:

1. Select **Mozambique** from country selector
2. Click on each scenario preset
3. Click "Apply Scenario"
4. Click "Run Simulation"

**Expected ranking of total jobs created**:
1. 🥇 Industrialization Drive (highest)
2. 🥈 Agricultural Focus (moderate)
3. 🥉 Commodity Extraction (lowest)

If the results show a different ranking, there may be an issue with:
- How subsidies are converted to final demand shocks
- How tariffs affect domestic production
- Time horizon scaling factors
- Sector multiplier calculations
