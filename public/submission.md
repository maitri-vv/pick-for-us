---
title: "Pick For Us: I trained a small movie model to end the endless ‘you pick’ loop"
published: false
tags: ai, opensource, machinelearning, webdev
---

**Timing note:** This project was inspired by Hacktoberfest Week 3's “Slow and Steady” theme and started before its deadline. It was completed after the deadline and was not submitted on time. This post is a project showcase, not a claim of an eligible challenge entry.

A movie night has a surprisingly tedious opening scene.

“Something good?”

“Sure. You pick.”

Forty thumbnails later, nobody has picked anything.

I built **Pick For Us** around a small promise: reduce the work of choosing. It opens with an actual recommendation, asks for no uploads or account connections, and lets you add a few favorite films only if you want a more personal pick.

## What I built

There are two modes: **Just me** and **Both of us**. In the second, each person can tap up to five favorites. The app looks for a recommendation supported by both sets of taste signals and explains the connections separately.

It presents one main pick, a small set of alternatives, and a “That's the one” button that lets you stop choosing. Genre filtering and “Seen it / next” are there when needed. There is no endless feed.

The default works with no input. It uses community ratings with a support adjustment, so a film with a handful of glowing reviews does not automatically outrank a well-supported favorite.

## Demo and code

- [Try Pick For Us](https://pick-for-us.maitrivaghasiya-iimu.chatgpt.site)
- [Download the complete project, trained model and training scripts](https://pick-for-us.maitrivaghasiya-iimu.chatgpt.site/pick-for-us-source.zip)
- [Inspect the evaluation report](https://pick-for-us.maitrivaghasiya-iimu.chatgpt.site/api/model)

For a quick walkthrough: open the app, choose “Both of us,” add one or two favorites for each person, and find a shared pick. Check the separate explanations, then choose the film or ask for another.

## A real dataset and a model trained from scratch

I used the **MovieLens latest-small September 2018 snapshot**, containing 100,836 ratings from 610 users across 9,742 source movies. After a training-only minimum-support filter, the application catalog contains 1,859 films.

The model is based on **EASE**, a linear collaborative-filtering method. It learns how likes for one film help predict likes for others. NumPy fits its regularized closed-form solution; it is not an LLM prompt pretending to be a recommender.

The training pipeline:

1. Sort each user's ratings by time and hold out their latest 20%.
2. Build a binary interaction matrix from training ratings of four stars or higher.
3. Fit EASE with regularization of 80 and a zero diagonal.
4. Retain the largest 80 positive outgoing weights per movie and export them.
5. Evaluate that exported sparse model, rather than a larger model that the app never serves.

The sparse positive truncation is my deployment adaptation of EASE. I did not tune its settings through a search over test-set results.

## What the tests actually showed

| Experiment | Users | Model Recall@10 | Baseline Recall@10 |
|---|---:|---:|---:|
| Complete historical positive profile | 573 | 11.030% | 6.097%, training popularity |
| Five recent training likes, production scoring | 563 | 9.822% | 4.845%, community quality |

Recall@10 measures how much of a user's held-out liked set appears in the top ten. It is not a probability of enjoyment, and I am not calling it “98% accuracy.”

The second experiment is closer to the interface: it uses only five likes and the same single-person scoring formula served by the backend. However, the evaluator still excludes all previously rated training films, which a genuinely new visitor has not supplied. Real onboarding performance still needs a user study.

There are other limits. The split is chronological per user, not one global date cutoff. The catalog is historical and leans toward English-language films. These are development-snapshot experiments, not a claim of state-of-the-art research results.

## How the two-person decision works

Each person gets an affinity score derived from learned weights. After normalization, the shared score combines 65% of the weaker affinity with 35% of the pair's average, plus a small community-quality component.

That means a very strong signal for one person cannot completely erase a weak signal for the other. It is a transparent product rule—not a learned or user-validated guarantee of fairness. The interface shows each person's relative affinity and the selected favorites contributing positive learned weights.

## Frontend and backend

React handles the responsive interface. The backend exposes catalog search, recommendation scoring, and evaluation metadata. The hosted app uses Vinext on a server runtime; the downloadable package is a standard Next.js project with the same frontend, handlers, and learned model.

The trained weights ship with the backend. There are no model-service keys, streaming-account integrations, user uploads, or GPU requirements. User-selected IDs are sent to this server for scoring; the app does not intentionally persist a personal profile.

Twelve checks exercise the actual recommendation handler and model, including invalid input, seen-film exclusion, genre filtering, and two-person symmetry. Browser checks verify the complete selection-to-result flow and the mobile layout. ChatGPT/Codex assisted the implementation and testing.

## Why open innovation matters here

A small, inspectable model is enough for this job. I can show how the coefficients were learned, rerun training, compare against baselines, and explain the serving formula without outsourcing the decision to a proprietary chat API.

The distinction between open application code and data permissions matters: my application code is MIT-licensed, while the MovieLens-derived artifacts retain GroupLens's research-use terms. This is a non-commercial research demo; a commercial product would need suitable permission or a different dataset.

The app does not know current streaming availability, age suitability, or recent releases. Its poster-like cards are original typographic graphics, not official film artwork. It links to IMDb so visitors can inspect details before deciding.

I haven't measured minutes saved. The product's “Slow and Steady” contribution is the workflow: arrive with nothing, optionally offer a few tastes, get one grounded suggestion, and give yourself permission to stop scrolling.

## Credits

- F. Maxwell Harper and Joseph A. Konstan, [The MovieLens Datasets: History and Context](https://doi.org/10.1145/2827872), 2015. [Dataset and terms](https://grouplens.org/datasets/movielens/). No endorsement by GroupLens or the University of Minnesota is implied.
- Harald Steck, [Embarrassingly Shallow Autoencoders for Sparse Data](https://arxiv.org/abs/1905.03375), 2019.
- NumPy, SciPy, React, Next.js, Vinext, and their contributors.
- DM Sans and Manrope through Google Fonts.

The original dataset download was unavailable during the build, so training files were obtained from the `smanihwr/ml-latest-small` mirror. File hashes and the original data terms are included for provenance.
