# Job Quality Metrics - Implementation Summary

## Overview

Added comprehensive job quality analysis to the policy simulator to address the critical issue of **job quality** in economic development, particularly relevant for low-income countries like Mozambique where working poverty is extremely high.

## What Was Added

### 1. **Job Quality Metrics Schema** (backend/app/api/schemas.py)

New `JobQualityMetrics` schema tracking:

- **Formalization**: Formal vs informal job counts and formalization rate
- **Working Poverty**: Risk percentage and job counts above/below poverty line
- **Productivity**: Average output per worker (USD/year) and productivity category
- **Sector Composition**: Jobs by agriculture, manufacturing, and services

### 2. **Job Quality Calculation** (backend/app/models/economic_model.py)

New method `_calculate_job_quality_metrics()` that estimates:

#### Working Poverty Risk by Sector
Based on ILO working poverty estimates for developing countries:

| Sector | Poverty Risk |
|--------|-------------|
| Agriculture | 85% |
| Trade (informal retail) | 70% |
| Other Services (informal) | 65% |
| Construction | 55% |
| Transport | 50% |
| Textiles | 45% |
| Food Processing | 40% |
| Manufacturing | 30% |
| Public Services | 25% |
| Chemicals | 25% |
| Automotive | 20% |
| Mining | 15% |
| Utilities | 15% |
| Finance | 10% |

**Rationale**: Working poverty is highly correlated with informality. Agriculture and informal services have 70-90% poverty risk, while formal manufacturing/services have 20-40% risk.

#### Productivity by Sector (USD per worker per year)

| Category | Sectors | Productivity |
|----------|---------|--------------|
| **High** (≥$15K) | Finance, Mining, Utilities, Chemicals, Automotive | $15K-28K |
| **Medium** ($8-15K) | Manufacturing, Public Services, Transport, Food Processing | $8K-12K |
| **Low** (<$8K) | Agriculture, Construction, Textiles, Trade, Other Services | $3.5K-7K |

**Rationale**: Reflects capital intensity and value-added per worker. Agriculture is subsistence-level (~$3,500/worker), while finance and capital-intensive sectors exceed $20K/worker.

### 3. **Job Quality Dashboard** (frontend/src/components/ResultsPanel.jsx)

New **Job Quality Analysis** section displaying:

#### Three Key Metrics Cards:

1. **Formalization Rate**
   - Green (≥60%): Good quality jobs, mostly formal
   - Amber (40-60%): Mixed quality
   - Red (<40%): Poor quality, mostly informal
   - Shows formal vs informal job counts

2. **Working Poverty Risk**
   - Green (≤30%): Low poverty risk
   - Amber (30-60%): Moderate poverty risk
   - Red (>60%): High poverty risk
   - Shows jobs above/below poverty line

3. **Average Productivity**
   - Displays USD per worker per year
   - Color-coded by category (High/Medium/Low)
   - Indicates economic value of jobs created

#### Sector Composition Bar
- Visual breakdown by Agriculture, Manufacturing, Services
- Shows which broad sectors are creating jobs

#### Interpretation Note
Explains what job quality indicators mean for policy outcomes

## Why This Matters

### The Mozambique Case

Mozambique's analysis revealed that **agricultural scenarios create MORE jobs than industrialization**, but:

- Agriculture jobs are **88% informal**
- **85% working poverty risk** in agriculture
- **$3,500/worker productivity** vs $12,000+ in manufacturing

So while agriculture creates 200K+ jobs, they are:
- Low-wage, informal jobs
- High poverty risk
- Low productivity

Manufacturing creates 60K jobs, but they are:
- Higher-wage, more formal
- Lower poverty risk
- 3-4x higher productivity

### Structural Transformation

Job quality metrics help distinguish between:
1. **Quantity** of jobs (agriculture wins)
2. **Quality** of jobs (manufacturing wins)

This addresses your concern: *"Working poverty is extremely high, especially in rural areas"*

## How It Works

For each simulation, the model now:

1. **Calculates formal vs informal jobs** by sector using informal_share multipliers
2. **Estimates working poverty risk** using sector-specific poverty risk rates (correlated with informality)
3. **Computes average productivity** as weighted average of sector GDP per worker
4. **Categorizes by broad sector** (agriculture, manufacturing, services)

All displayed prominently in a new dashboard section that appears immediately after the main employment impact.

## Example Interpretation

### Agricultural Focus Scenario (Mozambique)
- **Total Jobs**: 207,000
- **Formalization Rate**: 15% (RED - poor quality)
- **Working Poverty Risk**: 82% (RED - very high risk)
- **Avg Productivity**: $4,200/worker (LOW category)
- **Sector**: 96% agriculture

**Interpretation**: Creates many jobs quickly but they are informal, low-wage, high poverty risk.

### Industrialization Drive Scenario (Mozambique)
- **Total Jobs**: 61,000
- **Formalization Rate**: 58% (AMBER - mixed quality)
- **Working Poverty Risk**: 35% (AMBER - moderate risk)
- **Avg Productivity**: $9,800/worker (MEDIUM category)
- **Sector**: 8% agriculture, 75% manufacturing, 17% services

**Interpretation**: Creates fewer jobs but they are more formal, higher wages, lower poverty risk, higher productivity - better for long-term development.

## Data Sources

- **Working poverty estimates**: ILO Statistics, World Bank Poverty & Equity Database
- **Productivity estimates**: Based on typical sector GDP per worker in developing economies
- **Informal shares**: From TIVA multipliers (Stats SA Labour Force Survey for ZAF, ILO for others)

## Next Steps

This implementation provides the foundation to:
1. Compare scenarios not just on job QUANTITY but also job QUALITY
2. Highlight trade-offs between rapid job creation (agriculture) vs quality job creation (manufacturing)
3. Support structural transformation analysis showing the path from low-productivity to high-productivity sectors

The model now better captures the reality that **not all jobs are created equal** - a critical insight for development policy.
