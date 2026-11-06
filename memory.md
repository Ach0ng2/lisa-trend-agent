# Memory: Lisa (Content Writer untuk Tam)

## 1. Project Context & Setup Lingkungan
- Workspace Pribadi Tama: `/data/Tama` (ruang ide & konten personal)
- Channel Sheggario: Ario Pratomo (target 100K subs dalam 6 bulan dari 98.1K). Niche tech storytelling dikombinasikan dengan dinamika parenting/family (@curhatbapakibu). Jadwal upload rutin 1x seminggu long-form YT ditambah IG Reels.
- Direktori Kerja Sheggario:
  - Source Scripts (Read-Only): `/data/Sheggario/Existing/`
  - Output Baru & Guidelines (Read/Write): `/opt/data/data/sheggario/` (subfolder `guidelines/` dan `new/`)
- Penanganan File .docx:
  - Gunakan standalone python script via terminal (bukan sandbox) menggunakan library `python-docx`.
  - Bersihkan skrip helper setelah pembuatan dokumen selesai.

---

## 2. Riwayat Project & Catatan Produksi

### A. Acara Launching ASUS ProArt P16 (Update: 19 Okt 2026)
- Keperluan: Konten IG Reels dari peluncuran laptop seharga ~100 jutaan bersama Mas Ario.
- Poin Kunci: Pembahasan harga, prosesor NVIDIA RTX Spark N1X (arsitektur 6144-core GPU dan 20-core CPU dalam satu chip terpadu), serta perbandingan nilai terhadap MacBook M5 Max (~200 juta).
- Batasan Lapangan: Perangkat di lokasi peluncuran hanya berupa unit pajangan (display unit). Pengujian ketahanan baterai (on-battery) maupun uji alur kerja berat harian tidak memungkinkan untuk dilakukan di tempat.

### B. Riset Chery Q untuk Mba Nucha (Update: 1 Okt 2026)
- Keperluan: Riset fitur kendaraan listrik untuk IG Reels Mba Nucha (istri Mas Ario).
- Angle: Fitur teknologi yang relevan bagi sosok mom-preneur dalam keseharian (antar-jemput anak sekolah, mobilitas meeting kerja, hingga olahraga padel/tenis).

### C. Script Family Link Android (Update: 12 Okt 2026)
- Keperluan: Video edukasi YouTube bagi orang tua tentang pembatasan gadget anak, adaptasi dari versi iOS Parental Control terdahulu.
- Konsep: Menjadikan smartphone Android layaknya dumb phone terkelola (komunikasi keluarga, aplikasi belajar, dan kontrol durasi game) dengan ulasan objektif mengenai kelebihan, kekurangan, serta panduan praktis.

### D. Pengembangan & Promosi Aplikasi PerfBenchie (Update: 30 Okt 2026)
- Produk: Aplikasi Windows desktop buatan Tama sendiri (vibe-coded) untuk benchmarking performa game mobile via koneksi kabel USB tanpa instalasi di HP.
- Detail: Landing page di `https://perfbenchie-lp.pages.dev/`. Model bayar sukarela mulai Rp25.000 untuk lisensi seumur hidup tanpa akun/login. Posisinya sebagai alternatif praktis dan offline untuk GameBench dan PerfDog.
- Strategi Integrasi: Ditampilkan secara halus dan natural dalam video komparasi Mas Ario (Poco F9 Ultra vs S26 Ultra). Data performa frame time, jank rate, dan latency ditunjukkan terlebih dahulu, baru aplikasinya diulas singkat dari sudut pandang kemudahan pakai.

### E. Komparasi Poco F9 Ultra vs Samsung S26 Ultra (Update: 30 Okt 2026)
- Konsep: Komparasi performa chipset sekelas dengan rentang harga yang berbeda jauh, pengujian multitasking, gaming dengan PerfBenchie, fitur AI on-device vs cloud, dan opini anak-anak Mas Ario.
- Data Kamera: Borneo melakukan pengujian foto dan video di lapangan.

### F. Video S26 Ultra Jadi Gaming PC (Update: 15 Okt 2026)
- Hasil: Video telah tayang dan menembus hampir 10K views per pertengahan Oktober 2026.
- Alur: Menyorot 8 bulan pemakaian harian S26 Ultra, kabar DeX for PC, dan 4 level kapabilitas (pekerjaan dokumen ringan, game Android via Play Store, emulasi game konsol retro, hingga emulasi PC game AAA).

### G. Video OPPO Find X9 Ultra Camera (Update: Awal Okt 2026)
- Status: Video komparasi kamera hasil riset pre-shoot Tama telah diproduksi dan tayang (5.800+ views).

### H. Review ROG Xbox Ally X20 Anniversary Edition (Update: 5 Nov 2026)
- Keperluan: Video review YouTube long-form unit pinjaman 2 minggu ROG Xbox Ally X20 (RC74XA) dan aksesoris ROG Bulwark Dock (DG300).
- Persona Mas Ario: First-time Xbox Ally user, gamer bapak-bapak yang jam mainnya sempit ("masih mau main game tapi seringkali gak jadi karena gak ada waktu").
- Preferensi Struktur Naskah Tama:
  1. Section headers sederhana: `[HOOK]`, `[BUMPER]`, `[FIRST IMPRESSION & BUILD]`, `[DISPLAY & AUDIO]`, `[GAMING TEST]`, `[LARGER SCREENS]`, `[KESIMPULAN & CTA]`.
  2. Data gaming test wajib berbasis pengujian on-battery Mode Turbo nyata (COD MW4, Forza Horizon 6, Cyberpunk 2077, Street Fighter V).
  3. Detail hardware kunci: Layar OLED 7.4 inci 120Hz VRR (FreeSync Premium Pro), Joystick magnetik TMR anti-drift, Transforming D-pad rotasi 4/8 arah, speaker stereo Dolby Atmos, dan ROG Bulwark Dock 7-in-1 dengan flip cover stand.
  4. Ergonomi & pemakaian riil: Rekomendasi posisi tengkurap / ganjal bantal atau sandaran meja agar tidak pegal mengangkat 756g.
  5. Closing CTA: Selipkan ajakan subscribe sebelum signature "By Now, Be Nice!".

---

## 3. Preferensi Kerja & Standar Naskah Baru (Update: 6 Nov 2026)
- **Riset Eksternal Wajib saat Brainstorm**: Setiap kali Tama mengajak brainstorm topik baru/trending, Lisa WAJIB mencari keluar (external research via web search, berita brand resmi, komunitas tech terkini seperti Reddit r/gadgets, The Verge, Engadget, X, dll). DILARANG hanya berputar pada apa yang sudah ada di memory internal workspace.
- **Tools Riset Eksternal (AI Research Skills)**:
  - Referensi: `orchestra-research/AI-research-SKILLs` dan `WenyuChiou/ai-research-skills`.
  - PENGGUNAAN: HANYA untuk fase research (literature/web triage, fact-checking, gap-to-topic analysis, sintesis bukti konkret). DILARANG KERAS dipakai untuk menulis naskah/script. Penulisan naskah tetap eksklusif menggunakan skill `sheggario-script-writing`.
- **Constraint Acara Launching**: Jangan pernah menyarankan uji coba baterai seharian atau uji render berat saat Mas Ario menghadiri acara launching, karena unit hanya dipajang.
- **Kedalaman Riset**: Sajikan data spesifikasi konkret yang siap dibahas Mas Ario, hindari saran umum yang mengambang.
- **Standar Format Naskah Baru** (dari hasil revisi docx Poco F9 Ultra vs S26 Ultra):
  1. Hook dibuka dengan pertanyaan pembanding bertema "Tapi...". Untuk konten short-form (Reels/TikTok), sediakan 2-3 variasi opsi Hook ([HOOK], [HOOK 2], [HOOK 3]) dengan angle berbeda (lugas, target gamer/FOMO, dan brand-safe).
  2. Pembagian bab atau chapter menggunakan penomoran runtut atau label kurung siku sederhana ([HOOK], [TOPIK UTAMA], [PLOT TWIST], [KESIMPULAN]).
  3. Angka spesifikasi selalu dibungkus cerita pengalaman dan kesan pemakaian nyata (verdict feel).
  4. Celah data teknis langsung digantikan dengan demonstrasi B-roll visual di video.
  5. Catatan visual produksi dimasukkan rapi dalam komentar naskah (misal: Add B-Roll, Insert text) atau cues kurung siku sederhana ([SHOW: ...], [TOS: ...]).
  6. Call to action diarahkan untuk meminta masukan dan diskusi hangat, bukan jualan agresif. Pada short-form, arahkan tonton full review di YouTube.
  7. Alasan keputusan pribadi Mas Ario ditekankan pada kenyamanan ekosistem perangkat.
  8. Naskah bersih total: buang checklist persiapan, tabel kaku, timestamps per detik, disclaimer kondisi lab, dan daftar link dari tubuh naskah.
  9. Format styling dokumen .docx: TEKS POLOS HITAM (NO COLORS, tanpa warna biru/merah dsb). Catatan khusus atau tips produksi SELALU di chat, jangan masuk ke dokumen .docx.
  10. **Brand Relationship & Tone Etiquette (PENTING)**: Mas Ario sangat menjaga hubungan baik dengan brand (khususnya Samsung). Dilarang keras memakai framing agresif yang mendiskreditkan/menjelekkan brand atau produk mahal (hindari kata seperti "ngapain buang duit...", "dibikin malu...", dsb). Gunakan framing yang elegan, berbasis rasa penasaran (curiosity), objektif, atau framing underdog yang ngasih kejutan tanpa merendahkan flagship incumbent ("S26 Ultra udah jadi daily driver andalan gue...").

---

## 4. Skills & Alat Bantu Terdaftar
- **sheggario-script-writing**: Penulisan skrip tech YouTube/Reels/TikTok dengan karakter khas Mas Ario (bilingual natural, humor wordplay, jujur dengan kekurangan kecil, closer wajib "By Now, Be Nice!").
- **xurl (v1.1.1)**: CLI resmi developer platform X untuk posting, quoting, search, timeline, media upload, dan interaksi v2 API dengan keamanan token tingkat tinggi.
- **youtube-seo (v1.1.1)**: Formulasi judul di bawah 60 karakter, optimasi meta deskripsi di bawah 160 karakter, panduan thumbnail kontras tinggi, dan penyelarasan untuk pencarian Google serta kutipan AI Overviews (GEO).
- **humanizer & stop-slop**: Standar pembersihan tulisan dari pola kaku AI (memangkas filler, memvariasikan ritme kalimat, menghilangkan polaritas klise, mengutamakan kalimat aktif, dan membuang em dash secara mutlak).
- **content-research-writer**: Kolaborasi pembuatan outline, riset data pendukung terverifikasi, perbaikan hook pembuka, dan evaluasi naskah per bagian secara iteratif.

---

## 5. Trend Intelligence Agent & Telegram Automation (Update: 6 Nov 2026)
- **Folder Project**: `trend_agent/` (terpisah dan bersih dari dokumen naskah harian).
- **Bot Telegram**: `@LisaaWriter_bot` (Bot Token terdaftar).
- **ID Chat Personal Tama**: `5743390596`.
- **API Keys Aktif**:
  - Google Gemini API (`GEMINI_API_KEY` via AI Studio Free Tier).
  - YouTube Data API v3 (`YOUTUBE_API_KEY` via Google Cloud Console Free Tier).
- **Format Laporan & Konten (NON-NEGOTIABLE dari Tama)**:
  1. **Closing Phrase**: `By Now, Be Nice!` HANYA untuk naskah/script video Mas Ario. DILARANG KERAS dipakai di chat, notifikasi bot, laporan tren, atau pesan Lisa ke Tama.
  2. **Struktur Laporan Bot**: Hapus bagian `Angle YouTube (Long-Form)` dan `Opsi Hook Reels/Shorts Mas Ario`. Fokus pada: Nama Topik, Klasifikasi Tren, Arbitrage Score & Status Pasar, serta Bukti Video (Long-Form & Short-Form).
  3. **Filter Bahasa & Kualitas Video**:
     - Wajib HANYA video berbahasa **Indonesia atau Inggris** (alfabet Latin murni, tolak karakter Arab, Devanagari/India, Thai, Cyrillic, Mandarin).
     - Buang video destruktif/siksaan fisik ekstrem (seperti hot metal ball 1000°C, blender, drop test ekstrem) yang tidak masuk akal diproduksi Mas Ario & Tama. Prioritaskan review, comparison, hands-on, unboxing, camera/gaming test, atau tips tech nyata.
  4. **Interaksi Chatbot Telegram & 6 Pilar Konten**:
     - Bot listener WAJIB memahami 6 Content Pillars Mas Ario (contoh perangkat/software HANYA acuan tema, Gemini WAJIB eksploratif mencari nama produk/software baru):
       1. **Useful Softwares & Everyday Apps**: LocalSend, Life360, GoodNotes, Family Link, Raycast, Obsidian, Bitwarden, KDE Connect.
       2. **Handheld & Mobile Gaming**: ROG Ally, Steam Deck, DroidDeck, Odin 2, RedMagic, Gamesir, emulasi game mobile.
       3. **Creator Gear & Audio**: DJI Mic 2, Osmo Pocket 3, Rode Wireless, Sony ZV-E10, Insta360 Ace Pro.
       4. **Smartphones & Flagship Comparisons**: Samsung Galaxy S, Vivo X, Xiaomi Ultra, iPhone Pro, Pixel.
       5. **AI & Next-Gen Computing**: DeepSeek, Ollama, Ray-Ban Meta, RTX 50 series, Snapdragon X Elite.
       6. **Productivity & Ecosystem Workflow**: MacBook M-series, iPad Mini/Pro, Samsung DeX setup, multi-device sync.
     - Jika Tama meminta opsi lain ("opsi lain", "kurang suka"), jalankan pipeline rotasi pilar dan simpan `seen_history` agar DILARANG mengulang nama produk/software yang sudah pernah disajikan sebelumnya.
     - Jika Tama meminta menelaah topik spesifik (misal: "Lis, kalo droiddeck gimana?"), bot otomatis menjalankan riset pasar YouTube (views terbanyak & VPH tertinggi berbahasa Indo/Inggris) dan merespon dalam format kartu laporan yang sama.
- **Otomasi Cloud (Zero Cost)**: `.github/workflows/daily_trend.yml` terjadwal cron setiap pukul 00.50 UTC (~07.50 WIB) sebelum jam kerja pagi.
- **GitHub Repository**: `https://github.com/Ach0ng2/lisa-trend-agent` (Verified Live & Run #1 Success in 22s).
