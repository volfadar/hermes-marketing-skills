# Anti-Ban — Cara Tidak Kena-Banned WhatsApp

> **Baca ini dulu sebelum kirim apapun via WAHA.** Ini ringkasan dari
> [panduan resmi WAHA](https://waha.devlike.pro/docs/overview/how-to-avoid-blocking/)
> + consensus komunitas. Bukan hard guardrails — **soft warnings**. Tapi
> pelanggaran = akun banned, tidak bisa banding, tidak bisa pulihkan.

## Sistem "poin" WhatsApp (model mental)

WhatsApp tidak publish angka pasti, tapi perilaku mereka konsisten dengan sistem poin:

```
  + poin: percakapan 2-arah (orang reply kamu)
  + poin: orang save nomor kamu ke kontak mereka
  - poin: orang mark kamu sebagai spam (Report)
  --- poin: orang block kamu
  - poin: message ke nomor yang belum save kamu
  - poin: pattern bot-like (fixed interval, identical text)
  
  Kalau poin < 0 → BANNED permanen
  Rule of thumb: "di-tag spam 5-10x = banned"
```

## Trigger utama banned (urutan bahaya)

1. **Cold outreach ke nomor yang belum save kamu** — #1 penyebab. Mereka dapat
   prompt "Apakah ini spam?" → sekali klik = 1 strike.
2. **Pesan identik ke banyak orang** — WhatsApp detect fingerprint text.
3. **Fixed interval (sistematis)** — 100 pesan tiap tepat 5 detik = obvious bot.
4. **Broadcast massal tanpa opt-in** — kombinasi #1 + #2 + #3.
5. **Number baru tanpa profil** — no photo, no name, no status = suspect.
6. **Link flaggy** — domain yang pernah di-flag spam, atau URL shortener tertentu.
7. **Volume tinggi di hari pertama** — number baru kirim 1000 pesan = instabanned.
8. **Restart/logout saat di-shadow-restrict** — ini yang WAHA spesifik warn.

## Shadow restriction (error 463)

**Gejala:** pesan ke kontak BARU gagal dengan HTTP 463 dari WAHA.
Session tetap WORKING. Pesan ke kontak yang sudah ada tetap jalan.

**Arti:** WhatsApp silently restrict kamu. Bukan banned permanen — restriksi
"cooling off".

**YANG HARUS KAMU LAKUKAN:**
- ✅ **STOP semua outreach ke nomor baru** selama 24-72 jam.
- ✅ Tunggu. Restriction lift otomatis.
- ✅ Lanjut percakapan yang sudah ada (reply inbound aman).

**YANG TIDAK BOLEH:**
- ❌ **JANGAN restart session.**
- ❌ **JANGAN logout.**
- ❌ **JANGAN re-pair/scan QR ulang.**
- ❌ **JANGAN paksa kirim ke nomor baru.**

Restart saat restriction = WhatsApp anggap kamu "panik cleanup" = banned permanen.

## Aturan volume (community consensus, bukan official)

| Umur akun | Max pesan/hari (broadcast) | Catatan |
|---|---|---|
| < 7 hari | **50** atau kurang | Sangat fragile. Warm-up dulu. |
| 7-30 hari | 100-200 | Mulai aman, masih hati-hati. |
| 30-90 hari | 200-400 | "Warmed up". |
| > 90 hari, aktif 2-arah | 400-500 | Account established. |
| Business official (green tick) | lebih tinggi | Tapi tetap bukan free pass. |

**Per kontak per jam:** max **4 pesan** (yang reply kamu). Lalu stop 1 jam.

> `lib/broadcast.py` mengimplementasi aturan 4/jam ini otomatis via
> cooldown tracking di `~/.waha-marketing/state/sent.json`.

## Humanisasi (HALF wajib, setengahnya)

| Praktik | Implementasi di skill ini |
|---|---|
| **Random delay, bukan fixed** | `DELAY_MIN=12s, DELAY_MAX=45s` + jitter ±25%, plus length factor |
| **Typing indicator sebelum kirim** | `startTyping` → sleep → `stopTyping` → send |
| **Mark seen dulu** | `sendSeen` sebelum reply (recommended WAHA docs) |
| **Message variation** | Rotate 5+ template, insert `{name}`, random double-space |
| **Batch pause** | Setiap 20 pesan, pause 5-15 menit |
| **Jangan 24/7** | Kasih "jam kerja" (mis. 9am-9pm WIB), jangan broadcast tengah malam |
| **Group by area code** | WhatsApp expect kamu chat orang region sama (opsional, advanced) |

## Profil number baru (wajib sebelum broadcast apapun)

Sebelum pakai nomor untuk marketing, **lengkapi profil dulu**:
1. Photo profil (jangan logo generic — foto manusia/wajah lebih baik)
2. Display name yang manusiawi
3. Status / "about" yang jelas
4. Biarkan 3-7 hari dengan **percakapan manual** (keluarga, teman) sebelum broadcast
5. Ideal: minta beberapa orang save nomor kamu ke kontak mereka

## Opt-in: tidak opsional (etika + survival)

**Hanya kirim ke orang yang EXPLICITLY opt-in.** Maksudnya:
- ✅ Isi form di landing page kamu "Saya mau update via WA"
- ✅ Reply ke WA kamu "YES, saya mau info"
- ✅ Check box di checkout "kirim update via WA"
- ✅ DAFTAR eksplisit di workshop/event kamu

**TIDAK termasuk opt-in:**
- ❌ Nomor dari business card yang kamu kumpul di event
- ❌ Lead dari LinkedIn/email yang belum consent WA
- ❌ "Mereka pasti tertarik, kan?" → tidak. Itu spam.
- ❌ Pembeli sekali 3 tahun lalu yang tidak consent newsletter

`lib/broadcast.py` **menolak** kirim ke kontak yang `opt_in != yes` di CSV.
Itu bukan kemalasan — itu survival.

## Content rules

| ✅ Oke | ❌ Avoid |
|---|---|
| Personalized (pakai nama) | Identical template ke semua |
| 1 pesan pendek pembuka, tunggu reply | Spam 5 pesan panjang beruntun |
| Relevan dengan apa mereka opt-in | "Promo bulanan" ke orang yang opt-in untuk "tutorial" |
| Link ke domain kamu sendiri | Link shortener (bit.ly) atau domain flaggy |
| Tawarkan opt-out ("balas STOP") | Tidak ada cara unsub |
| Bahasa manusia, tidak pushy | Hype, ALL CAPS, banyak emoji |

## Kill switch

Kalau ada yang salah (spam report banyak, restriction muncul, dst.):

```bash
bash scripts/emergency-halt.sh
```

Ini touch `/tmp/waha-broadcast-halt`. Broadcast yang berjalan stop di message
boundary berikutnya (dalam ~1 pesan). Setelah issue clear: `rm /tmp/waha-broadcast-halt`.

## Red flag (kapan HARUS berhenti)

- ✗ Error 463 muncul → stop, baca "Shadow restriction" di atas
- ✗ Banyak kontak reply "salah siapa?" / "stop" → list kamu kotor, hentikan
- ✗ Promosi mendadak turun → kemungkinan shadow-restricted
- ✗ Kamu merasa "ini agak spammy" → kemungkinan besar iya

## Checklist pre-broadcast (print, tempel)

- [ ] Akun sudah berumur 7+ hari, profil lengkap
- [ ] 100% kontak opt-in eksplisit (bisa dibuktikan)
- [ ] 5+ message template dengan variation
- [ ] Personalisasi `{name}` (bukan identik)
- [ ] Delay randomized (skill ini otomatis)
- [ ] Typing indicator on
- [ ] Daily cap sesuai umur akun
- [ ] Halt file siap (`emergency-halt.sh` di tangan)
- [ ] Ada opt-out mechanism ("balas STOP")
- [ ] Content relevan dengan alasan mereka opt-in

Kalau ada ✗ di atas, **jangan broadcast dulu**.
