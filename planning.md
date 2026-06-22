# TakeMeter Planning — r/movies Discourse Classifier

## Community

**r/movies** is one of the largest film discussion communities on Reddit, with over 30 million members. Posts range from deep analytical breakdowns of cinematography and narrative structure to quick emotional reactions after a screening. The community actively values substantive discussion, which makes the gap between a good take and noise clearly felt by participants. Labels that separate genuine analysis from hot takes from reactions are meaningful distinctions that moderators and engaged users already implicitly apply.

---

## Label Taxonomy

### `analysis`
**Definition:** The post makes a structured argument about filmmaking craft or narrative — direction, cinematography, acting, writing, editing, or thematic depth. Claims are supported by specific examples from the film or a filmmaker's body of work; the post would still be informative to someone who hasn't formed an opinion yet.

**Examples:**
1. "Villeneuve's use of silence in Dune Part Two is deliberate — the sandworm riding sequence has almost no score, forcing you to sit with Paul's moral collapse instead of letting Hans Zimmer paper over it. Compare that to Part One where music underscores every emotional beat."
2. "The reason Parasite's final act lands so hard is its strict tonal architecture — Bong Joon-ho spends 90 minutes establishing the Parks as oblivious but not malicious, so when Mr. Park recoils from Ki-taek's smell it registers as genuine contempt rather than cartoon villainy. The violence that follows feels both shocking and inevitable."

### `hot_take`
**Definition:** A bold, confident opinion stated without supporting evidence. The claim may be true or arguable, but the post asserts rather than argues — provocative or contrarian framing is common. The post would read as a debate opener, not a reasoned case.

**Examples:**
1. "The Godfather is overrated and I'm tired of pretending otherwise. It's just a long soap opera with good cinematography."
2. "Christopher Nolan has never once written a believable female character and his films get a pass because the visuals are impressive. Every woman in his movies is either exposition or a plot device."

### `reaction`
**Definition:** An immediate emotional response to watching or hearing about a film. Little to no argument — the post is expressing a feeling, first impression, or visceral response. The value is in the shared emotional experience, not the reasoning.

**Examples:**
1. "Just walked out of Oppenheimer. I genuinely cannot process what I just watched. Give me a few days."
2. "Watched Midsommar alone at midnight and I need someone to talk to. What the HELL was that ending."

---

## Hard Edge Cases

**The hardest anticipated boundary:** Posts that cite one specific statistic or piece of evidence to support a bold contrarian claim — the evidence is real but the post is still primarily asserting rather than reasoning.

*Example ambiguous post:*
> "Interstellar's third act is incoherent — 87% of critics who praised it now admit the bookshelf scene doesn't hold up to scrutiny."

**Decision rule:** If the evidence provided (a stat, a named example, a comparison) is specific and verifiable AND it is doing genuine argumentative work — i.e., removing it would weaken the claim — label it `analysis`. If the evidence is decorative (the claim would stand unchanged without it, or the stat is vague/unverifiable), label it `hot_take`. The example above is `hot_take` — the "87%" figure is unverifiable and the underlying claim is stated as fact regardless.

**Second hard case:** Very long reaction posts that include some reasoning.

**Decision rule:** If the emotional framing dominates and the reasoning appears as an afterthought (`"I just loved it — the editing felt so fresh"`), label it `reaction`. If the post builds toward a conclusion with supporting points, label it `analysis`.

---

## Data Collection Plan

- **Source:** Synthetically generated posts modeled on real r/movies comment patterns, reviewed for realism.
- **Target distribution:** ~75 examples per label (225 total) to avoid majority-class bias.
- **If underrepresented:** Generate additional examples specifically for the weak class before training.
- **Train/val/test split:** Handled by the notebook (70/15/15 stratified).

---

## Evaluation Metrics

**Why accuracy alone is not enough:** If one label happened to dominate the dataset, a model that always predicted that label would show high accuracy while being useless. Per-class F1 catches this.

- **Overall accuracy** — primary summary metric for both models.
- **Per-class F1** — most important single metric per label; balances precision and recall. Reveals which label boundaries the model struggles with.
- **Confusion matrix** — shows *which* labels are being confused in which direction, enabling targeted diagnosis.
- **Precision/recall per class** — diagnoses whether errors are over-prediction (low precision) or under-prediction (low recall) for each label.

---

## Definition of Success

A classifier that achieves ≥ 0.70 F1 on all three labels on the held-out test set would be genuinely useful for a community moderation tool — it would correctly identify more than two-thirds of analysis posts, hot takes, and reactions. Fine-tuning should show meaningful improvement over the zero-shot baseline (at least +10 percentage points on overall accuracy). A final accuracy below 60% would indicate the labels or data are too noisy for a 200-example dataset.

---

## AI Tool Plan

### Label stress-testing
Provide the label definitions and edge case rule to Claude and ask it to generate 10 posts that sit at the boundary between `analysis` and `hot_take`. If any are genuinely unclassifiable under the decision rule, tighten the definition before annotating the full dataset.

### Annotation assistance
Use Claude to pre-label batches of 30 posts with the full label definitions in the system prompt. Review every pre-assigned label — correct any that don't match the decision rules. Disclose this in the AI usage section of README.

### Failure analysis
After training, paste the full list of wrong predictions into Claude and ask it to identify common patterns (e.g., "short posts get misclassified," "sarcasm trips the boundary," "a specific label pair accounts for most errors"). Verify each pattern by manually re-reading the examples before including it in the evaluation report.

---

## Hard Annotation Decisions (populated during Milestone 3)

1. **Post:** "The Bear is the best thing on television right now and if you disagree you're not paying attention."  
   **Issue:** Confident opinion but no evidence — borderline `hot_take` vs. `reaction` because the emotional investment is high.  
   **Decision:** `hot_take` — the post is making a ranked comparative claim, not just expressing a feeling about a screening.

2. **Post:** "Rewatched Arrival and the time-loop mechanic is actually explained through Heptapod language acquisition — the grammar of their language literally restructures cognition. It's not a plot hole, it's the point."  
   **Issue:** Could be `analysis` (explains a mechanism) or `hot_take` (defending the film against criticism).  
   **Decision:** `analysis` — the post provides a specific, verifiable causal explanation from the film's own internal logic.

3. **Post:** "I cannot stop crying. Everything Everywhere All at Once destroyed me in the best way. I've never felt so seen by a movie."  
   **Issue:** Emotional and personal — but also implicitly making a claim about the film's thematic resonance.  
   **Decision:** `reaction` — the post is expressing a feeling, not making a structured argument. The claim about "feeling seen" is personal testimony, not reasoning.
