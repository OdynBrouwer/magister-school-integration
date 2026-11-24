# Magister repository instructions

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
- Use the convention `v2.3.2bN` with a matching manifest `2.3.2bN`.
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

## Issue closure

- Close #51 only after rate-limit tests and b4 or later.
- Close #50 only after card-resource startup is lock-safe and tested.
- Close #49 only after height options are built into the bundled card and tested.
