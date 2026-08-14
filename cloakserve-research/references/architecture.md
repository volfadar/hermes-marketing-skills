# Arsitektur — cloakserve-research skill

Bagaimana semua komponen terhubung.

## Diagram alur

```
   ┌──────────────────────────────────────────────────┐
   │  Hermes Agent                                     │
   │  - menjalankan model (mis. deepseek-v4-flash)    │
   │  - browser tool: browser_navigate, browser_console│
   │  - skills/, memory/, cron/                        │
   └────────────────┬─────────────────────────────────┘
                    │ browser.cdp_url = ws://127.0.0.1:9222
                    │ (diset oleh wire-hermes.sh)
                    ▼
   ┌──────────────────────────────────────────────────┐
   │  Docker container "cloakserve"                    │
   │  Image: cloakhq/cloakbrowser:latest               │
   │  ┌────────────────────────────────────────────┐  │
   │  │  cloakserve (CDP multiplexer)              │  │
   │  │  - aiohttp + websockets server             │  │
   │  │  - menjalankan CloakBrowser per-fingerprint│  │
   │  │  - menyajikan /json/version, /json/list    │  │
   │  │  - route WebSocket /devtools/...           │  │
   │  └────────────────┬───────────────────────────┘  │
   │                   │ spawn                         │
   │  ┌────────────────▼───────────────────────────┐  │
   │  │  CloakBrowser (stealth Chromium binary)    │  │
   │  │  - Chromium patched di source C++          │  │
   │  │  - fingerprint: Windows Chrome 146         │  │
   │  │  - timezone: Asia/Jakarta (default)        │  │
   │  │  - locale: id-ID (default)                 │  │
   │  └────────────────┬───────────────────────────┘  │
   └───────────────────┼──────────────────────────────┘
                       │ HTTPS outbound
                       ▼
            ┌──────────────────────┐
   (opsional)│  Tailscale exit node  │   egress dari IP residensial Indonesia
            │  (HP kamu sendiri)    │   (bukan IP datacenter asing)
            └──────────┬───────────┘
                       ▼
              Target: marketplace, blog, halaman publik
```

## Komponen & tanggung jawab

| Komponen | Peran | Diset oleh |
|---|---|---|
| **Hermes Agent** | Orchestrator. Punya `browser` tool yang bicara CDP. | User (`hermes setup`) |
| **Model AI** | "Otak" Hermes. Mis. deepseek-v4-flash (murah). | `model.default` di config |
| **Docker** | Runtime untuk container cloakserve. | User (Docker Desktop) |
| **cloakserve** | CDP multiplexer. Jalankan CloakBrowser, sajikan CDP. | `start.sh` |
| **CloakBrowser** | Stealth Chromium. Kerja nyata: load page, execute JS. | cloakserve (otomatis) |
| **Tailscale** (opsional) | VPN mesh. Route egress lewat HP. | `tailscale-setup.sh` |

## Kenapa arsitektur ini (bukan alternatif lain)

**Kenapa Docker + cloakserve, bukan `pip install cloakbrowser`?**
- cloakserve **tidak distribusi via PyPI** — hanya ada di Docker image resmi.
- Tanpa cloakserve, Hermes tidak bisa connect via `browser.cdp_url` (tidak ada endpoint CDP yang disajikan).
- Docker isolasi: kalau browser crash, tidak ganggu sistem host.

**Kenapa CDP multiplexer (bukan 1 browser langsung)?**
- Bisa banyak fingerprint dari 1 port (`?fingerprint=brand-a`, `?fingerprint=brand-b`).
- Setiap fingerprint = identitas browser berbeda → tidak terkait satu sama lain.
- Idle timeout: browser yang tidak dipakai dimatikan otomatis (hemat RAM).

**Kenapa Tailscale (bukan VPN komersial)?**
- Tailscale = mesh VPN peer-to-peer. Tidak ada server tengah.
- Exit node adalah **HP kamu sendiri** → IP residensial Indonesia asli, bukan proxy belian.
- Gratis untuk personal use, end-to-end encrypted.
- Kamu kontrol kapan exit node aktif (matikan kalau tidak riset).

## Alur data

1. User prompt ke Hermes (mis. via `research.sh` template).
2. Hermes panggil `browser_navigate` tool.
3. Hermes's browser tool connect ke `ws://127.0.0.1:9222?fingerprint=...`.
4. cloakserve route ke CloakBrowser instance yang tepat (spawn baru kalau fingerprint baru).
5. CloakBrowser load page, execute JS, return DOM snapshot.
6. (Opsional) Tailscale exit node → traffic egress dari HP kamu.
7. Hermes proses hasil → format sesuai prompt → return ke user.
8. User **review** hasil sebelum dipakai untuk apapun.

## Isolasi & security

- **Container Docker** mengisolasi cloakserve + CloakBrowser dari host. Kalau compromise, blast radius terbatas.
- **Tidak ada credentials di container.** API key, login session, dll. tetap di host (Hermes). CloakBrowser **tidak punya** akses ke akun kamu.
- **Allowlist Hermes** untuk messaging gateway (Telegram/WA): pakai numeric user IDs.
- **Tailscale** tidak ekspos port internal kamu ke internet. Hanya route outbound lewat exit node.

## Yang TIDAK ada di arsitektur ini

- **Tidak ada auto-posting** ke social media. Hermes cuma riset + draft. Posting = manusia.
- **Tidak ada auto-DM.** Engagement customer = manusia.
- **Tidak ada credential sharing.** CloakBrowser tidak pegang password/token apapun.
- **Tidak ada bypass.** Login, paywall, anti-fraud = di luar scope (dan dilarang `ethics.md`).
