# Lever: SME / demand stimulus

A broad demand stimulus of g% of GDP is injected into final demand,
spread across sectors by the household consumption vector and scaled by
a **first-round fiscal multiplier** m:

ΔF = m · (g · GDP) · hh_shares

m = 0.5, range [0.1, 1.0], from the bucket approach of Batini, Eyraud,
Forni and Weber (2014), IMF TNM 14/04 (registry). m is the first-round
translation of the fiscal injection into domestic final demand
(import/saving leakages); the input-output multiplier is applied on top
by the engine, so m deliberately does NOT embed second-round effects.

The former kinked diminishing-returns schedule (v0.8.0) had no citation
per kink and was removed; the lever is linear.
