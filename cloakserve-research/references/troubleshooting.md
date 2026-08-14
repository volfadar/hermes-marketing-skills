# Troubleshooting — cloakserve-research skill

Urut berdasarkan gejala. Jalankan `bash scripts/doctor.sh` dulu untuk diagnosis otomatis.

## Install / Start

### `docker: command not found`
**Sebab:** Docker belum terinstall.
**Fix:** Install Docker Desktop (Mac/Windows) atau Docker Engine (Linux). https://www.docker.com/products/docker-desktop

### `docker: Cannot connect to the Docker daemon`
**Sebab:** Docker daemon belum jalan.
**Fix:** Start Docker Desktop (Mac/Windows) atau `sudo systemctl start docker` (Linux). Tunggu icon hijau, re-run `initialize.sh`.

### `cloakserve: FAILED to become ready in 180s`
**Sebab:** Pertama kali download stealth Chromium binary (~150MB) bisa lambat di koneksi Indonesia.
**Fix:**
1. Cek log: `docker logs cloakserve` — kalau ada progress download, tunggu lebih lama.
2. Restart: `bash scripts/stop.sh && bash scripts/start.sh`.
3. Kalau tetap gagal: hapus container + image, re-pull:
   ```bash
   bash scripts/stop.sh
   docker rmi cloakhq/cloakbrowser:latest
   bash scripts/start.sh
   ```

### Port 9222 sudah dippakai
**Sebab:** Aplikasi lain sudah pakai 9222 (biasanya Chrome debug port).
**Fix:** Pakai port lain: `bash scripts/initialize.sh --port 9223` (dan update `wire-hermes.sh --port 9223`).

## CDP / Browser

### `/json/version` returns 502 / connection refused
**Sebab:** Container jalan tapi inner Chromium masih booting, atau crash.
**Fix:**
1. `bash scripts/status.sh --logs` → cek log.
2. Kalau "Chrome ready" belum muncul di log, tunggu 60 detik lagi.
3. Kalau ada error `Missing X server` di log — image butuh `--shm-size=1g` (start.sh sudah set, tapi kalau kamu run manual docker pastikan flag itu ada).
4. Restart container: `bash scripts/stop.sh && bash scripts/start.sh`.

### Browser navigate tapi konsol ke tab "New Tab" (bukan tab target)
**Sebab:** cloakserve multiplexer kadang buka tab default lebih dulu.
**Fix:** Otomatis. Hermes akan recover dengan `Target.getTargets + Runtime.evaluate`. Kalau sering terjadi, tambahkan di prompt:
> "Rute langsung ke tab target via Target.getTargets + Runtime.evaluate."

### Tokopedia/Shopee minta Captcha
**Sebab:** Frekuensi terlalu tinggi, atau fingerprint kurang bervariasi.
**Fix:**
1. Pelankan riset. Jangan 50 halaman dalam 5 menit.
2. Pakai Tailscale exit node (residential IP lebih jarang kena Captcha).
3. Ganti fingerprint seed: `bash scripts/start.sh --fingerprint-seed brand-b`.
4. Kalau tetap, pindah ke platform lain dulu (Shopee vs Tokopedia).

## Hermes

### Error "404 No endpoints found that support tool use"
**Sebab:** Config kehilangan `model.default`. Bug versi awal `wire-hermes.sh` — sudah diperbaiki.
**Fix:** Jalankan `bash scripts/doctor.sh` — akan tunjukkan kalau model.default hilang. Atau edit manual `~/.hermes/config.yaml`:
```yaml
model:
  default: "deepseek/deepseek-v4-flash-0731"
  provider: "openrouter"
```

### Hermes timeout 300s saat disuruh "ikuti SKILL.md"
**Sebab:** Model lemah (deepseek-v4-flash) tidak kuat multi-step abstrak.
**Fix:** Pakai `bash scripts/research.sh "<query>"` (yang pakai template eksplisit). Atau copy template dari `templates/*.txt` langsung.

### Browser tool tidak muncul di Hermes
**Sebab:** `browser` tool belum di-enable, atau `browser.cdp_url` tidak ter-set.
**Fix:**
1. `bash scripts/status.sh` — pastikan "wired: yes".
2. `hermes tools` → pastikan "browser" enabled.
3. Re-run `bash scripts/wire-hermes.sh`.

### Hermes pakai model lain (bukan deepseek-v4-flash) setelah setup
**Sebab:** Config sebelumnya menimpa.
**Fix:** `hermes config set model.default "deepseek/deepseek-v4-flash-0731"` dan `hermes config set model.provider openrouter`.

## Tailscale

### `tailscale up` hang
**Sebab:** Butuh login browser interaktif.
**Fix:** Tailscale akan print URL. Copy ke browser, login dengan akun Tailscale, approve mesin.

### HP tidak muncul di `tailscale status`
**Sebab:** HP belum login dengan akun yang sama, atau belum approve.
**Fix:**
1. Pastikan HP login akun Tailscale yang sama.
2. Buka https://login.tailscale.com/admin/machines — approve HP.
3. Di HP, enable "Run as exit node".

### Setelah `tailscale up --exit-node=...`, internet mati
**Sebab:** HP tidak online / tidak approve / route error.
**Fix:** `sudo tailscale up --exit-node=` (kosong) untuk kembali direct.

## Permission / Sudo

### `permission denied while trying to connect to the Docker daemon socket`
**Sebab:** User tidak di grup docker.
**Fix:** `sudo usermod -aG docker $USER && newgrp docker`. Logout/login kalau perlu.

### `tailscale up` minta sudo
**Normal.** Tailscale butuh root untuk network config. Pakai `sudo`.

## Etika /_BLOCK

### Situs tidak bisa diakses walau publik (403, anti-bot challenge)
**Sebab:** Site sangat ketat anti-bot-nya, atau geo-block.
**Pilihan:**
1. Pakai Tailscale exit node Indonesia.
2. Cari sumber data alternatif (situs aggregator, blog, API publik).
3. **JANGAN** paksa dengan teknik yang melanggar ToS. Lihat `ethics.md`.

### Hermes bilang "Saya tidak bisa melanjutkan karena ini butuh login"
**Ini fitur, bukan bug.** Skill ini sengaja minta Hermes menolak riset yang butuh login. Riset publik saja.

## Masalah lain?

1. `bash scripts/doctor.sh` untuk diagnosis otomatis.
2. `bash scripts/status.sh --logs` untuk lihat log container.
3. Restart bersih: `bash scripts/stop.sh && bash scripts/initialize.sh --force`.
