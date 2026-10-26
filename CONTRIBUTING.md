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
[`icon-sets-sync`](https://github.com/ichava/icon-sets-sync), which opens
the pull request. **Do not hand-edit vendored assets** — the next refresh will
overwrite the change. Fix it upstream, or adjust the toolkit.

The icon artwork itself is not ours. It belongs to its upstream authors and
keeps their licence and attribution, recorded in each pack's `ATTRIBUTION.md`.
Never remove or reword an upstream credit.

## Licensing your contribution

Simtabi LLC is the licensor of every ichava repository. Everyone who works on
them, maintainers included, is a contributor and not a licensor.

- In an **MIT** repository, you agree that your contribution is licensed under
  that repository's MIT licence, with Simtabi LLC as the copyright holder named
  in `LICENSE`.
- In a **proprietary** repository (`icon-browser`, `react-icon-browser`,
  `react-landingpage`, `ichava.com`, `icon-sets-bundled`,
  `icon-sets-metronic`), you contribute under your agreement with Simtabi LLC,
  and the result is Simtabi LLC's.

Licensing questions go to imani@simtabi.com.

Do not commit lock files (`composer.lock`, `package-lock.json` and the like) in
any ichava repository. They are gitignored, and CI resolves dependencies fresh.

## Reporting bugs

Open an issue on the repository the bug lives in, with the package version, the
Laravel and PHP versions, and the smallest reproduction you can manage.

Security vulnerabilities are the exception — see [SECURITY.md](SECURITY.md).
