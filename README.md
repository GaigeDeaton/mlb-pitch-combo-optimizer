# MLB Pitch Combo Optimizer

A data science pipeline that identifies each MLB pitcher's optimal 3-pitch
arsenal, personalized to 6 statistically-derived batter archetypes and
handedness, using 2026 season Statcast data.

**Live Dashboard:** https://mlb-pitch-combo-optimizer.streamlit.app/

## What this answers

For a given pitcher, given their real pitch arsenal, which 3 pitch types
should they lean on most against a specific kind of hitter -- and how does
that change based on batter handedness and hitting style?

Success is measured by run value (Statcast's delta_run_exp) -- not
strikeouts specifically, since any outcome that limits scoring (a
strikeout, a routine groundout, a walk avoided) counts as a good result
for the pitcher.

## Methodology

1. Batter archetypes -- 6 hitter profiles built via Gaussian Mixture
   Model clustering (not hard k-means) across 20 plate discipline, power,
   and batted-ball features. GMM was chosen deliberately over k-means: an
   early silhouette-score comparison showed batters don't sort into
   cleanly separated groups, so a soft/probabilistic clustering approach
   (where a batter can be, say, 60% one archetype and 40% another) was a
   more honest fit than forcing hard labels.
2. Pitcher arsenal scoring -- every possible 3-pitch combination from a
   pitcher's real, qualifying arsenal (100+ pitches thrown this season)
   is scored by average run value, weighted by each pitch's actual usage
   rate rather than a simple average.
3. Small-sample correction -- empirical Bayes shrinkage is applied at
   multiple levels (batter-by-pitch-category, pitcher-by-handedness,
   pitcher-by-archetype) so thin samples get pulled toward a more
   reliable baseline instead of producing misleadingly extreme scores.
4. League-wide aggregation -- comparing the top 10% of pitcher/
   handedness matchups against the full population showed fastballs are
   notably under-represented in elite combos relative to their overall
   usage, while changeups, sinkers, cutters, and curveballs are
   over-represented.
5. Tunneling (tested, inconclusive) -- a physics-based measure of how
   similar a pitcher's pitches look at the batter's swing-decision point
   was built and tested against run value. It showed no meaningful
   correlation in this data (r ~= -0.03 to -0.07), most likely because a
   season-averaged, arsenal-level proxy doesn't capture pitch-sequence-
   level deception the way real tunneling operates. Documented as a
   tested negative finding, not hidden.

## Key validated findings

- Usage-weighting (vs. simple averaging) changes the optimal combo for
  ~22-24% of pitchers.
- Layering in batter archetype (on top of handedness alone) changes the
  optimal combo for 35-47% of pitchers, depending on archetype.
- Elite-tier pitcher/handedness matchups under-use the fastball and
  over-use secondary pitches relative to the league-wide baseline.

## Repo structure

- dashboard_app.py -- Streamlit dashboard (live app entry point)
- dashboard_combo_data.csv -- Final dashboard-ready dataset
- requirements.txt -- Python dependencies
- notebooks/ -- Full analysis pipeline, in order
  - batter_archetypes.ipynb -- Phase 2: batter feature engineering + GMM clustering
  - pitcher_arsenal.ipynb -- Phase 3: pitcher arsenal + combo scoring
  - combo_by_archetype.ipynb -- Phase 4: archetype-weighted combo scoring
  - leaguewide_aggregation.ipynb -- Phase 5: league-wide pitch-type findings
  - tunneling.ipynb -- Phase 7: trajectory/tunneling analysis
  - dashboard_export.ipynb -- Final export step for the dashboard
- data/ -- Intermediate + final result files

## Tech stack

Python (pandas, scikit-learn, numpy), Streamlit, pybaseball (Statcast
data access via Baseball Savant).

## Data pipeline

Raw Statcast data is pulled daily via an automated pybaseball script.
Notebooks are rerun manually to refresh archetypes and combo scores, then
re-exported to dashboard_combo_data.csv for the live dashboard.

## Limitations

- Only covers pitchers with 3+ qualifying pitch types (100+ thrown this
  season) -- true 2-pitch specialists are excluded by design.
- This is a descriptive/retrospective analysis of what happened this
  season, not a predictive model -- it does not forecast future
  performance.
- Archetype composition can shift meaningfully when the clustering model
  is rerun on updated data, so day-to-day comparisons of a pitcher's
  score against a named archetype should be treated as approximate.
