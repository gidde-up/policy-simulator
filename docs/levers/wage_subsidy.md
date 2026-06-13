# Lever: wage subsidy

A subsidy at rate w on sector j's labour costs lowers its unit cost in
proportion to the sector's labour share: a DomesticCostShock
dc[j] = -w x labour_share_j, where labour_share_j = compensation /
output (data-derived from the country JSON). Thereafter identical
machinery to the production subsidy (downstream and real-income gains
through the price model). Fiscal cost = w x wage bill of j (smaller than
a production subsidy's w x output, so a smaller financing drag).

**Deliberately excluded** (cited, not modelled): the wage subsidy here
acts only through the price/demand channel. It does NOT model the
hiring response to a lower effective wage beyond that demand effect,
nor displacement of non-subsidised workers, nor deadweight (subsidising
hires that would have happened anyway). The empirical literature finds
these effects large and context-dependent; capturing them would require
a labour-demand model this tool does not have. Read the result as the
demand-side effect of the cost reduction, not the full employment
effect of a wage-subsidy programme.
