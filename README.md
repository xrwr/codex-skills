# codex-skills

Portable Codex skills maintained as a public, MIT-licensed collection.

## Skills

### `building-viewers`

Build or extend read-only browser viewers from the data, artifacts, and application stack that actually exist in a repository. The skill covers catalog/API contracts, URL-restorable selection, desktop and mobile interaction, failure isolation, real-browser verification, and optional deployment selection.

It includes a React + TypeScript + FastAPI starter for repositories without a viewer stack. Existing applications are adapted in place instead of being replaced by the starter. Tailscale is an optional private-sharing route when it is already available and appropriate; it is not a runtime dependency.

## Install

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

Restart Codex after installation. For reproducible machine setup, keep the repository URL and a release tag in dotfiles; keep the skill source and reusable assets here.

## Development

```bash
python -m unittest -v tests/test_skill_package.py
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/building-viewers
```

The test suite renders the starter into a temporary directory and verifies that it refuses to overwrite an existing target.

## License

[MIT](LICENSE)
