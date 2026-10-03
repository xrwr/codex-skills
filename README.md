# codex-skills

Portable Codex skills maintained as a public, MIT-licensed collection.

## Skills

### `building-viewers`

Build or extend read-only browser viewers from the data, artifacts, and application stack that actually exist in a repository. The skill covers catalog/API contracts, URL-restorable selection, desktop and mobile interaction, failure isolation, real-browser verification, and optional deployment selection.

It includes a React + TypeScript + FastAPI starter for repositories without a viewer stack. Existing applications are adapted in place instead of being replaced by the starter. Tailscale is an optional private-sharing route when it is already available and appropriate; it is not a runtime dependency.

### `building-data-science-projects`

Create or restructure Python data-science and machine-learning projects with a focused stack. The skill preserves an existing repository's package manager, frameworks, and directory contracts; for greenfield projects, it selects only the libraries and directories that have a current owner.

Recommendations are conditional rather than a bulk-install bundle. Exact versions remain in each project's `pyproject.toml` and lockfile, while experiment lifecycle details and viewer implementation stay delegated to the corresponding skills.

### `managing-experiments`

Plan, configure, retry, and assess repository experiments with self-contained experiment configs. Each config declares its component selections directly instead of inheriting from another experiment; shared settings stay with the concrete component, task, or artifact contract that owns them.

An experiment combines a hypothesis with a bounded validation plan; trials are conditions within that plan, named `001a`, `001b`, and so on when adopting a new convention. Search earlier experiments before assigning a new ID. Corrections and retries preserve the experiment, trial, and fold; planned comparison changes add trials, and independent validation plans may need a new experiment. Use the skill's decision table autonomously within an approved plan or automatic experiment scope and budget; ask when the classification is unclear or the work exceeds that scope. Track executions through job IDs, run IDs, and logs without requiring manual attempt numbers or directories. Preserve existing attempt contracts and previous results used for comparisons. No theme hierarchy is required. Run status comes from artifacts attributable to the target execution.

Before registering or starting a new experiment, present its candidate number, experiment-level hypothesis, evidence, and comparison plan for confirmation. Trials state their IDs, changed conditions, baselines, and roles in testing that hypothesis; they do not require separate hypotheses or hypothesis approvals. Preserve existing approval for concrete plans. Choosing new experiment numbers and hypotheses autonomously requires explicit authorization covering those choices; an automatic-loop round limit alone does not grant it.

W&B groups collect CV folds for the same trial; other trials are compared separately, and retry history is excluded from CV aggregation through explicit selection of execution results. A single verification or bounded search batch schedules a follow-up Codex summary after its required evaluations, with fixed trial, job or run ID, and artifact references. The summary follows `summarizing-experiments` when available, records important comparison conclusions, and does not launch further experiments.

### `summarizing-experiments`

Summarize verified conditions, metrics, observations, and unknowns from experiment artifacts. Keep experiment documents factual; discuss interpretation and next actions in chat. Automatically record important, evidence-backed comparison conclusions in `docs/knowledge/` as short `HIT` / `MISS` / `OPEN` entries with experiment Markdown links and compact before/after scores when useful. Group entries by pipeline category, report what was saved for later human review, avoid duplicates, and preserve human corrections. Unverified ideas stay in a single section at the top of each category file; AI additions to that section still require approval. Non-interactive summaries follow the same rules. Preserve the five-column overview and never invent a launch-time hypothesis after seeing the result.

Keep the human-facing summary short: purpose, comparison, main results, and evaluation limits. Route AI verification and reproduction to canonical configs, artifacts, and a separate record when needed; keep operational histories out of the summary and read them only for the relevant investigation. Default reproduction and audit records to `docs/evidence/<task>/<id>.md`, outside human report directories and the viewer's ordinary list and search, while keeping them accessible by links.

By default, update each experiment in `docs/experiments/<task>/<id>.md` and maintain the Mermaid lineage and overview table in `docs/experiments/<task>/README.md`. Keep one overview row per experiment, compare trials inside its summary, and link selected results to the exact trial, execution records, and artifacts. Preserve established report locations. Reuse Hydra configuration snapshots where available; commit IDs are optional, and code provenance remains separate from configuration.

### `checking-training-pipelines`

Check leakage, real-data forward/backward, fixed-batch overfitting, and a short training/validation run with time and step limits. Monitor training speed and GPU state lightly. Keep auxiliary records minimal and outside the experiment output tree.

Use this skill for training correctness; use `managing-experiments` for experiment configuration, execution history, and resource scheduling.

### `automating-experiments`

Explicitly start a bounded experiment loop. A dedicated Pueue control job opens a fresh Codex session, lets the existing experiment skills select and run one verification, waits for its completion summary, then opens the next session. The default limit is three rounds; failures and stop requests end continuation. This skill has automatic invocation disabled.

In the target repository, ask:

```text
$automating-experiments で、現在のサマリーから検出器の改善を自動実験して。
GPU 0を使って最大3回。データ分割は固定し、結果を見て次の検証を選んで。
```

The skill records the authorized scope, round limit, Pueue job IDs, and session IDs outside experiment outputs. Its `status` and `stop` commands are documented in [the skill](skills/automating-experiments/SKILL.md). Stopping ends future sessions; already-started work continues. The round limit bounds sessions, not new experiment IDs, elapsed time, or GPU hours. An authorized search batch needs its own enforced trial/time limits. The helper requires Python 3.12+, Pueue, an authenticated Codex CLI with `--approve-for-me`, and the installed management and summary skills.

## Install

### `building-viewers`

Ask Codex to install the skill from this repository:

```text
Install the building-viewers skill from xrwr/codex-skills.
```

Or run the bundled installer directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/building-viewers
```

### `building-data-science-projects`

Ask Codex to install the skill from this repository:

```text
Install the building-data-science-projects skill from xrwr/codex-skills.
```

Or run the bundled installer directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/building-data-science-projects
```

### `managing-experiments`

Ask Codex to install the skill from this repository:

```text
Install the managing-experiments skill from xrwr/codex-skills.
```

Or run the bundled installer directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/managing-experiments
```

### `summarizing-experiments`

Ask Codex to install the skill from this repository:

```text
Install the summarizing-experiments skill from xrwr/codex-skills.
```

Or run the bundled installer directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/summarizing-experiments
```

### `checking-training-pipelines`

Ask Codex to install the skill from this repository:

```text
Install the checking-training-pipelines skill from xrwr/codex-skills.
```

Or run the bundled installer directly after the skill is published:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/checking-training-pipelines
```

### `automating-experiments`

Install `managing-experiments` and `summarizing-experiments` above, then install this skill after publication:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/automating-experiments
```

Restart Codex after installation. For reproducible machine setup, keep the repository URL and a release tag in dotfiles; keep the skill source and reusable assets here.

## Development

```bash
uv run python -m unittest -v tests/test_skill_package.py tests/test_experiment_loop.py
for skill in building-viewers building-data-science-projects managing-experiments summarizing-experiments checking-training-pipelines automating-experiments; do
  uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
    "skills/$skill"
done
```

The package suite checks the skill files, metadata, documented contracts, and viewer scaffolding when this collection is edited. Run it locally before publishing changes; GitHub Actions also runs it on pushes and pull requests. It does not invoke a coding agent or automatically run when a skill is used, and it does not evaluate the quality of agent-generated reports or applications. The loop also runs the official validator against every skill.

The loop tests exercise round limits, failed summaries, stale dependencies, stop requests, and duplicate execution without starting training. They do not measure hypothesis quality.

A separate starter CI job generates the bundled viewer template into a temporary directory and runs its backend/frontend tests, lint, and build. Tests for a viewer adapted to a real project belong to that project.

## License

[MIT](LICENSE)
