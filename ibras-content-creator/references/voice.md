# Brand Voice — Bangun + Rawat

Voice = alasan orang kenal kamu, bukan kompetitor. Tanpa voice match, output AI
terdengar generik = AI-slop. Skill ini **mewajibkan** voice profile sebelum
generate konten apapun.

## Cara bangun voice profile (sekali, 30 menit)

### 1. Kumpulkan 3-5 sampel konten terbaik
Pilih post yang:
- Dapat engagement tertinggi (relative)
- Yang kamu bangga publish
- Yang "terdengar seperti kamu" saat baca ulang

Save sebagai `.txt` / `.md` di satu folder.

### 2. Ekstrak via voice-profile.sh
```bash
bash scripts/voice-profile.sh ~/my-samples/
```
Script minta Hermes ekstrak 8 atribut voice:
1. Tone
2. Kosakata khas
3. Kosakata yang dihindari
4. Struktur kalimat
5. Penggunaan emoji
6. CTA khas
7. Sudut pandang
8. Tanda tangan (catchphrase/sign-off)

### 3. Review + simpan ke USER.md memory
Output voice profile dari Hermes → kamu review → simpan ke Hermes memory:
```
Save this as my brand voice profile in USER.md: <paste summary>
```

Setelah ini, semua konten yang Hermes draft akan inherit voice ini.

## Cara mengetes voice match

Setelah simpan profile, test:
```bash
bash scripts/caption.sh "topic yang kamu biasa bahas" --platform instagram
```
Baca output. Pertanyaan test:
- "Kalau saya tidak publish ini, orang bisa nebak ini saya?" → kalau tidak, voice belum match
- "Ada kalimat yang terdengar seperti AI?" → edit yang itu, re-run profile

## Voice profile bukan statik — evolve

Voice kamu berubah seiring:
- Audience grow + feedback
- Kamu eksperimen tone baru
- Brand pivot

**Re-extract voice profile setiap 20-30 post baru.** Voice yang stale = konten
yang tidak resonate lagi.

```bash
# Setiap 20 post, update profile dengan sampel baru
bash scripts/voice-profile.sh ~/my-samples-recent/
```

## Voice attributes — contoh nyata

Profile yang baik punya **spesifik**, bukan generic.

❌ **Generic (tidak berguna):**
> Tone: friendly. Emoji: kadang. CTA: follow.

✅ **Spesifik (actionable):**
> Tone: santai-tapi-jelas, kadang ironis (terutama soal hype kopi), never preachy.
> Kosakata khas: "ngopi", "bijian" (bukan "biji"), "manual brew" (bukan "seduh manual").
> Dihindari: "revolusioner", "game-changer", "karya anak bangsa" (cringe).
> Struktur: kalimat pendek. Hook di baris 1. Question di akhir.
> Emoji: max 1-2 per post. Kopi ☕ khas. 🤎 kalau sentimental.
> CTA: "komen kalau..." (question ringan), bukan "follow for more" (pushy).
> Sudut pandang: first-person "saya", kadang "kita" kalau ajakan.
> Tanda tangan: "— Andi" kalau formal, no sign-off kalau casual reel.

## Anti-pattern voice

- ❌ **Voice chameleon** — berubah tiap post (audience bingung)
- ❌ **Voice over-imitate** — copy influencer lain (inauthentic)
- ❌ **Voice corporate** — kaku, jargon (kecuali B2B emang gitu)
- ❌ **Voice AI-default** — "In this article, we will explore..." (beneran AI bau)
- ❌ **Voice inconsistent** — formal di LinkedIn, slang di IG (ok kalau intentional, not ok kalau accident)

## Kalau belum punya voice (creator baru)

OK. Itu normal. Cara develop:
1. **Posting 30 hari, journal mana yang feels right.**
2. Setelah 30 post, ekstrak profile dari 3-5 yang paling "kamu".
3. Iterate.

Voice bukan di-design di depan. Voice di-discover dari praktik.

## Voice + platform: adaptasi, bukan ganti

Voice inti sama, tapi adaptasi per platform:
- **LinkedIn**: voice kamu + tone sedikit lebih profesional (tapi tidak fake-corporate)
- **TikTok**: voice kamu + lebih casual + visual hook kuat
- **X**: voice kamu + lebih punchy (280 char)
- **Instagram caption**: voice kamu + lebih visual description
- **YouTube**: voice kamu + lebih conversational + structured

Skill ini tahu platform-aware. Tapi **kamu** yang confirm voice match.
