# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Two channels, in
order of preference:

1. **GitHub private vulnerability reporting**, from the affected repository's
   Security tab. This attaches the report to the repository, with a draft
   advisory and a CVE request path already in place.
2. **Email [security@simtabi.com](mailto:security@simtabi.com)**, if you would
   rather not use GitHub, or if the repository offers no *Report a
   vulnerability* button.

Include, where possible:

- The affected repository and version.
- A description of the issue and its impact.
- Steps to reproduce, or a proof of concept.

**Acknowledgement within 48 hours.** We will keep you informed as we
investigate, and we will credit you in the fix's release notes unless you
prefer otherwise.

`security@simtabi.com` is the disclosure address and is watched for exactly
this. It is kept separate from community mail so a report is never buried in a
thread about a feature request. Please do not send vulnerabilities to
`opensource@simtabi.com`.

## Which channel a repository actually offers

Private vulnerability reporting is a public-repository feature, and it is off
by default. Every public repository in this organization has it switched on, so
channel 1 is available on all of them.

A **private** repository's Security tab offers no *Report a vulnerability*
button, whatever this policy says, so email is the only channel there.

The repository's own `/security/policy` page settles it: the button is shown
when the channel is open. Do not infer it from anything else.

## Scope

This policy applies to every repository in the
[ichava](https://github.com/ichava) organization that does not carry its own
`SECURITY.md`. A repository's own policy takes precedence where one is present,
and a few carry one because their disclosure surface genuinely differs.

Every package is pre-1.0. Report anything you find regardless; pre-1.0 is not a
reason to stay quiet.
