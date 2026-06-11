# Lever: government sector support

Replaces the former "subsidy" lever (v0.11.0).

Support of rate r to sector s is a final-demand injection
ΔF_s = r·x_s (the slider percentage is read against the sector's
baseline gross output, so support scales with sector size).

## Financing drag (toggle, default ON)
Tax-financed support: the same total amount is subtracted from
household consumption, spread by the household consumption vector.
With the toggle on, learners see the **net** effect (demand shifted,
not created); with it off, the **gross** effect of the injection alone.
The fiscal cost equals the spending itself.

No behavioural parameters: both sides of the lever are pure
final-demand accounting through the Leontief system.
