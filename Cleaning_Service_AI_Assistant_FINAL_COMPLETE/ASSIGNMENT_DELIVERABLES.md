# Assignment Deliverables — Cleaning Service

Dokumen ini memetakan project ke output yang diminta pada Panduan Tugas AI Business Assistant.

## 1. Business Problem Canvas

File: `business_case.md`

Berisi:
- User
- Pain
- Evidence
- Impact
- Problem Statement
- How Might We (HMW)

## 2. Problem Statement + HMW

File: `business_case.md`

Keduanya dibuat berdasarkan masalah operasional Cleaning Service, bukan langsung mengunci solusi ke chatbot/AI.

## 3. Source Code Adaptasi

File utama:
- `app.py`
- `ai_service.py`
- `schemas.py`
- `business_rules.py`

Perubahan mengikuti proses bisnis Cleaning Service. Bukan sekadar mengganti nama produk dari bakery.

## 4. Tiga Test Case

### A — Data Lengkap

> Selamat siang Kak, saya Andi. Saya ingin pesan Deep Cleaning sebanyak 1 layanan untuk rumah 2 lantai. Mohon tim datang langsung (onsite) pada Sabtu, 19 September 2026 pukul 09:00. Alamat lengkapnya Jl. Melati No. 18, Kelurahan Suka Maju, Kecamatan Medan Johor, Kota Medan. Catatan: tolong fokuskan pembersihan pada kamar mandi dan dapur.

Data yang sengaja dibuat lengkap:
- customer name
- service
- quantity
- service date
- service time
- property type
- property detail
- fulfillment
- address
- special note

Target pengujian: `READY`.

### B — Data Belum Lengkap

> Kak, saya mau pesan deep cleaning untuk rumah besok. Kira-kira bisa datang?

Data yang sengaja belum diberikan:
- customer name
- quantity
- exact service time
- address
- fulfillment
- property detail

Target pengujian: `NEEDS CONFIRMATION`. Layanan tetap harus dikenali dari katalog; harga satuan boleh ditampilkan, tetapi subtotal/total menunggu jumlah.

### C — Chat Natural / Masih Samar

> Kak, kalau Sabtu pagi rumah saya dibersihin bisa nggak? Rumahnya dua lantai, lokasinya kurang lebih daerah Sunggal. Jamnya fleksibel aja, nanti saya kabarin lagi ya.

Tujuan pengujian:
- menguji bahasa percakapan sehari-hari;
- membedakan informasi yang cukup pasti dari informasi yang masih samar;
- memastikan AI tidak mengarang jam, alamat, atau detail lain.

Target pengujian: `NEEDS CONFIRMATION`.

## 5. Screenshot

Ambil screenshot aktual dari aplikasi setelah testing:
- minimal 1 hasil `READY` dari Case A;
- minimal 1 hasil `NEEDS CONFIRMATION` dari Case B atau C.

Hasil screenshot harus berasal dari aplikasi yang benar-benar dijalankan.

## 6. Demo 3–5 Menit

Urutan yang disarankan:
1. Jelaskan User, Pain, Evidence, Impact, dan HMW.
2. Tunjukkan perubahan `schemas.py`, `ai_service.py`, dan `business_rules.py`.
3. Jalankan Case A dan tunjukkan `READY`.
4. Jalankan Case B/C dan tunjukkan `NEEDS CONFIRMATION`.
5. Jelaskan apa yang dipelajari dan jika ada hasil AI yang berbeda dari dugaan, sampaikan secara jujur.

## Rubrik yang ditargetkan

- Business Problem & Evidence: 20%
- Problem Statement & HMW: 15%
- Schema & AI Prompt: 15%
- Business Rules: 25%
- Testing: 15%
- Demo & Pemahaman Anggota: 10%

## Prinsip kejujuran

Project tidak mengklaim hasil AI yang belum benar-benar dijalankan. Hasil aktual testing harus dicatat setelah aplikasi diuji.
