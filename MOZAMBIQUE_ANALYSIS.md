# Why Agriculture Creates More Jobs Than Industrialization

## The Issue

When running simulations for Mozambique, the **Agricultural Focus** scenario creates MORE jobs than the **Industrialization Drive** scenario, which contradicts our expectation.

## Root Cause: Sector Size Dominance

The model applies subsidies as **% of current sector GDP**. Since agriculture is 30% of Mozambique's economy versus 7% for manufacturing, agriculture receives MUCH larger absolute dollar amounts even with lower subsidy rates.

### Mozambique GDP Structure (Total: $22,750M)

| Sector | % of GDP | GDP Value |
|--------|----------|-----------|
| Agriculture | 30% | $6,825M |
| Trade | 20% | $4,550M |
| Public Services | 15% | $3,413M |
| Manufacturing | 7% | $1,592M |
| Mining | 5% | $1,138M |
| Food Processing | 3% | $682M |
| Construction | 3% | $682M |
| Textiles | 1% | $227M |

## Calculation Breakdown

### Agricultural Scenario
| Intervention | Rate | Sector GDP | Absolute $ | Jobs/M | Total Jobs |
|--------------|------|------------|------------|--------|------------|
| Agriculture subsidy | 15% | $6,825M | **$1,024M** | 195 | **199,680** |
| Food processing subsidy | 10% | $682M | $68M | 119 | 8,092 |
| **TOTAL** | | | **$1,092M** | | **~207,772** |

### Industrial Scenario
| Intervention | Rate | Sector GDP | Absolute $ | Jobs/M | Total Jobs |
|--------------|------|------------|------------|--------|------------|
| Manufacturing subsidy | 25% | $1,592M | **$398M** | 82 | 32,636 |
| Textiles subsidy | 20% | $227M | $45M | 154 | 6,930 |
| Food processing subsidy | 15% | $682M | $102M | 119 | 12,138 |
| Construction subsidy | 12% | $682M | $82M | 113 | 9,266 |
| **TOTAL** | | | **$627M** | | **~60,970** |

**Even with HIGHER subsidy rates (25% vs 15%), industrial sectors receive LESS absolute dollars because they're much smaller parts of the economy.**

## Why This Happens

1. **Agriculture dominates** the economy (30% of GDP = $6.8B)
2. **Subsidies scale with sector size**: 15% of $6.8B > 25% of $1.6B
3. **Agriculture is highly labor-intensive**: 168-195 jobs per $1M
4. **Result**: Agriculture subsidy × agriculture employment intensity = massive job numbers

## The Real Development Challenge

This actually reflects **Mozambique's real structural transformation challenge**:

- You can't easily "industrialize" when agriculture is 30% of GDP and manufacturing is only 7%
- Even aggressive industrial policy (25% subsidies!) translates to small absolute amounts
- Agriculture creates lots of jobs, but they're mostly **informal, low-productivity jobs**
- Natural gas (mining) creates almost NO jobs despite huge revenues

## Model Limitations

The model has a **chicken-and-egg problem**:

1. **Current approach**: Subsidies are % of existing sector GDP
   - Can't grow small sectors much because they receive small absolute amounts
   - Perpetuates existing structure

2. **What's missing**: Structural transformation dynamics
   - In reality, industrial policy GROWS sectors over time
   - Tariffs should make domestic production more competitive and EXPAND sector size
   - Productivity investment should fundamentally shift the economy

3. **Static vs Dynamic**: The model is static (one-time shock) not dynamic (sectors grow/shrink)

## How to Make Industrialization Win (Model Adjustments)

To make industrialization create more jobs in the model, we could:

### Option 1: Increase Industrial Subsidies Even More
- Manufacturing: 35% (instead of 25%)
- Textiles: 30% (instead of 20%)
- Construction: 20% (instead of 12%)

### Option 2: Add Tariff Effects
The industrial scenario has high tariffs (20% manufacturing, 18% textiles) but these may not be generating enough demand shock. Check if tariff elasticities are working properly.

### Option 3: Weight SME Stimulus More
Industrial scenario has 2.5% GDP SME vs 1.5% for agriculture. This difference might not be large enough.

### Option 4: Account for Productivity Investment
Industrial scenario has 7% productivity investment vs 2% for agriculture. The long-term multiplier effects aren't capturing this advantage enough.

## Policy Implications for Real Mozambique

This reveals a fundamental truth about low-income, agriculture-dependent economies:

1. **Agriculture focus** creates LOTS of jobs quickly
   - But: informal, low-wage, low-productivity jobs
   - Doesn't change economic structure

2. **Industrial transformation** is HARD
   - Requires MASSIVE investment relative to current sector sizes
   - Takes long time (5-10+ years)
   - Early job impacts may be lower than agriculture spending
   - But: creates formal, higher-wage, higher-productivity jobs

3. **Gas boom creates almost no jobs**
   - Mining only 8 jobs per $1M
   - Capital goes to foreign companies
   - Revenues come later (2030s-2040s)

## Recommendation

The model is actually working CORRECTLY - it's revealing that:

**You can't easily industrialize a 30%-agriculture economy with moderate industrial subsidies. You need either:**
1. **Massive industrial subsidies** (30-40% of sector GDP, not 20-25%)
2. **Long time horizons** (10+ years for sectors to grow and compound)
3. **Complementary policies** not in the model (infrastructure, skills, institutions)

This is why structural transformation is so challenging in practice.

---

**For the model to show industrialization > agriculture, we need to recalibrate the industrial scenario with much higher intervention rates or adjust how demand shocks are calculated.**
