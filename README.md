# TakeMeter — r/movies Discourse Classifier

A fine-tuned text classifier that evaluates discourse quality in r/movies posts and comments, distinguishing **analysis**, **hot takes**, and **reactions**.

---

## Community Choice

**r/movies** (Reddit). The subreddit has over 30 million members and generates highly varied discourse: some posts build detailed arguments about filmmaking craft; others are bold contrarian opinions stated without evidence; still others are raw emotional reactions immediately after a screening. These three modes are recognizable to any regular participant — community members explicitly value substantive analysis and often call out posts that are "just a hot take." That makes the label taxonomy grounded in actual community norms rather than externally imposed categories.

---

## Label Taxonomy

| Label | Definition | Example |
|---|---|---|
| `analysis` | Makes a structured argument about filmmaking craft or narrative — direction, cinematography, acting, writing, editing, or thematic depth. Claims are supported by specific examples from the film or filmmaker's body of work. | "The editing in Mad Max: Fury Road uses centre framing to keep action in the middle third of the screen. In a two-hour chase film it means you never lose spatial orientation. That's genuinely hard to do." |
| `hot_take` | A bold, confident opinion stated without supporting evidence. The claim may be arguable, but the post asserts rather than argues — provocative or contrarian framing is common. | "The Godfather is overrated and I'm tired of pretending otherwise. It's just a long soap opera with good cinematography." |
| `reaction` | An immediate emotional response to watching or hearing about a film. Little to no argument — the post expresses a feeling, first impression, or visceral response. | "Watched Midsommar alone at midnight and I need someone to talk to. What the HELL was that ending." |

---

## Data Collection

**Source:** Synthetically generated posts modeled on real r/movies comment patterns, reviewed for realism. Posts represent the vocabulary, register, and subject matter of actual r/movies discourse (Letterboxd-adjacent film literacy, contemporary releases, canonical reference points).

**Labeling process:** Each example was labeled against the written definitions in planning.md. Borderline cases were resolved using explicit decision rules documented in the planning document.

**Label distribution:**

| Label | Count | % of dataset |
|---|---|---|
| `analysis` | 62 | 31% |
| `hot_take` | 56 | 28% |
| `reaction` | 83 | 41% |
| **Total** | **201** | **100%** |

**Three difficult-to-label examples:**

1. *"The Holdovers is just a comfort film dressed up with good cinematography and prestige pedigree."*
   **Issue:** Expresses a strong opinion but also implicitly makes an aesthetic claim about what "prestige pedigree" conceals.
   **Decision:** `hot_take` — the post asserts rather than argues; there is no supporting evidence or specific craft observation.

2. *"Rewatched Arrival and the time-loop mechanic is actually explained through Heptapod language acquisition — the grammar of their language literally restructures cognition. It's not a plot hole, it's the point."*
   **Issue:** Defending a film against criticism (hot_take framing) but providing a specific, verifiable claim about the film's internal logic (analysis substance).
   **Decision:** `analysis` — the post provides a specific causal explanation that would be persuasive to someone unfamiliar with the criticism. The evidence is doing argumentative work.

3. *"Tár made me deeply uncomfortable and I can't stop thinking about it. Not sure if I liked it or not. Not sure that's the point."*
   **Issue:** Could be `reaction` (expressing discomfort) or `analysis` (the final clause gestures at interpretation).
   **Decision:** `reaction` — the post is expressing a state, not building an argument. The interpretive gesture is not developed.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace). Selected for compatibility with the free Colab T4 GPU tier and fast convergence on small datasets.

**Training setup:**
- Framework: HuggingFace `transformers` + `Trainer` API
- Train/val/test split: 70% / 15% / 15% (stratified, `random_state=42`)
- Training examples: 140 | Validation: 30 | Test: 31
- Tokenization: `max_length=256`, `truncation=True`

**Hyperparameter decisions:**
- `num_train_epochs=3` — standard for small BERT fine-tuning. Increasing risked overfitting on 140 training examples.
- `learning_rate=2e-5` — the standard starting point for BERT-family fine-tuning. Reduces destabilization of pretrained weights.
- `per_device_train_batch_size=16` — fits T4 GPU memory comfortably.
- `warmup_steps=50` — smooths early training instability on a small dataset.

---

## Baseline

**Model:** Groq `llama-3.3-70b-versatile` (zero-shot, `temperature=0`)

**Prompt used:**

```
You are classifying posts from r/movies, the film discussion subreddit on Reddit.
Assign each post to exactly one of the following categories.

analysis: The post makes a structured argument about filmmaking craft or narrative — direction,
cinematography, acting, writing, editing, or thematic depth. Claims are supported by specific
examples from the film or a filmmaker's body of work.
Example: "The editing in Mad Max: Fury Road uses centre framing to keep action in the middle
third of the screen — you never lose spatial orientation across a two-hour chase film."

hot_take: A bold, confident opinion stated without supporting evidence. Provocative or contrarian
framing is common. The post asserts rather than argues.
Example: "The Godfather is overrated. It's just a long soap opera with good cinematography."

reaction: An immediate emotional response to watching or hearing about a film. Little to no
argument — the post expresses a feeling, first impression, or visceral response.
Example: "Watched Midsommar alone at midnight. What the HELL was that ending."

Respond with ONLY the label name. Do not explain your reasoning. Do not add punctuation.

Valid labels:
analysis
hot_take
reaction
```

**Collection method:** Each of the 31 test examples was submitted to the Groq API (`max_tokens=20`). All 31 responses parsed successfully (0 unparseable).

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy | Test examples |
|---|---|---|
| Zero-shot baseline (Groq llama-3.3-70b-versatile) | **0.968** | 31 |
| Fine-tuned DistilBERT | **0.871** | 31 |

Fine-tuning regression: **−0.097** (the baseline outperformed the fine-tuned model by ~10 percentage points)

### Per-Class Metrics — Fine-Tuned Model

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 0.77 | 1.00 | 0.87 | 10 |
| `hot_take` | 1.00 | 0.50 | 0.67 | 8 |
| `reaction` | 0.93 | 1.00 | 0.96 | 13 |
| **macro avg** | **0.90** | **0.83** | **0.83** | 31 |
| **weighted avg** | **0.90** | **0.87** | **0.86** | 31 |

### Per-Class Metrics — Baseline (Groq)

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 0.91 | 1.00 | 0.95 | 10 |
| `hot_take` | 1.00 | 0.88 | 0.93 | 8 |
| `reaction` | 1.00 | 1.00 | 1.00 | 13 |
| **macro avg** | **0.97** | **0.96** | **0.96** | 31 |
| **weighted avg** | **0.97** | **0.97** | **0.97** | 31 |

### Confusion Matrix — Fine-Tuned Model

| | Predicted: analysis | Predicted: hot_take | Predicted: reaction |
|---|---|---|---|
| **True: analysis** | 10 | 0 | 0 |
| **True: hot_take** | 3 | 4 | 1 |
| **True: reaction** | 0 | 0 | 13 |

See [confusion_matrix.png](confusion_matrix.png) for the visual version.

**Reading the matrix:** `analysis` and `reaction` are classified perfectly (100% recall). All 4 errors are `hot_take` misclassifications — 3 predicted as `analysis` and 1 predicted as `reaction`. The fine-tuned model has learned `analysis` and `reaction` well but cannot reliably identify `hot_take`.

### Wrong Prediction Analysis

**Example 1**
- **Text:** *"The MCU's core problem is that every film is required to service the franchise rather than itself. Any character moment that could produce genuine change — loss, failure, growth — is undone in the next installment because the IP needs to remain stable. It's not about bad directors; it's a structural constraint."*
- **True label:** `hot_take`
- **Predicted:** `analysis` (confidence: 0.34)
- **Analysis:** This is the most instructive error. The post makes a structured argument with an explicit causal claim ("it's a structural constraint") and industry reasoning — it reads syntactically like analysis. But it provides no evidence: no specific films, no examples of a character moment being undone, no citation of a constraint mechanism. The model appears to have learned that posts with abstract structural reasoning signal `analysis`, missing the annotation rule that evidence must be specific and verifiable. The low confidence (0.34) suggests the model was genuinely uncertain — this is a real borderline case and the same post was considered ambiguous during annotation.

**Example 2**
- **Text:** *"Citizen Kane is a film school exercise, not a masterpiece. Every choice in it is about demonstrating technique, not about the story."*
- **True label:** `hot_take`
- **Predicted:** `analysis` (confidence: 0.34)
- **Analysis:** The post makes a categorical claim about Welles's intentions ("every choice is about demonstrating technique") that superficially resembles analytical observation. The phrase "film school exercise" is critical vocabulary that signals discourse awareness. The model appears to associate filmmaking terminology with the `analysis` label — the word "technique" is a strong surface signal for analysis in the training data. The error reveals a vocabulary shortcut: the model learned that technical film language → `analysis`, without learning that `hot_take` posts frequently use that same vocabulary to sound credible.

**Example 3**
- **Text:** *"The greatest cinematographer working today is Hoyte van Hoytema and the Oppenheimer discussion mostly missed what he was doing with IMAX texture to physicalize memory and imagination."*
- **True label:** `hot_take`
- **Predicted:** `analysis` (confidence: 0.35)
- **Analysis:** This post names a specific cinematographer, a specific film, and a specific technical concept (IMAX texture / physicalization of memory) — three markers the model has learned to associate with `analysis`. The error is legitimate: this is a genuinely hard case. Under the annotation rules, it's `hot_take` because the claim ("the discussion mostly missed what he was doing") is asserted without demonstrating what van Hoytema actually did. But the vocabulary is indistinguishable from analysis-level discourse. This suggests the decision boundary between sophisticated `hot_take` and `analysis` is too subtle for 140 training examples to capture.

### Sample Classifications

| Post (excerpt) | True label | Predicted | Confidence |
|---|---|---|---|
| "Villeneuve's use of silence in Dune Part Two is deliberate — the sandworm riding sequence has almost no score, forcing you to sit with Paul's moral collapse..." | `analysis` | `analysis` | ~0.92 |
| "Just walked out of Oppenheimer. I genuinely cannot process what I just watched. Give me a few days." | `reaction` | `reaction` | ~0.97 |
| "The Godfather is overrated and I'm tired of pretending otherwise. It's just a long soap opera with good cinematography." | `hot_take` | `hot_take` | ~0.88 |
| "Parasite just wrecked me. The last twenty minutes — I couldn't breathe. Incredible." | `reaction` | `reaction` | ~0.96 |
| "The color work in Moonlight is doing real narrative labor... the palette charts his psychic state, not just his environment." | `analysis` | `analysis` | ~0.90 |

**One correct prediction explained:** The Dune Part Two post is correctly classified as `analysis` because it names a specific formal decision (absence of score in the sandworm sequence), attributes intent to the director, and makes a comparative claim (contrasting Part Two with Part One). The model has learned that posts containing director names, technical craft terms, and explicit comparisons signal `analysis` — and in this case that signal is correct.

---

## Reflection: What the Model Learned vs. What I Intended

**What I intended the model to learn:** The distinction between `analysis` and `hot_take` is argumentative structure — does the post provide evidence that would persuade someone unfamiliar with the claim? A post about cinematography with specific examples is `analysis`; a post about cinematography with a confident assertion is `hot_take`.

**What the model actually learned:** The model learned surface vocabulary signals. Posts with technical film terminology (cinematographer, IMAX, structural constraint, technique) were associated with `analysis` regardless of whether evidence was doing argumentative work. Posts with first-person emotional registers and present tense were correctly associated with `reaction`. The `hot_take` label was systematically underlearned because sophisticated hot takes borrow the vocabulary of analysis — the model needed to learn a structural distinction that isn't visible at the word level.

**The core gap:** With only 140 training examples, DistilBERT could not learn the argumentative structure distinction — it learned the vocabulary distribution instead. The confusion matrix confirms this: `analysis` and `reaction` have clean surface signals (technical film vocabulary vs. emotional first-person register). `hot_take` does not have a clean surface signal, because good hot takes are written to sound like analysis.

**Why the baseline outperformed fine-tuning:** Llama 3.3 70B already has a rich semantic model of discourse types built from pretraining. With 31 test examples and very clean archetypal posts, it can apply the label definitions almost perfectly from the prompt alone. DistilBERT is 40x smaller and learned from only 140 examples — it picked up vocabulary shortcuts that worked on easy cases but failed on sophisticated hot takes. On a messier, larger, real-world dataset, fine-tuning would likely surpass the zero-shot baseline because the task complexity would exceed what can be conveyed in a prompt.

---

## Spec Reflection

**One way the spec helped:** The explicit warning about label distribution — "if any label accounts for more than 70% of your dataset, you have an imbalance problem" — prompted a deliberate distribution check before training. The `reaction` label was naturally easier to generate examples for; without that check it could have dominated the dataset and produced a majority-class classifier.

**One way implementation diverged:** The spec assumes data is collected manually from a real community. Using synthetic data produced cleaner, more archetypal examples than real r/movies posts — which contributed to the baseline performing surprisingly well (synthetic posts closely match the idealized examples in the classification prompt). Real posts blend registers, use sarcasm, reference in-jokes, and trail off mid-thought in ways the synthetic data doesn't capture. The model was trained on easier examples than it would encounter in production.

---

## AI Usage

1. **Dataset generation:** Claude (claude-sonnet-4-6) generated all 201 labeled examples. The prompt provided the full label taxonomy and decision rules from planning.md and instructed the model to produce realistic r/movies-style posts for each label. All generated examples were reviewed for plausibility and labeling correctness. Approximately 15 generated examples were revised or discarded because they straddled two labels without a defensible decision.

2. **Label stress-testing:** Before finalizing the taxonomy, Claude was prompted to generate 10 posts at the `analysis` / `hot_take` boundary. This revealed that posts citing a single statistic were genuinely ambiguous under the original definition — which prompted the decision rule that evidence must be "doing argumentative work." The taxonomy was tightened before any annotation began.

3. **Failure analysis:** After training, the 4 wrong predictions were reviewed and a pattern was identified: all misclassifications involved `hot_take` posts that used technical film vocabulary. This pattern was verified manually by re-reading each example. The reflection section above is based on that analysis.

---
