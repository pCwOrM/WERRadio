# WERRadio (`rad.werr.io` / `werrad.io`)

**WERRadio**, WerrOzan 53-Koma & Güneş Dili AI müzik ekosisteminden beslenen, düşük bellekli (~120 MB RAM) ve minimum disk kullanımlı (<50 MB dönen arabellek) **7/24 kesintisiz internet radyosu** ve kurulabilir **PWA (App-Like)** radyo arayüzüdür.

## ⚡ 30 Saniyede Hızlı Başlangıç

```bash
git clone https://github.com/pCwOrM/WERRadio.git && cd WERRadio
python -m http.server 8080 --directory web
# Tarayıcıda aç: http://localhost:8080  (veya canlı yayın: https://rad.werr.io)
```

## Mimari

```text
[ ozan-api.werr.io (/v1/public/songs) ]
          │  (Fisher-Yates full-cycle shuffle, 1-2 track rolling buffer)
          ▼
[ lexsrv — Liquidsoap 2.2.4 + Icecast 2.4.4 (127.0.0.1:8000, 192 kbps MP3, 2.5s crossfade) ]
          │
          ▼
[ Apache2 (127.0.0.1:8088) + Cloudflare Tunnel ] ──► https://rad.werr.io / https://werrad.io
```

## Klasör Yapısı

- `web/` — Kurulabilir PWA radyo arayüzü (`index.html`, `manifest.webmanifest`, `sw.js`, `stream.m3u`, `icon-192.png`, `icon-512.png`).
  - Canlı **Şu An Çalıyor** (`/status-json.xsl` + Türkçe HTML entity çözümü + aynı kökenli `/catalog.json`).
  - Dinamik kayan sekme başlığı (`document.title`), kilit ekranı `MediaSession` ve mobil uyku/ağ kopması otomatik yeniden bağlanma (`scheduleReconnect`).
- `radio/` — Sunucu yayın bileşenleri:
  - `next_track.py`: Keşfet API'sinden sıradaki parçayı Fisher-Yates shuffle ile seçer, `/tmp/werrozan-radio/tracks` içinde en fazla 1–2 geçici dosya tutar ve `/var/www/rad.werr.io/catalog.json` önbelleğini günceller.
  - `werrozan.liq.example`: Liquidsoap 2.2.4 yapılandırma şablonu (`crossfade(duration=2.5)` + `mksafe`).
  - `icecast.xml.example`: `127.0.0.1:8000` yerel dinlemeli, mobil uyku dayanımlı (`queue-size: 2097152`, `burst-size: 131072`) Icecast2 şablonu.
  - `rad.werr.io.conf.example`: Güvenlik başlıklı Apache2 ters vekil şablonu.

## İşbirliği & Katkı Akışı

- `main` dalı **Branch Protection** ile korunmaktadır.
- Yeni özellik, arayüz veya kanal geliştirmeleri için kendi branch'inizde çalışıp **Pull Request (PR)** açın; `@pCwOrM` onayı sonrası `main`'e birleştirilir.

## Lisans

**Business Source License 1.1 (BSL 1.1)** — © 2026 ITouch Systems · Çukurova Üniversitesi Teknokent (ITouch Bilişim Sistemleri Ltd. Şti.). Detaylar için [LICENSE](LICENSE) dosyasına bakın.
