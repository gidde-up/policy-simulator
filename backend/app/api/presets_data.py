"""Curated didactic scenarios (presets) -- plain data, no framework
imports, so the data-pipeline test suite can load this module by file
path and verify every scenario against the engine.

Each preset:
  params       lever settings sent to /api/simulate (percent units)
  walkthrough  ordered narration steps shown in Guided mode; every
               sign/structure claim is enforced by tests/test_presets.py
               via `expected`
  expected     net_sign: positive | negative | near_zero (near_zero =
               |net| < 0.1% of baseline employment)

The recurring data-derived lesson for support levers: a tax-financed
injection is net employment-positive only if the supported sector
creates more jobs per dollar (Type I) than the household consumption
basket the financing drag falls on.
"""

PRESETS = [
    # ----------------------------------------------------- South Africa
    {
        "id": "zaf_manufacturing_protection",
        "country_code": "ZAF",
        "name": "Manufacturing Protection",
        "description": "Tariffs on manufacturing, automotive and "
                       "textiles: protection's gains against its costs",
        "params": {
            "tariff_changes": {"manufacturing": 15, "automotive": 20,
                               "textiles": 10},
        },
        "walkthrough": [
            {"title": "The promise",
             "text": "Tariffs raise import prices, so part of the demand "
                     "previously met by imports shifts to domestic "
                     "producers: the protected sectors gain jobs (green "
                     "channel bar)."},
            {"title": "The hidden bill",
             "text": "Domestic industries also BUY the protected goods "
                     "as inputs. Their costs rise and demand for their "
                     "output (including exports) falls; consumer prices "
                     "rise and households cut spending everywhere (red "
                     "channel bars)."},
            {"title": "The net result",
             "text": "The losses outweigh the protected-sector gains: "
                     "the net effect is negative, and small next to the "
                     "gross reallocation (about 47,000 jobs gained where "
                     "protection lands, 59,000 lost elsewhere). Toggle "
                     "retaliation to add export exposure."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": True,
                     "gains_positive": True},
    },
    {
        "id": "zaf_construction_push",
        "country_code": "ZAF",
        "name": "Construction & Trade Support",
        "description": "Tax-financed support to labour-intensive "
                       "sectors: gross gains vs financing drag",
        "params": {
            "sector_support": {"construction": 8, "trade": 5},
        },
        "walkthrough": [
            {"title": "The injection",
             "text": "Government spending boosts demand for construction "
                     "and trade, both more labour-intensive than the "
                     "average of what South African households buy."},
            {"title": "Who pays",
             "text": "The financing drag (tax-financed, toggle on by "
                     "default) takes the same amount out of household "
                     "consumption."},
            {"title": "The lesson",
             "text": "The net effect stays clearly positive BECAUSE the "
                     "supported sectors employ more people per dollar "
                     "than the household basket the taxes come out of. "
                     "Switch the drag off to see the gross effect alone."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "zaf_demand_stimulus",
        "country_code": "ZAF",
        "name": "Broad Demand Stimulus",
        "description": "A 2%-of-GDP demand stimulus spread through "
                       "household consumption",
        "params": {"sme_stimulus": 2},
        "walkthrough": [
            {"title": "The injection",
             "text": "The stimulus reaches sectors in proportion to "
                     "household spending patterns, scaled by a cited "
                     "first-round fiscal multiplier (0.5, range 0.1-1.0) "
                     "before supply-chain effects."},
            {"title": "Read the range",
             "text": "The result is shown as a range over the cited "
                     "multiplier values: the honest statement is an "
                     "order of magnitude, not a point."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    # ---------------------------------------------------------- Tunisia
    {
        "id": "tun_textile_focus",
        "country_code": "TUN",
        "name": "Textiles: Tariff vs Support",
        "description": "The same sector, protected and supported - and "
                       "the two instruments nearly cancel",
        "params": {
            "tariff_changes": {"textiles": 10},
            "sector_support": {"textiles": 8},
        },
        "walkthrough": [
            {"title": "Two instruments, one sector",
             "text": "The tariff works through import substitution; the "
                     "support is a direct demand injection. The channel "
                     "bars separate them."},
            {"title": "Nearly zero net",
             "text": "The gains and the bills (downstream costs, "
                     "real-income loss, financing drag) almost exactly "
                     "cancel: about 21,000 jobs gained and 21,000 lost. "
                     "When the net is this small, the honest reading is "
                     "'approximately zero, with large reallocation' - "
                     "not the sign of the residual."},
        ],
        "expected": {"net_sign": "near_zero", "has_tariff_channels": True},
    },
    {
        "id": "tun_agro_processing",
        "country_code": "TUN",
        "name": "Agro-processing Support",
        "description": "Support to food processing and agriculture",
        "params": {
            "sector_support": {"food_processing": 10, "agriculture": 5},
        },
        "walkthrough": [
            {"title": "Linkages at work",
             "text": "Food processing has the strongest supply-chain "
                     "linkages in this economy (output multiplier 1.76); "
                     "supporting it pulls agriculture along."},
            {"title": "Net of financing",
             "text": "Even after the financing drag the effect stays "
                     "positive: the supported chain employs more people "
                     "per dollar than average household consumption."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "tun_demand_stimulus",
        "country_code": "TUN",
        "name": "Broad Demand Stimulus",
        "description": "A 2%-of-GDP demand stimulus",
        "params": {"sme_stimulus": 2},
        "walkthrough": [
            {"title": "Small open economy",
             "text": "Part of any demand stimulus leaks into imports; "
                     "Tunisia's import shares are roughly double South "
                     "Africa's, so its multipliers are lower. Compare "
                     "the same preset across countries."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    # --------------------------------------------------------- Viet Nam
    {
        "id": "vnm_manufacturing_support",
        "country_code": "VNM",
        "name": "Manufacturing Support - a Cautionary Tale",
        "description": "Tax-financed support to the flagship sector "
                       "comes out strongly net-NEGATIVE",
        "params": {"sector_support": {"manufacturing": 5}},
        "walkthrough": [
            {"title": "The surprise",
             "text": "Supporting Viet Nam's flagship sector DESTROYS "
                     "net employment. Manufacturing creates about 31 "
                     "jobs per million dollars of demand (supply chain "
                     "included) - but the household consumption basket "
                     "the financing drag falls on creates about 113, "
                     "because Vietnamese households spend heavily on "
                     "labour-intensive food and services."},
            {"title": "See it yourself",
             "text": "Toggle the financing drag OFF: the gross effect "
                     "of the same injection is strongly positive. The "
                     "lever's sign is decided by WHO PAYS, not by the "
                     "injection."},
            {"title": "Read it as accounting, not a forecast",
             "text": "This is a comparative-static input-output result "
                     "at fixed prices and technology - the direction and "
                     "rough magnitude of a reallocation, not a prediction "
                     "of Viet Nam's employment."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False},
    },
    {
        "id": "vnm_agriculture_support",
        "country_code": "VNM",
        "name": "Agriculture Support",
        "description": "Support to the most labour-intensive sector",
        "params": {"sector_support": {"agriculture": 5}},
        "walkthrough": [
            {"title": "The mirror image",
             "text": "Agriculture creates about 210 jobs per million "
                     "dollars of demand - nearly double the household "
                     "basket. The same tax-financed mechanism that made "
                     "manufacturing support net-negative makes "
                     "agriculture support strongly net-positive."},
            {"title": "The general rule",
             "text": "A tax-financed sector support creates net jobs "
                     "only if the supported sector employs more people "
                     "per dollar than the consumption it crowds out."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "vnm_tariff_experiment",
        "country_code": "VNM",
        "name": "Tariff Experiment",
        "description": "A 10% manufacturing tariff in an "
                       "import-dependent economy",
        "params": {"tariff_changes": {"manufacturing": 10}},
        "walkthrough": [
            {"title": "Import-dependent production",
             "text": "Viet Nam's industries run on imported inputs. A "
                     "manufacturing tariff feeds straight into "
                     "production costs across the economy: the "
                     "downstream channel dwarfs the protected-sector "
                     "gain."},
            {"title": "The net result",
             "text": "Strongly negative - the largest relative loss of "
                     "the five countries for this experiment."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": True,
                     "gains_positive": True},
    },
    # --------------------------------------------------------- Thailand
    {
        "id": "tha_automotive",
        "country_code": "THA",
        "name": "Automotive Focus - the Flagship Paradox",
        "description": "Tariff plus support for the automotive flagship "
                       "comes out net-NEGATIVE",
        "params": {
            "tariff_changes": {"automotive": 10},
            "sector_support": {"automotive": 8},
        },
        "walkthrough": [
            {"title": "A capital-intensive flagship",
             "text": "Thailand's automotive sector creates about 24 "
                     "jobs per million dollars of demand - a third of "
                     "the household basket's 73. Both instruments aim "
                     "demand at a sector that employs few people per "
                     "dollar."},
            {"title": "Who pays",
             "text": "The tariff's downstream and real-income costs and "
                     "the support's financing drag all fall on more "
                     "labour-intensive activity. Net effect: negative, "
                     "despite real gains inside the automotive supply "
                     "chain."},
            {"title": "Read it as accounting, not a forecast",
             "text": "Comparative-static input-output result at fixed "
                     "prices and technology - the direction and rough "
                     "magnitude of a reallocation, not a prediction of "
                     "Thailand's employment."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": True},
    },
    {
        "id": "tha_construction",
        "country_code": "THA",
        "name": "Construction Support",
        "description": "Support just above the basket's labour "
                       "intensity: modestly positive",
        "params": {"sector_support": {"construction": 8}},
        "walkthrough": [
            {"title": "Close call",
             "text": "Construction creates about 80 jobs per million "
                     "dollars - just above the household basket's 73. "
                     "The tax-financed net effect is positive but "
                     "modest: the margin between supported sector and "
                     "basket is the whole story."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "tha_food_processing",
        "country_code": "THA",
        "name": "Food Processing Support",
        "description": "Support to food processing and agriculture",
        "params": {
            "sector_support": {"food_processing": 10, "agriculture": 4},
        },
        "walkthrough": [
            {"title": "Agro-chain",
             "text": "Food processing (94 jobs per million dollars) "
                     "pulls agriculture (217) along its supply chain - "
                     "watch the agriculture row in the sector chart "
                     "even though most support goes to processing."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    # ----------------------------------------------------------- Senegal
    {
        "id": "sen_agriculture",
        "country_code": "SEN",
        "name": "Agriculture & Agro-processing",
        "description": "Support to agriculture and food processing",
        "params": {
            "sector_support": {"agriculture": 10, "food_processing": 6},
        },
        "walkthrough": [
            {"title": "Labour-intensive base",
             "text": "Senegal's agriculture employs far more people per "
                     "dollar of output than any other sector here; the "
                     "direct bar dominates the decomposition."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "sen_construction",
        "country_code": "SEN",
        "name": "Construction & Infrastructure",
        "description": "Support to construction plus a small stimulus",
        "params": {"sector_support": {"construction": 10},
                   "sme_stimulus": 1},
        "walkthrough": [
            {"title": "Two instruments",
             "text": "Targeted support and a broad stimulus appear as "
                     "separate channels; construction has the highest "
                     "output multiplier in this economy (1.72)."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "sen_tariff_experiment",
        "country_code": "SEN",
        "name": "Tariff Experiment",
        "description": "A 10% manufacturing tariff where domestic "
                       "substitutes are thin",
        "params": {"tariff_changes": {"manufacturing": 10}},
        "walkthrough": [
            {"title": "Thin substitution",
             "text": "With little domestic manufacturing capacity, a "
                     "tariff mostly raises prices instead of shifting "
                     "demand to local producers (Senegal's import-demand "
                     "elasticity sits at the bottom of the cited range - "
                     "see the assumptions panel)."},
            {"title": "The net result",
             "text": "Marginally negative, with the parameter range "
                     "straddling zero: gains and losses nearly cancel. "
                     "The robust message is the reallocation, not the "
                     "small net number."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": True,
                     "gains_positive": True},
    },

    # ===== extension levers (Session F/H); group order in the UI puts
    # industrial/sectoral and public-employment scenarios first =====
    {
        "id": "zaf_public_works",
        "country_code": "ZAF",
        "name": "Public Works (Labour-Based)",
        "description": "An employment-intensive public works programme, "
                       "1% of GDP",
        "params": {"public_works": {"budget_pct_gdp": 1.0,
                                    "method": "labour_based"}},
        "walkthrough": [
            {"title": "Maximising labour content",
             "text": "Labour-based methods spend a much larger share of "
                     "the budget on wages than equipment-based ones "
                     "(ILO EIIP: 20-50% vs the construction sector's own "
                     "~16%). The wage component creates direct job-years; "
                     "the materials component flows through the "
                     "construction supply chain."},
            {"title": "Job-years, not permanent posts",
             "text": "Results are job-years: one person employed for one "
                     "year. Even net of the tax-financing drag, the "
                     "labour intensity makes this strongly job-positive. "
                     "Real programmes such as South Africa's EPWP use "
                     "this approach (referenced as context; the tool does "
                     "not model the EPWP's specific design)."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False,
                     "has_job_years": True},
    },
    {
        "id": "tha_direct_public_employment",
        "country_code": "THA",
        "name": "Direct Public Hiring",
        "description": "Government hiring in public services, 1% of GDP",
        "params": {"direct_public_employment": {"budget_pct_gdp": 1.0}},
        "walkthrough": [
            {"title": "Wages plus operating costs",
             "text": "The budget splits, data-derived, into a wage "
                     "component (direct job-years at public-services pay) "
                     "and a non-wage operating component flowing through "
                     "the public-services input chain."},
            {"title": "Net of financing",
             "text": "With the tax-financing drag on, the net effect is "
                     "close to zero here: public services are only "
                     "moderately labour-intensive relative to the "
                     "household basket the tax falls on. Toggle the drag "
                     "off to see the gross programme effect."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False,
                     "has_job_years": True},
    },
    {
        "id": "sen_production_subsidy_agri",
        "country_code": "SEN",
        "name": "Production Subsidy: Agriculture",
        "description": "A 8% production subsidy to agriculture",
        "params": {"production_subsidy": {"agriculture": 8}},
        "walkthrough": [
            {"title": "Subsidising a jobs-rich sector",
             "text": "A production subsidy lowers the sector's price, "
                     "raising demand for it and lifting household real "
                     "income. Agriculture is the most labour-intensive "
                     "sector in Senegal."},
            {"title": "Net positive",
             "text": "Because agriculture creates far more jobs per "
                     "dollar than the household basket the tax falls on, "
                     "the subsidy is net job-positive even with the "
                     "financing drag - the mirror image of subsidising a "
                     "capital-intensive sector."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "tha_production_subsidy_auto",
        "country_code": "THA",
        "name": "Production vs Wage Subsidy: Automotive",
        "description": "A 10% production subsidy to automotive - compare "
                       "with the wage-subsidy variant",
        "params": {"production_subsidy": {"automotive": 10}},
        "walkthrough": [
            {"title": "Subsidising a capital-intensive sector",
             "text": "Automotive creates few jobs per dollar. A "
                     "production subsidy on its full output is expensive, "
                     "so the tax-financing drag on the labour-intensive "
                     "household basket dominates: net negative."},
            {"title": "Compare the wage subsidy",
             "text": "Switch to a wage subsidy at the same rate: it costs "
                     "only the labour share of output, a far smaller "
                     "fiscal footprint and a much smaller net loss. Same "
                     "sector, very different bill."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False},
    },
    {
        "id": "tha_wage_subsidy_auto",
        "country_code": "THA",
        "name": "Wage Subsidy: Automotive",
        "description": "A 10% wage subsidy to automotive labour costs",
        "params": {"wage_subsidy": {"automotive": 10}},
        "walkthrough": [
            {"title": "Cheaper than a production subsidy",
             "text": "A wage subsidy covers only the labour share of "
                     "cost, so the fiscal cost and its financing drag are "
                     "much smaller than a production subsidy's. The net "
                     "loss is correspondingly smaller."},
            {"title": "What this leaves out",
             "text": "This models only the demand-side effect of the "
                     "lower cost. Hiring responses beyond that, "
                     "displacement and deadweight are deliberately not "
                     "modelled (see the assumptions panel)."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False},
    },
    {
        "id": "vnm_investment_incentive",
        "country_code": "VNM",
        "name": "Investment Tax Incentive",
        "description": "A tax incentive costing 1% of GDP at 30% intensity",
        "params": {"investment_tax_incentive":
                   {"fiscal_cost_pct_gdp": 1.0, "intensity": 30}},
        "walkthrough": [
            {"title": "The windfall",
             "text": "Investor surveys find most incentivised investment "
                     "would have happened anyway. At the registered 75% "
                     "redundancy, three-quarters of the spend is windfall "
                     "- only the remaining quarter creates new demand."},
            {"title": "Net negative",
             "text": "The full revenue forgone carries the financing "
                     "drag, while only the small additional investment "
                     "adds jobs: the net effect is negative. The "
                     "windfall is shown explicitly - it is the point."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False,
                     "has_windfall": True},
    },
    {
        "id": "vnm_public_investment",
        "country_code": "VNM",
        "name": "Public Investment (Broad)",
        "description": "Public investment of 1.5% of GDP by GFCF "
                       "composition",
        "params": {"public_investment": {"amount_pct_gdp": 1.5}},
        "walkthrough": [
            {"title": "Investment vs the basket that funds it",
             "text": "Investment demand follows the capital-goods (GFCF) "
                     "mix, which is less labour-intensive than Viet Nam's "
                     "household consumption basket. Tax-financed, the "
                     "drag on that jobs-rich basket outweighs the "
                     "investment's job content."},
            {"title": "Gross vs net",
             "text": "Toggle the financing drag off to see the gross "
                     "effect; the net result is the honest one for a "
                     "tax-financed programme."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False},
    },
    {
        "id": "zaf_stimulus_government",
        "country_code": "ZAF",
        "name": "Stimulus Composition: Government",
        "description": "A 2%-of-GDP stimulus via government consumption "
                       "- compare with the household-transfer default",
        "params": {"sme_stimulus": 2, "stimulus_target": "government"},
        "walkthrough": [
            {"title": "Composition matters",
             "text": "Routed through government consumption, the stimulus "
                     "enters demand at full value (its only leakage is "
                     "the imported content of what government buys)."},
            {"title": "Compare the transfer",
             "text": "The household-transfer default is scaled by a "
                     "first-round fiscal multiplier below 1 (transfers "
                     "are partly saved or spent on imports), so it "
                     "creates fewer jobs for the same budget. How you "
                     "spend matters as much as how much."},
        ],
        "expected": {"net_sign": "positive", "has_tariff_channels": False},
    },
    {
        "id": "tun_depreciation",
        "country_code": "TUN",
        "name": "Exchange-Rate Depreciation (Stylised)",
        "description": "A 10% depreciation: export gains vs import-cost "
                       "and real-income losses",
        "params": {"depreciation": 10},
        "walkthrough": [
            {"title": "Two sides",
             "text": "A depreciation makes exports cheaper abroad "
                     "(export volumes expand) but raises the domestic "
                     "price of all imports, lifting input costs and "
                     "cutting household real income."},
            {"title": "Import-dependent: net negative here",
             "text": "Tunisia's high imported-input dependence means the "
                     "cost and real-income losses outweigh the export "
                     "gain. The sign is not forced - the country's "
                     "structure decides it. Stylised: a pure relative-"
                     "price shock, no monetary or inflation dynamics."},
        ],
        "expected": {"net_sign": "negative", "has_tariff_channels": False},
    },
]
