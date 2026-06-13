# What is deliberately NOT in this tool, and why

This simulator models policy as demand and price transformations of a
fixed-coefficient input-output system. Several policies that matter for
employment cannot be expressed that way honestly, so they are left out
rather than faked. This is itself a teaching point: the boundary of a
model is part of understanding it.

## Interest-rate / monetary policy
There is no monetary block, no financial sector behaviour, no
expectations and no inflation dynamics. An interest-rate change works
through investment, the exchange rate, asset prices and credit -
channels this comparative-static, fixed-price model does not contain.
Adding a single "interest-rate multiplier" would be an invented number.

## Active labour market policies (training, public employment services,
job-matching subsidies)
These act on the matching side of the labour market - search frictions,
skills, information - not on final demand. Their effectiveness varies
enormously by design and context, and there is no credible per-country
unit-cost (cost per job) that this tool could apply without inventing
it. The evidence to consult instead: Card, Kluve and Weber (2018),
"What Works? A Meta-Analysis of Recent Active Labor Market Program
Evaluations", Journal of the European Economic Association 16(3),
894-931 - which finds small short-run effects, larger medium-run
effects, and wide variation by programme type.

## Minimum wages
A minimum wage changes the price of labour and the wage distribution;
its employment effect is a contested empirical question that depends on
labour-market structure (monopsony, compliance, spillovers) entirely
outside a demand-driven I-O model. The model has no labour supply curve
and no wage-setting, so it cannot say anything credible here.

## Distribution-targeted transfers (e.g. cash transfers to the poorest)
The general demand-stimulus lever already lets you inject spending
through the household consumption vector. Targeting by household type
(income decile, rural/urban, informal) would need household-survey
microdata and a consumption pattern per group, which the tool does not
carry. Modelling "a transfer to the poorest 20%" would require invented
consumption shares.

## The common thread
Each of these needs a behavioural or distributional mechanism with no
data-derived, per-country parameter available. Under this project's
ground rules (no invented numbers), the honest choice is to exclude
them and say why, not to add a plausible-looking slider.
