# Verification — October 26, 2026

Story: a visitor chooses zero, one, or two sets of favorites; a POST to the recommendation backend scores trained MovieLens weights; the UI renders a real catalog movie and its learned associations.

- Training: completed on the recorded dataset snapshot; the included weights are actual trained coefficients.
- Held-out evaluation: full-profile and five-like serving-scoring evaluations completed; see lib/metrics.json for exact metrics and protocol limits.
- API/model checks: 12 checks passed against the actual route handler and learned weights.
- TypeScript: noEmit check passed.
- Browser: zero-input community pick rendered; Toy Story for person one plus The Matrix for person two produced a shared recommendation with separate learned-link explanations; confirming the film changed the heading to “Decision made. Snacks next.”
- Responsive: inspected the 390px embedded viewport; mobile controls checked separately.
- No claims of measured real-world time savings, group satisfaction or ranking superiority beyond the recorded offline experiments.

The initial backend HTTP probe from the shell could not reach the managed browser preview origin. Handler-level tests and the browser's actual requests verified the API/model boundary instead. Final production checks are recorded after deployment.
