# Ibras Skill Namespace Design

## Decision

Rebrand all seven marketplace skills with an `ibras-` prefix at every identity
boundary: public directory, YAML `name`, marketplace identifier, install command,
cross-skill discovery, and user-facing documentation.

The new canonical names are:

- `ibras-marketing-orchestrator`
- `ibras-brand-strategy-coach`
- `ibras-content-creator`
- `ibras-social-publishing`
- `ibras-waha-marketing`
- `ibras-email-marketing`
- `ibras-cloakserve-research`

Do not publish aliases under the old names. Aliases would preserve the global
name collision this change is intended to remove.

## Compatibility Boundary

Keep existing runtime state and integration names stable. Paths such as
`~/.waha-marketing`, `~/.hermes-email`, business profile storage, environment
variable names, Docker container names, and external API concepts are not skill
identities and must not be renamed. Existing users can therefore install the new
skill names without losing their configured integrations or stored business data.

## Hermes Bundle Layout

Hermes v0.20.2 downloads only support files explicitly referenced by `SKILL.md`
and only from `references/`, `templates/`, `scripts/`, `assets/`, and `examples/`.
Move per-skill `lib/` to `scripts/lib/`, `hooks/` to `scripts/hooks/`, and
`data/` to `assets/data/`. Update commands and script-relative paths accordingly.

Each `SKILL.md` gets a generated `Hermes bundle manifest` containing direct
Markdown links to every shipped support file. This keeps progressive disclosure
while making the remote bundle deterministic and complete. `README.md` remains
repository documentation and is not installed as skill runtime content.

## Alternatives Rejected

1. Prefix only the YAML name: rejected because marketplace slugs and install
   paths would remain ambiguous.
2. Prefix only the repository identifier: rejected because Hermes exposes and
   resolves short skill names globally.
3. Keep the current layout and distribute ZIP files: rejected because it does
   not satisfy marketplace installation.
4. Patch Hermes itself: rejected because existing Hermes installations would
   still receive incomplete bundles.

## Verification

A contract test must fail if a canonical directory/name is missing, an old
marketplace identity remains, a forbidden runtime directory is present, or any
support file is absent from the `SKILL.md` manifest. After local tests, publish
the branch and install all seven canonical identifiers into a blank Incus Hermes
profile. Compare installed file manifests with the public commit, run security
audits and representative doctors/smoke commands, then perform model-awareness
tests once the temporary OpenRouter key is supplied.

