# Business Problem Canvas — AI Smart Cleaning Service Assistant

> Dokumen ini mengikuti format tugas AI Business Assistant Remix Challenge.
> Cleaning Service dipilih sebagai konteks bisnis baru; bukan sekadar mengganti nama produk.

## 1. USER

**Siapa yang paling sering melakukan pekerjaan ini?**

Owner/admin UMKM cleaning service yang menerima chat customer melalui WhatsApp atau Instagram dan harus mengubah chat tersebut menjadi order yang siap diproses.

## 2. PAIN

**Bagian mana yang merepotkan, lambat, berulang, atau rawan salah?**

Admin harus membaca chat bahasa natural lalu mencari layanan, jumlah, tanggal, jam, tipe properti, dan alamat. Informasi sering tersebar atau tidak lengkap. Admin kemudian harus bertanya ulang dan menghitung harga dari katalog.

## 3. EVIDENCE

**Apa bukti yang Anda punya atau apa yang akan Anda cek?**

Untuk tugas kelas ini kami tidak mengklaim memiliki data customer nyata. Evidence yang akan dicek adalah hasil pengujian tiga chat dummy yang sengaja dibuat untuk mewakili:
1. data lengkap,
2. data kurang,
3. bahasa natural/ambigu.

Kami akan membandingkan hasil AI dengan field yang memang tertulis di setiap chat dan mencatat kesalahan jika ada.

## 4. IMPACT

**Apa akibat masalah tersebut bagi user atau bisnis?**

Jika detail terlewat, admin harus melakukan follow-up berulang, jadwal dapat salah, petugas dapat datang tanpa alamat/detail yang cukup, dan harga atau rekap order dapat tidak konsisten.

---

# Problem Statement

**Owner/admin UMKM cleaning service membutuhkan cara untuk mengubah chat customer menjadi data order yang lengkap dan terstruktur karena pencatatan manual dapat melewatkan layanan, jadwal, tipe properti, atau alamat, sehingga proses follow-up dan penjadwalan menjadi lebih lambat dan rawan salah.**

# How Might We (HMW)

**Bagaimana kita dapat membantu admin cleaning service memastikan informasi order dari chat customer lengkap dan jelas sebelum order diproses?**

> HMW tidak mengunci solusi pada AI. AI hanya menjadi salah satu cara untuk membantu kebutuhan tersebut.

---

# Adaptasi dari Starter Project Bakery

| Bagian | Bakery Starter | Cleaning Service Version | Alasan |
|---|---|---|---|
| Catalog | Product + harga | Service + harga | Cleaning menjual jasa |
| Data utama | product_name, quantity | service_name, quantity | Yang dipesan adalah layanan |
| Jadwal | delivery_date | service_date + service_time | Petugas perlu datang pada waktu tertentu |
| Lokasi | delivery_address | service address | Petugas datang ke lokasi customer |
| Data konteks | - | property_type + property_detail | Tipe dan kondisi properti memengaruhi kebutuhan cleaning |
| AI | Memahami chat produk | Memahami chat jasa, jadwal, properti, alamat | Konteks bisnis berubah |
| Business Rules | Harga + field wajib | Harga + validasi service, jadwal, properti, alamat | Aturan operasional cleaning berbeda |

---

# Minimal 3 Business Rules yang Berbeda dari Bakery

1. **Service Catalog Rule**  
   Layanan harus cocok dengan katalog cleaning dan quantity harus jelas. Harga diambil dari Python, bukan dari AI.

2. **Onsite Address Rule**  
   Cleaning service demo dilakukan onsite. Jika alamat belum ada, order tidak boleh READY.

3. **Property Type Rule**  
   Tipe properti wajib diketahui dan harus termasuk Rumah, Apartemen, Kantor, Ruko, atau Villa.

4. **Exact Schedule Rule**  
   Tanggal dan jam harus cukup pasti. Kata "pagi", "sore", atau "minggu depan" tanpa informasi yang cukup membuat order NEEDS CONFIRMATION.

---

# Peran AI dan Business Rules

## AI / Gemini
- memahami bahasa natural,
- mengenali layanan dan jumlah,
- memahami tanggal relatif seperti "besok",
- mengambil tipe properti dan alamat,
- mengenali informasi yang ambigu,
- membuat ringkasan dan draft follow-up.

## Python / Business Rules
- mengambil harga dari service catalog,
- menghitung subtotal dan total,
- memastikan layanan valid,
- memastikan tanggal dan jam tersedia,
- memastikan tipe properti valid,
- memastikan alamat onsite tersedia,
- menentukan READY / NEEDS CONFIRMATION.

**AI understands. The system controls.**

---

# 3 Test Cases

Sesuai panduan, tiga case harus menunjukkan complete, missing, dan natural/ambiguous.

## Tiga Test Case untuk Pengujian

Pengujian mengikuti tiga kondisi yang diminta pada assignment: data lengkap, data kurang, dan chat natural/ambigu. Hasil aktual tetap harus dicatat setelah aplikasi benar-benar dijalankan.

### Case A — Data Lengkap

> Selamat siang Kak, saya Andi. Saya ingin pesan Deep Cleaning sebanyak 1 layanan untuk rumah 2 lantai. Mohon tim datang langsung (onsite) pada Sabtu, 19 September 2026 pukul 09:00. Alamat lengkapnya Jl. Melati No. 18, Kelurahan Suka Maju, Kecamatan Medan Johor, Kota Medan. Catatan: tolong fokuskan pembersihan pada kamar mandi dan dapur.

Field yang tersedia:
- Customer: Andi
- Service: Deep Cleaning
- Quantity: 1
- Date: 2026-09-19
- Time: 09:00
- Property type: Rumah
- Property detail: 2 lantai
- Fulfillment: onsite
- Address: Jl. Melati No. 18, Kelurahan Suka Maju, Kecamatan Medan Johor, Kota Medan
- Special note: fokus kamar mandi dan dapur

**Target:** READY.

### Case B — Data Belum Lengkap

> Kak, saya mau pesan deep cleaning untuk rumah besok. Kira-kira bisa datang?

Field yang belum tersedia antara lain:
- nama customer
- jumlah layanan
- jam pasti
- alamat
- metode layanan
- detail properti

**Target:** NEEDS CONFIRMATION.

### Case C — Chat Natural / Masih Samar

> Kak, kalau Sabtu pagi rumah saya dibersihin bisa nggak? Rumahnya dua lantai, lokasinya kurang lebih daerah Sunggal. Jamnya fleksibel aja, nanti saya kabarin lagi ya.

Pesan ini sengaja menggunakan gaya percakapan sehari-hari. Ada informasi yang cukup jelas, tetapi ada juga bagian yang belum dapat dipakai sebagai data operasional pasti:
- “Sabtu pagi” belum menjadi jam pasti;
- “kurang lebih daerah Sunggal” belum merupakan alamat lengkap;
- “jamnya fleksibel” menunjukkan waktu belum final;
- layanan disebut secara umum sebagai “dibersihin”, sehingga perlu dipastikan jenis layanan yang dipilih.

**Target:** NEEDS CONFIRMATION.

### Catatan Testing

Jika output AI berbeda dari target atau ada field yang salah diekstrak, hasil tersebut harus dicatat dan dijelaskan. Jangan mengganti hasil aktual hanya agar terlihat sempurna.
## Case B — Missing

**Chat**

> Kak mau deep cleaning rumah besok.

**Yang diharapkan untuk diuji**
- service: Deep Cleaning
- property_type: Rumah
- date: besok
- missing: jam, alamat, dan quantity jika tidak dianggap default oleh sistem
- status: **NEEDS CONFIRMATION**

**Hasil aktual setelah testing:** isi berdasarkan hasil aplikasi.

## Case C — Natural / Ambiguous

**Chat**

> Sore nanti bisa bersihin rumah? Sekitar 2 lantai dan alamatnya di Sunggal.

**Yang diharapkan untuk diuji**
- property_type: Rumah
- property_detail: 2 lantai
- address: Sunggal
- "sore" tidak boleh dipaksa menjadi jam tertentu
- layanan belum cukup spesifik
- status: **NEEDS CONFIRMATION**

**Hasil aktual setelah testing:** isi berdasarkan hasil aplikasi.

---

# Tabel Pencatatan Hasil Testing

| Case | Chat | Hasil AI | Status | Apa yang Dipelajari? |
|---|---|---|---|---|
| A | Complete | **Isi setelah testing** | **Isi setelah testing** | Apakah field lengkap terbaca? |
| B | Missing | **Isi setelah testing** | **Isi setelah testing** | Apakah missing field terdeteksi? |
| C | Natural/Ambiguous | **Isi setelah testing** | **Isi setelah testing** | Apakah AI membedakan data pasti dan ambigu? |

**Truth & Intellectual Honesty:** jika hasil AI salah atau berbeda dari dugaan, hasil tersebut harus dicatat dan dijelaskan. Jangan mengubah evidence agar terlihat sempurna.

---

# Checklist Submit

- [ ] Memahami alur starter project.
- [ ] Domain berbeda dari bakery.
- [ ] Problem bisnis jelas.
- [ ] User, Pain, Evidence, Impact tersedia.
- [ ] Problem Statement tersedia.
- [ ] HMW tersedia.
- [ ] Schema sesuai cleaning service.
- [ ] AI prompt sesuai cleaning service.
- [ ] Minimal 3 business rules yang benar-benar berbeda.
- [ ] Tiga chat diuji: Complete, Missing, Ambiguous.
- [ ] Ada screenshot READY.
- [ ] Ada screenshot NEEDS CONFIRMATION.
- [ ] Setiap anggota memahami perubahan.
- [ ] Tidak meng-upload `.env` atau API key.

---

# Demo 3–5 Menit

### 0:00–0:30 — Problem
Jelaskan:
- siapa user,
- pain,
- HMW.

### 0:30–1:30 — Code Change
Tunjukkan:
- `schemas.py`,
- `ai_service.py`,
- `business_rules.py`.

Fokus pada perubahan dari bakery menjadi cleaning service.

### 1:30–3:00 — Testing
Jalankan:
1. Case A → target READY.
2. Case B → target NEEDS CONFIRMATION.
3. Case C → target NEEDS CONFIRMATION karena informasi masih samar.

Tunjukkan field yang diekstrak dan missing field.

### 3:00–3:30 — Reflection
Jelaskan apa yang masih perlu diperbaiki atau dites.

---

# Refleksi Individu

Setiap anggota menyiapkan jawaban sendiri:

1. **Apa fungsi `app.py` menurut pemahaman Anda sendiri?**
2. **Apa perbedaan pekerjaan Gemini dengan `business_rules.py`?**
3. **Apa satu asumsi kelompok yang berubah setelah testing?**

Jawaban harus berdasarkan pemahaman dan hasil testing anggota, bukan copy-paste.
