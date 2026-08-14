# marketing-orchestrator

Router untuk keenam skill marketing lainnya. Dia memutuskan **skill mana yang jalan
dan urutannya**, memegang peta **state bus** (siapa menulis apa, siapa membacanya),
dan menutup tiap sesi dengan bentuk yang sama.

Dia tidak menulis, tidak meriset, tidak mengirim.

## Install

```bash
cp -R marketing-orchestrator ~/.hermes/skills/marketing-orchestrator
```

## Kenapa ada

Tiap skill tahu dirinya sendiri. Tidak ada yang tahu urutannya, dan tidak ada yang
memiliki state bus. Akibatnya agen memilih skill dengan mencocokkan kata di kalimat
pertama pemilik usaha — dan pemilik warung yang cuma butuh 15 menit mengisi `sikap`
berakhir di positioning lab lengkap.

`tools-mapping.md` sebenarnya sudah menjawab sebagian, tapi dulu dia tinggal di dalam
`brand-strategy-coach/references/`, jadi lima dari enam skill tidak bisa melihatnya.
Sekarang dia di `shared/`.

## Perintah

| Perintah | Untuk apa |
|---|---|
| `bash scripts/status.sh` | **langkah pertama tiap sesi** — rem, profil, yang belum selesai, antrean, job |
| `bash scripts/help.sh` | rute & aturan "dibeli bukan dibangun" dalam satu layar |
| `bash scripts/doctor.sh` | periksa seluruh state bus terbaca |

## Aturan yang paling sering dilanggar

**Sebelum menulis script apa pun, tanya berurutan:**

1. Hermes sudah punya? (penjadwal, notepad job, monitor-mode, telemetri biaya,
   kartu persetujuan, transkripsi)
2. Alat yang sudah dibayar sudah punya? (Repliz: komentar, DM, jadwal posting,
   satu kotak masuk — mulai Rp 18.000 sekali bayar)
3. Baru bangun sendiri.

Yang **tidak** ditangani Repliz dan tetap milik skill kita: **WhatsApp** (WAHA) dan
**email** (Gmail SMTP/IMAP).

## Berkas bersama

Semua yang di `lib/`, `references/`, `scripts/`, dan `hooks/` disalin dari `shared/`
oleh `bash shared/sync.sh`. Jangan diedit di sini — edit yang kanonik.
