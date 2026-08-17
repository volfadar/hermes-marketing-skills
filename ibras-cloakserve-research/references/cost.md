# Biaya — ibras-cloakserve-research skill

Breakdown realistis untuk pemakaian rutin + harian.

## Komponen & biaya

| Komponen | Biaya | Catatan |
|---|---|---|
| **CloakBrowser** (free binary) | **$0** | Free tier cukup untuk riset harian. Pro ($20/bln) = fingerprint lebih bervariasi, untuk volume tinggi. |
| **Docker** | **$0** | Gratis untuk personal use. |
| **Tailscale** (personal) | **$0** | Gratis sampai 100 device. |
| **Hermes Agent** | **$0** | Open source (MIT). |
| **OpenRouter API (model)** | bervariasi | Lihat tabel di bawah. |
| **Server/VPS** (opsional) | $5-10/bln | Hanya kalau mau 24/7. Bisa pakai laptop sendiri gratis. |

## Model AI — pilihan & biaya

| Model | Biaya per 1M token | Kecepatan | Kecerdasan | Rekomendasi |
|---|---|---|---|---|
| **deepseek/deepseek-v4-flash-0731** | ~$0.30 input / $0.60 output | Cepat | Cukup (dengan template eksplisit) | **Default skill ini** |
| deepseek-v4-pro | ~$1.10 / $4.40 | Sedang | Tinggi | Kalau perlu reasoning kompleks |
| google/gemini-2.0-flash-exp:free | **$0** (free tier) | Cepat | Cukup | Budget nol, tapi rate-limited |
| meta-llama/llama-3.3-70b:free | **$0** | Sedang | Cukup | Alternatif free |
| anthropic/claude-sonnet-4.5 | ~$3 / $15 | Sedang | Sangat tinggi | Riset rumit, mahal |
| nous/hermes-4-pro | bervariasi | Cepat | Tinggi | Lewat Nous Portal |

**Suffix routing OpenRouter** (tambah ke nama model):
- `:floor` → sort by price (paling murah)
- `:nitro` → sort by throughput (paling cepat)
- `:cheapest` → alias floor
- `:fastest` → default

## Estimasi biaya harian (deepseek-v4-flash)

Asumsi: riset 1-2 jam/hari, ~10-20 riset task.

| Aktivitas | Token/hari | Biaya/hari |
|---|---|---|
| Riset kompetitor (1 task) | ~5,000-10,000 | ~$0.003-0.006 |
| Riset forum (1 task) | ~8,000-15,000 | ~$0.005-0.009 |
| 10 riset task sehari | ~80,000-150,000 | **~$0.05-0.10** |
| Cron job mingguan (auto) | ~20,000/minggu | ~$0.012/minggu |

**Estimasi bulanan:** **$2-5** untuk riset aktif harian.

## Strategi minimize biaya

### 1. Author sekali, pakai cheap model
Buat skill/template dengan model kuat (Claude/Opus) sekali. Lalu pin cron job ke model murah:
```bash
hermes cron add "0 9 * * 1" "<prompt>" \
  --model deepseek/deepseek-v4-flash-0731:floor \
  --provider openrouter \
  --name "Riset mingguan"
```

### 2. Free tier OpenRouter
27+ model free (`:free` suffix). Cukup untuk testing. Tapi rate-limited (tidak untuk production):
```yaml
model:
  default: "google/gemini-2.0-flash-exp:free"
  provider: openrouter
```

### 3. Local model (Ollama) untuk riset sensitif privacy
`$0` API cost, tapi butuh hardware (min 16GB RAM, GPU helps). **Fix context length dulu** (lihat `troubleshooting.md`):
```bash
# Modelfile
FROM gemma4:31b
PARAMETER num_ctx 64000
```

### 4. Cron watchdog (jangan bayar untuk "tidak ada perubahan")
Pakai `--monitor-script` atau `--no-agent` supaya cron job tidak bangunkan LLM kalau tidak ada perubahan:
```bash
hermes cron add "every 2h" "<prompt>" \
  --monitor-script ~/.hermes/scripts/price-watch.py \
  --name "Price watch"
```

### 5. Gateway history cap
Gateway mode (Telegram/WA) lebih mahal dari CLI (~2-3x token karena bawa history). Cap history:
```bash
hermes config set gateway.conversation_history_limit 10
```

## Biaya total realistis

| Skenario | Biaya bulanan |
|---|---|
| Riset 2-3x seminggu, deepseek-v4-flash | **$1-3** |
| Riset aktif harian + 1-2 cron job | **$3-8** |
| Riset intensif + model Claude sesekali | **$10-25** |

**Untuk konteks:** 1 cangkir kopi specialty = $2-4. Riset pasar sebulan ~ sama dengan 1 cangkir kopi. Return: keputusan bisnis yang jauh lebih informed.

## Monitoring biaya

- **OpenRouter dashboard** (https://openrouter.ai/credits) → real-time usage.
- **Hermes `/usage`** → token usage per session.
- **`/insights --days 7`** → usage insights 7 hari.
- Set **self-imposed credit limit** di OpenRouter supaya tidak kebablasan.

## Red flag biaya

- Tagihan >$50/bulan untuk riset personal → ada yang salah (mungkin cron job rakus).
- Token usage meroket tiba-tiba → cek cron jobs: `hermes cron list`.
- Gateway mode menghabiskan token cepat → cap history (di atas).
