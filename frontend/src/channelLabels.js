// Central channel-label map (Workstream F.1).
// Single source of human-readable labels for every engine channel key,
// used by the results UI, guided-mode summaries and any export. No raw
// snake_case channel key may reach user-facing output. A backend test
// (data-pipeline/tests/test_channel_labels.py) asserts this map covers
// every channel key the engine can emit and that no label is snake_case.

export const CHANNEL_LABELS = {
  // --- tariff channels ---
  protected_sector_gain: { label: 'Protected-sector gain', hint: 'Import substitution into the tariffed sector' },
  tariff_protected_sector: { label: 'Protected-sector effect', hint: 'Import substitution into the tariffed sector' },
  downstream_cost: { label: 'Downstream input-cost effect', hint: 'Higher input costs reduce downstream output, including exports' },
  tariff_downstream: { label: 'Downstream input-cost effect', hint: 'Higher input costs reduce downstream output' },
  real_income_loss: { label: 'Consumer real-income effect', hint: 'Higher consumer prices reduce household demand across sectors' },
  tariff_consumption: { label: 'Consumer price effect', hint: 'Higher consumer prices reduce household demand' },
  retaliation: { label: 'Retaliation (stylised)', hint: 'Export demand falls in the top export sectors' },
  tariff_revenue: { label: 'Tariff revenue memo item', hint: 'Government revenue from the tariff (memo only, not recycled)' },

  // --- spending and support channels ---
  sector_support: { label: 'Sector support', hint: 'Government spending boosts demand for the supported sector' },
  sme_stimulus: { label: 'Demand stimulus', hint: 'Stimulus spread through the chosen spending basket' },
  public_investment: { label: 'Public investment demand', hint: 'Investment spending allocated across sectors' },
  public_works_direct: { label: 'Direct public works jobs', hint: 'On-site labour of the works programme' },
  public_works_materials: { label: 'Public works materials and supplier demand', hint: 'Non-wage materials and the supplier chain' },
  public_works_wages: { label: 'Public works wage income', hint: 'Induced spending of programme wages' },
  direct_public_employment: { label: 'Direct public employment', hint: 'Public-service posts funded directly' },
  direct_public_employment_operating: { label: 'Public employment operating costs', hint: 'Non-wage operating inputs of public services' },
  production_subsidy: { label: 'Production subsidy effect', hint: 'Lower output prices in the subsidised sector' },
  production_subsidy_real_income: { label: 'Production subsidy: real-income effect', hint: 'Lower prices raise household real income' },
  production_subsidy_downstream: { label: 'Production subsidy: downstream demand', hint: 'Cheaper inputs for downstream users' },
  wage_subsidy: { label: 'Wage subsidy effect', hint: 'Lower labour cost in the subsidised sector' },
  wage_subsidy_real_income: { label: 'Wage subsidy: real-income effect', hint: 'Lower prices raise household real income' },
  wage_subsidy_downstream: { label: 'Wage subsidy: downstream demand', hint: 'Cheaper inputs for downstream users' },
  investment_tax_incentive: { label: 'Additional investment from tax incentive', hint: 'Investment beyond the windfall share' },
  investment_incentive: { label: 'Additional investment from tax incentive', hint: 'Investment beyond the windfall share' },
  investment_windfall: { label: 'Windfall share of tax incentive', hint: 'Investment that would have happened anyway' },

  // --- depreciation channels ---
  depreciation_exports: { label: 'Export competitiveness effect', hint: 'A weaker currency lifts export demand' },
  depreciation_import_cost: { label: 'Import-cost effect', hint: 'A weaker currency raises imported input costs' },
  depreciation_downstream: { label: 'Import input-cost effect', hint: 'Costlier imported inputs reduce downstream output' },
  depreciation_real_income: { label: 'Real-income loss from depreciation', hint: 'Costlier imports reduce household real income' },

  // --- financing ---
  financing_drag: { label: 'Financing offset', hint: 'Household consumption withdrawn to finance the policy' },
  financing_offset: { label: 'Financing offset', hint: 'Household consumption withdrawn to finance the policy' },

  // --- decomposition ---
  direct: { label: 'Direct effect', hint: 'Jobs in the directly affected sector' },
  indirect: { label: 'Supplier-chain effect', hint: 'Jobs along the supplier chain' },
  induced: { label: 'Induced household-consumption effect', hint: 'Jobs created when wages are re-spent (Type II)' },
};

export function channelLabel(key) {
  return (CHANNEL_LABELS[key] && CHANNEL_LABELS[key].label) || key;
}

export function channelHint(key) {
  return (CHANNEL_LABELS[key] && CHANNEL_LABELS[key].hint) || '';
}

export default CHANNEL_LABELS;
