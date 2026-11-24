# Magister repository instructions

## Repository scope

- This repository **is** the published HACS integration; changes here go straight to users.
- Only `custom_components/magister_school/` is shipped by HACS. `tools/`, tests, `blueprints/`, `card/` and release paperwork are repository-only.
- `tools/` holds developer tooling. Never import it from the integration and never move it into `custom_components/`.
- The local Home Assistant test installation and the Lovelace card live in separate folders/repositories outside this one. Never edit, copy or sync those from here.

## Home Assistant

- For primary Home Assistant checks, use `ha-primary-core` first.
- If core tools are unavailable, use `ha-primary-http` next.
- Do not use secondary Home Assistant MCP servers unless the primary routes are explicitly unavailable or the task concerns the secondary system.
- Check active Repairs and integration entities before changing code.

## GitHub

- Use GitHub CLI (`gh`) for repository, issue, pull-request, tag and release operations.
- The GitHub account is `OdynBrouwer`.
- Use `main` as the normal target branch.
- **Every change is published as a beta first.** Always bump to the next `vX.Y.ZbN` and create a prerelease.
- Never publish a stable release unless the user explicitly asks for "volledige versie" / "stable".
- Use the convention `vX.Y.ZbN` with a matching manifest `X.Y.ZbN`.
- Create prereleases with `gh release create <tag> --prerelease --target main`.
- When the user asks to remove older betas, delete the release **and** its tag: `gh release delete <tag> --yes --cleanup-tag`.

## Card releases

- Edit `card/src/magister-school-card.js`, never only the bundled file.
- Build from `card/` with `npm run build`.
- Verify that `custom_components/magister_school/www/magister-school-card.js` contains the source changes.
- Update and migrate the Lovelace resource URL when the manifest/card version changes.
- Test both card-height source configuration and resource URL cache-busting.

## Validation

- Run `pytest -q test_issue_fixes.py test_timeout_recovery.py`.
- Run card build with `Push-Location card; npm run build; Pop-Location`.
- Run JSON validation and `git diff --check`.
- Do not commit or push until the requested beta/release work is confirmed.

## API monitoring

- Magister has no public changelog. New fields: `--dump-raw` plus `python tools/magister_api_diff.py baseline.json current.json`.
- New features/rubrieken and login changes: `python tools/magister_bundle_diff.py --schoolserver <school>.magister.net` (public bundles, no account needed).
- Tests: `test_api_diff.py` and `test_bundle_diff.py`.

## Issue closure

- Close an issue only after the fixing code is built, tested and published as a beta.
