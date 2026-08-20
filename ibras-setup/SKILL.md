---
name: ibras-setup
description: "Pasang dan perbaiki dependensinya: model, browser/CDP, WAHA, SMTP, doctor tiap skill. Use for install, first run, dependency errors, or \"kenapa skill-nya nggak jalan\", checked in dependency order."
license: MIT
metadata:
  version: 1.0.0
  tags: [Setup, Doctor, Preflight, Onboarding, Workshop, WAHA, SMTP, CDP]
---

# Setup

The skills install fine. What fails is everything they depend on, and it fails
**silently** — no error, just worse answers. This skill is the one place that
checks all of it and tells the owner what to run next, in order.

## The failure this exists for

Measured on a clean install, 20 August 2026:

| Missing | What the owner sees |
|---|---|
| `model.default` unset | `404 tool-use` — looks like a broken skill |
| browser/CDP down | agent reports *"halamannya keblokir"* on a page returning HTTP 200 |
| Playwright half-installed | folder exists, `chrome` binary absent, everything looks fine |
| CDP installed but not wired | binary present, nothing listening on 9222, browser still dead |
| no WAHA instance | WhatsApp skill refuses every action, correctly, forever |
| no SMTP config | email skill cannot draft against a real inbox |

None of these raises an error the owner can act on. Three of them make the agent
produce a *confident wrong answer* instead of stopping.

## Run this first, always

```bash
bash scripts/setup.sh            # check only — never changes anything
bash scripts/setup.sh --fix      # do the safe ones, print commands for the rest
```

`--fix` will install a browser and wire it, create config directories, and copy
example configs. It will **not** start Docker containers, touch credentials, or
send anything. Those print a command for the owner to run and read first.

## Order matters, and the script enforces it

1. **Core** — `hermes`, `python3`, PyYAML, and `model.default`. Nothing else is
   worth checking until these pass; a missing model looks like every other bug.
2. **Browser / CDP** — needed by research and by the coach's reachability check.
   Two routes, and the script picks whichever is available:
   - **cloakserve** (Docker) — preferred, because its fingerprint is
     `Asia/Jakarta` + `id-ID`, so SERPs and prices come back Indonesian.
   - **Playwright Chromium** — no Docker needed. Install → run with
     `--remote-debugging-port=9222` → wire. **All three, or the browser is dead.**
3. **Per-skill config** — pillars, voice, WAHA, SMTP. Each is optional; the
   script says which skills each one unlocks so the owner can skip deliberately.
4. **All seven doctors**, aggregated into one table.

## What it will not do

- It will not put an API key, app password, or WAHA key on a command line — those
  are visible in the process list. It prints the form of the command and asks the
  owner to run it, or reads from a prompt with hidden input.
- It will not start a WhatsApp session or send a message.
- It will not "fix" a failing check by disabling it.

## Rules

Read `references/hermes-discipline.md` like every other skill. Two apply hardest here:

- **Rule 1.** If a check fails, say what the check actually returned. Do not
  describe a container, a port, or a page you did not query. *"Docker nggak ada"*
  and *"Docker ada tapi daemon-nya mati"* need different fixes.
- **Rule 2.** Version numbers and ports are figures. Print what you read, not
  what you expect.

Never tell the owner a component is "probably fine". Run the check.

## Reference

`references/prerequisites.md` — what each skill needs, what breaks without it,
and the current upstream facts with their sources and the date they were read.

<!-- HERMES_BUNDLE_MANIFEST_START -->
## Hermes bundle manifest

Hermes Skills Hub installs only support files linked directly from this file.
These links are the complete runtime manifest; load individual files only when needed.

### references

- [references/automation-posture.md](references/automation-posture.md)
- [references/hermes-discipline.md](references/hermes-discipline.md)
- [references/hermes-runtime.md](references/hermes-runtime.md)
- [references/market-adaptation.md](references/market-adaptation.md)
- [references/prerequisites.md](references/prerequisites.md)
- [references/repliz.md](references/repliz.md)
- [references/tools-mapping.md](references/tools-mapping.md)

### scripts

- [scripts/check-citations.py](scripts/check-citations.py)
- [scripts/check-numbers.py](scripts/check-numbers.py)
- [scripts/doctor-common.sh](scripts/doctor-common.sh)
- [scripts/halt.sh](scripts/halt.sh)
- [scripts/hooks/artifact-guard.py](scripts/hooks/artifact-guard.py)
- [scripts/install-guard.sh](scripts/install-guard.sh)
- [scripts/lib/copycheck.py](scripts/lib/copycheck.py)
- [scripts/lib/halt.py](scripts/lib/halt.py)
- [scripts/lib/handoff.py](scripts/lib/handoff.py)
- [scripts/lib/ledger.py](scripts/lib/ledger.py)
- [scripts/lib/profile.py](scripts/lib/profile.py)
- [scripts/lib/replycheck.py](scripts/lib/replycheck.py)
- [scripts/lib/watch.py](scripts/lib/watch.py)
- [scripts/preflight.sh](scripts/preflight.sh)
- [scripts/setup.sh](scripts/setup.sh)
- [scripts/smtp.sh](scripts/smtp.sh)
- [scripts/test-setup.sh](scripts/test-setup.sh)
- [scripts/waha.sh](scripts/waha.sh)

### templates

- [templates/profile.example.yaml](templates/profile.example.yaml)

<!-- HERMES_BUNDLE_MANIFEST_END -->
