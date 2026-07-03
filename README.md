# Alas, But One

Finds atomic typo candidates in documentation repositories by surfacing words that appear at most N times across a corpus of `.rst` and `.txt` files. Rare words are scored by likelihood of being a real typo and written to JSONL for review, AI classification, or ML training.

## Installation

```bash
git clone https://github.com/ccho-mongodb/alas-but-one.git
cd alas-but-one
pip3 install -r requirements.txt
```

`anthropic` and `scikit-learn`/`numpy` are optional — only needed for `--ai` and `--train` respectively.

## Setup

Edit `config.json`:

```json
{
  "settings": {
    "repo_base_full_path": "/absolute/path/to/your/docs/",
    "maxOccurrences": 1
  },
  "repositories": {
    "my-repo": {
      "name": "My Docs",
      "relative_path": "my-docs-repo/",
      "source_dir": "source/"
    }
  }
}
```

`repo_base_full_path` + `relative_path` + `source_dir` = the directory the tool walks for `.rst`/`.txt` files.

Add as many repositories as needed. Run all of them at once or target one with `--repo`.

## Usage

```bash
python alas.py                               # run all repos, JSONL output (default)
python alas.py --format csv                  # CSV output instead
python alas.py --repo "My Docs"              # single repo by display name
python alas.py --ai                          # AI review of borderline tokens
python alas.py --parallel                    # process repos concurrently
python alas.py --verbose                     # per-stage token counts
python alas.py --train labels.jsonl          # train ML classifier from labeled output
```

## Output

Each run produces `<repo name>.jsonl` (or `.csv` with `--format csv`), one record per candidate, sorted by `confidence` descending:

```jsonc
{
  "word": "retreive",
  "repo": "My Docs",
  "locations": [{"file": "/path/to/file.rst", "line": 42}],
  "num_occurrences": 1,
  "misspelled": true,
  "confidence": 0.85,       // 0.0–1.0, higher = more likely a real typo
  "suggestion": "retrieve",
  "ignore": false,
  "label": null,            // set manually for ML training
  "ai_reviewed": false,
  "ai_comment": null
}
```

## How Classification Works

Classification happens in up to three layers, each building on the previous:

**1. Heuristic scoring (always runs)**

The spell checker flags unknown words and computes a `confidence` score using edit distance to the nearest known word plus word-feature penalties (short words, digits, ALL CAPS, very long strings score lower). No configuration needed.

**2. AI review (optional, `--ai`)**

Tokens with confidence between 0.3 and 0.7 — the borderline cases where the heuristic is uncertain — are sent to Claude in batches. Claude updates `confidence`, `suggestion`, and `ai_comment` for each. Requires `ANTHROPIC_API_KEY` to be set.

The review thresholds and model are configurable in `config.json`:

```json
"ai": {
  "enabled": false,
  "model": "claude-haiku-4-5-20251001",
  "review_confidence_min": 0.3,
  "review_confidence_max": 0.7,
  "batch_size": 20
}
```

**3. ML classifier (optional, improves over time)**

After reviewing output, set `"label"` on records you want to use as training data:

- `"true_positive"` — real typo
- `"false_positive"` — legitimate term (jargon, acronym, product name, etc.)

Then train:

```bash
python alas.py --train output.jsonl
```

This fits a logistic regression classifier on your labeled examples and saves it to `models/classifier.pkl`. Subsequent runs automatically use it to replace heuristic scores with ML-predicted probabilities. Re-label and re-train as the model improves.

## Ignore List

The ignore list is stored in MongoDB (configured via `ABO_MONGO_URI`) and marks known-good words with `"ignore": true` in output so they can be filtered during review.

To persist ignore list changes from a reviewed file:

```bash
python save_ignore_list.py output.jsonl   # or output.csv
```

Set `"ignore": true` on records to add words, `false` to remove them. Requires `ABO_MONGO_URI` environment variable pointing to your shared MongoDB cluster.

To disable the ignore list, remove `ignore_list_matcher` from the pipeline stages in `alas.py`.

## Extending the Pipeline

The pipeline runs these stages in order:

```
collector → reader → tokenizer → max_occurrence_matcher
         → spell_checker → ignore_list_matcher
         → [ml_predictor] → [ai_reviewer] → formatter
```

To add a new matcher or formatter:

1. Create a file in `matchers/` or `formatters/`, subclass `BaseTask`, implement `run()`
2. Register it in `config.json` under `"modules"`
3. Add it to the pipeline in `alas.py`

To hook into existing stages without modifying them:

```python
from ai.hooks import default_hooks

@default_hooks.post_stage('spell_checker')
def my_hook(stage_name, data):
    # data is Dict[word, Token] after spell check
    return data  # must return data
```

## Known Bugs

This project is no longer under active development. The following issues are documented but will not be fixed here:

1. **Case signal is destroyed before scoring.** The tokenizer lowercases all content (`tokenizer/tokenize_rst.py`), so the ALL-CAPS acronym penalty in `matchers/confidence_scorer.py` and the `is_all_upper` ML feature in `training/features.py` can never fire. Acronyms (HTTP, JSON, SDK) score as full-strength typo candidates.

2. **Line numbers in output are off by one.** The tokenizer stores 0-based line indices, so every `"line"` value in the JSONL/CSV output points one line above the actual occurrence.

3. **Ignore-list reads and writes can target different databases.** The pipeline reads the MongoDB URI from `config.json` (`MONGODB_URI`), while `save_ignore_list.py` reads the `ABO_MONGO_URI` environment variable. If they differ, ignore-list updates silently never take effect on subsequent runs.

4. **The tokenizer is not format-aware.** Despite the name `tokenize_rst.py`, it applies a plain word regex to raw file content. Code blocks, inline literals, RST directives/roles, and URLs are all tokenized as prose — the largest source of false-positive candidates.
