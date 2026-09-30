# Contributing

Contributions are welcome on every ichava repository.

## Before you start

- **Open an issue first** for anything larger than a typo fix. It saves you
  building something we were about to change.
- Read the package's `docs/` tree, and [`core`'s](https://github.com/ichava/core/tree/main/docs)
  for the engine, so the change fits the way the ecosystem is put together.

## Pull requests

- One concern per pull request. A branch that fixes a bug and reformats a file is
  two reviews wearing one hat.
- Include a test for anything behavioural.
- Match the surrounding code — its naming, its comment density, its idiom.
- Update the docs in the same pull request. Documentation that lags the code is a
  bug, not a follow-up.

## Icon packs

Vendored SVG assets are refreshed from upstream by
[`maintainer-toolkit`](https://github.com/ichava/maintainer-toolkit), which opens
the pull request. **Do not hand-edit vendored assets** — the next refresh will
overwrite the change. Fix it upstream, or adjust the toolkit.

## Reporting bugs

Open an issue on the repository the bug lives in, with the package version, the
Laravel and PHP versions, and the smallest reproduction you can manage.

Security vulnerabilities are the exception — see [SECURITY.md](SECURITY.md).
