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

Run status is reported from evidence that can be traced to the current attempt, not from a queue label or checkpoint alone. The skill separates experiment identity from attempt lineage, so retries retain the experiment ID while old outputs are retired and every new attempt remains auditable.

### `summarizing-experiments`

Compare a repository's recorded experiment hypotheses with artifacts from the current attempt, then organize the evidence into a five-column overview: experiment ID, parent ID, hypothesis, result, and a domain-specific primary metric. Keep supporting details in per-experiment summaries, and never invent a hypothesis after seeing the result.

### `drawing-model-architecture-diagrams`

Create editable SVG diagrams that explain model architectures as semantic data flows rather than exhaustive layer listings. The skill requires input and output tensor shapes, expands only structure that matters to the explanation, uses symbolic dimensions instead of invented values, and verifies the rendered SVG.

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

### `drawing-model-architecture-diagrams`

Ask Codex to install the skill from this repository:

```text
Install the drawing-model-architecture-diagrams skill from xrwr/codex-skills.
```

Or run the bundled installer directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo xrwr/codex-skills \
  --path skills/drawing-model-architecture-diagrams
```

Restart Codex after installation. For reproducible machine setup, keep the repository URL and a release tag in dotfiles; keep the skill source and reusable assets here.

## Development

```bash
uv run python -m unittest -v tests/test_skill_package.py
for skill in building-viewers building-data-science-projects managing-experiments summarizing-experiments drawing-model-architecture-diagrams; do
  uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
    "skills/$skill"
done
```

The package suite validates repository distribution contracts, renders the viewer starter into a temporary directory, and verifies that the starter refuses to overwrite an existing target. The loop also runs the official validator against every skill.

## License

[MIT](LICENSE)
