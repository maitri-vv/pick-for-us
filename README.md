# Pick For Us

A trained movie recommender built for low-effort evenings. Get a pick immediately, optionally add up to five favorites, or combine two people's taste with a transparent compromise score. No uploads, streaming-account connections, or API keys.

## Timing and challenge status

Started on October 26, 2026 before the Week 3 cutoff (12:29 PM IST). **Not submitted before the deadline.** Work resumed after the cutoff. This is a completed theme-inspired research demo, not a claim of an eligible on-time entry.

Post-deadline work: two-person and mobile QA, title/type fixes verification, five-like serving-model evaluation, backend regression checks, packaging, documentation, and deployment. Do not backdate commits or represent this release as finished before the cutoff.

## Run the downloadable project

Install Node.js 22.13+ and run from the extracted `pick-for-us` folder:

```sh
npm install
npm run dev
```

Open http://localhost:3000. The trained weights are included, so Python is not needed to run the application. Production: `npm run build` then `npm start`.

The downloaded version is a standard Next.js app. The hosted source uses Vinext with the Sites deployment adapter; the frontend, recommendation routes, catalog and learned model are the same. Deploy the downloadable version to Vercel with the Next.js framework preset, no environment variables required. It needs a server runtime; GitHub Pages alone cannot run its API routes.

## Architecture

- React frontend: instant community pick, optional favorite search, one/two-person mode, genre selection, explainable result, seen/next, and decision confirmation.
- `GET /api/catalog?q=`: server-side movie search and genres.
- `POST /api/recommend`: validates IDs, scores learned weights, applies filters and excludes selected/seen movies.
- `GET /api/model`: evaluation metadata and provenance.
- Python / NumPy / SciPy: EASE model fit and reproducible evaluations.
- The backend bundles trained weights. It does not call an external LLM or require a GPU.

Preferences are sent to this app's server for scoring and are not intentionally persisted in a database or user account. The hosting provider may retain normal request metadata. Page fonts load from Google Fonts. External IMDb links open only when selected. Poster-like covers are original typographic graphics, not official movie artwork. No streaming availability, runtimes, plots, or age classifications are invented.

## Training

Dataset: GroupLens MovieLens latest-small, September 2018 snapshot, 100,836 ratings, 610 anonymous users, 9,742 source movies. The original download was unavailable in this environment; source files came from the `smanihwr/ml-latest-small` mirror. SHA-256 hashes are recorded in `lib/metrics.json`. Retain `DATA_LICENSE.txt`.

Download and extract the dataset from https://grouplens.org/datasets/movielens/latest/ into a folder containing ratings.csv, movies.csv and links.csv. Then:

```sh
python training/download_data.py --destination data/ml-latest-small
# If GroupLens is unavailable, add --mirror to use the documented mirror.
python -m pip install -r training/requirements.txt
python training/train.py --data /path/to/ml-latest-small
python training/evaluate_onboarding.py /path/to/ml-latest-small
```

The first script regenerates weights and the full-profile metrics. The second adds the five-like serving-model metrics expected by the UI. Run both before building.

Training: per-user chronological 80/20 split, with movie ID as timestamp tie-break. Only movies with at least 10 training ratings are retained (1,859). Ratings >=4 create binary likes. Fit the EASE ridge solution with lambda=80, zero the diagonal, keep each item's largest 80 positive outgoing weights, and round to six decimals. Neither hyperparameter was selected by searching the held-out test outcomes.

This is an adapted sparse positive EASE model, not the unchanged dense EASE paper model. It learns item-to-item coefficients from actual rating interactions. It is not an LLM fine-tune and does not use handcrafted genre matching as its personalization engine.

## Evaluation results

| Experiment | Eligible users | Trained model Recall@10 | Baseline Recall@10 |
|---|---:|---:|---:|
| Full historical positive profile | 573 | 11.030% | 6.097% (training popularity) |
| Five most recent training likes, production scoring | 563 | 9.822% | 4.845% (community quality) |

Full-profile NDCG@10: 0.12488 model vs 0.08299 popularity. All eligible unseen movies are candidates, not sampled negatives. All previously rated training movies are excluded. Relevant test items have ratings >=4. Recall@10 is the share of held-out liked items recovered in the top ten; it is **not 98% accuracy** or a probability someone will enjoy a movie.

Limits: per-user chronology is not one global time cutoff, so other users' later interactions can influence a target user's test period. The five-like simulation still knows which other movies to exclude; a true first-time visitor does not provide that history. We did not measure real-user satisfaction, reduced scrolling time, or two-person fairness. The snapshot is for development, not a standardized research leaderboard.

## Shared scoring

Normalize each person's item-affinity vector by its maximum. With favorites for both people, combine 0.65 × weaker affinity + 0.35 × mean affinity, then add a small community-quality component. With one person's favorites, use single-person scoring. With no favorites, use a Bayesian-smoothed community rating. Scores explain learned associations, not causation or guaranteed taste.

## Checks

`npm test` runs 12 checks against the real API handler and model weights: no-input recommendations, personalization, exclusion of seeds and seen movies, genre filtering, shared-score symmetry, hidden partner isolation in solo mode, and malformed input rejection.

Live browser checks cover zero-input loading, both-person selections, recommendation explanations, final selection, and a 390px mobile layout. The production build and TypeScript checks pass. See `VERIFICATION.md` for final details.

## Licensing and attribution

Application code: MIT (LICENSE). MovieLens data and derived model/catalog artifacts: GroupLens research-use conditions in DATA_LICENSE.txt; **not cleared for commercial or revenue-bearing use**. GroupLens/University of Minnesota do not endorse this project. Do not remove the data terms when redistributing the learned artifacts.

Cite: F. Maxwell Harper and Joseph A. Konstan (2015), The MovieLens Datasets: History and Context. ACM TiiS 5(4). https://doi.org/10.1145/2827872

Model method: Harald Steck (2019), Embarrassingly Shallow Autoencoders for Sparse Data. https://arxiv.org/abs/1905.03375

Libraries: NumPy, SciPy, React, Next.js/Vinext and their contributors. Typography: DM Sans and Manrope via Google Fonts. Implementation and evaluation were assisted by ChatGPT/Codex.
