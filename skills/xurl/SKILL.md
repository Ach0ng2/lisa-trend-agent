---
name: xurl
description: Integrasi CLI resmi X/Twitter untuk posting, pencarian, interaksi timeline, DM, upload media, dan akses v2 API.
---

# xurl: Official X (Twitter) CLI

CLI resmi developer platform X untuk berbagai kebutuhan operasional akun X/Twitter.

## Kemampuan Utama
- Posting status, balasan (reply), quote tweet, dan hapus post.
- Pencarian konten, pembacaan timeline, serta monitoring mentions.
- Interaksi engagement: like, repost, bookmark, follow, dan DM.
- Pengunggahan file media (gambar dan video).
- Akses langsung ke seluruh endpoint v2 API.

## Protokol Keamanan Kredensial
- DILARANG menampilkan atau membaca isi file `~/.xurl` ke context percakapan.
- Jangan meminta pengguna memasukkan token atau kunci rahasia ke dalam chat.
- Pengaturan otentikasi awal dilakukan secara mandiri oleh user di luar sesi percakapan.
- Untuk memeriksa status autentikasi, hanya gunakan perintah: `xurl auth status`.
- Hindari penggunaan opsi verbose (`-v` atau `--verbose`) karena dapat mengekspos header autentikasi.

## Perintah Singkat
- Post baru: `xurl post "Pesan lo di sini"`
- Balas post: `xurl reply POST_ID "Balasan lo"`
- Quote post: `xurl quote POST_ID "Tanggapan lo"`
- Pencarian tweet: `xurl search "kata kunci" -n 10`
- Cek profil aktif: `xurl whoami`
- Unggah media: `xurl media upload path/ke/file.jpg`
