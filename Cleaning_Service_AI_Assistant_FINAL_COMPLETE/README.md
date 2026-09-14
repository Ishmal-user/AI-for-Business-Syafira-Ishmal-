# 🧹 AI Smart Cleaning Service Assistant — Assignment Remix

Project ini adalah adaptasi dari starter project **AI Business Assistant** ke konteks
**Cleaning Service**, mengikuti Panduan Tugas AI for Business Pertemuan 3.

Panduan dosen menekankan:
- pahami alur starter,
- pilih bisnis lain,
- definisikan problem,
- ubah hanya bagian penting,
- uji 3 chat: Complete, Missing, Ambiguous,
- tunjukkan minimal satu READY dan satu NEEDS CONFIRMATION.

## 1. Alur Sistem

```text
Customer Chat
    ↓
app.py
    ↓
Gemini AI / ai_service.py
    ↓
Structured Order / schemas.py
    ↓
Business Rules / business_rules.py
    ↓
WhatsApp Draft
    ↓
Order Dashboard
```

Prinsip utama:

> **AI understands. The system controls.**

AI memahami bahasa natural. Python menjaga keputusan yang harus konsisten seperti
harga, validasi field wajib, dan status order.

## 2. Struktur File

```text
cleaning_service_project/
├── app.py
├── ai_service.py
├── schemas.py
├── business_rules.py
├── business_case.md
├── sample_messages.csv
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### `app.py`
Wajah aplikasi:
- menerima chat,
- tombol Analyze,
- menampilkan hasil,
- draft WhatsApp,
- Save to Order Dashboard,
- dashboard,
- AI vs Business Rules.

### `ai_service.py`
Jembatan ke Gemini:
- membuat prompt,
- mengirim chat,
- meminta structured JSON,
- memvalidasi hasil dengan Pydantic.

### `schemas.py`
Format data yang harus diisi AI:
- customer,
- service,
- quantity,
- date,
- time,
- property type,
- property detail,
- address,
- missing fields,
- risk flags.

### `business_rules.py`
Aturan yang harus konsisten:
- service harus valid,
- quantity harus ada,
- tanggal dan jam harus cukup pasti,
- property type harus valid,
- onsite harus punya alamat,
- harga dan total dihitung Python,
- status READY / NEEDS CONFIRMATION.

### `.env`
Tempat API key dan nama model. **Jangan upload ke GitHub.**

## 3. Setup macOS

Di Terminal VS Code:

```bash
cd /path/ke/cleaning_service_project
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Buat file `.env` dari `.env.example`:

```env
GEMINI_API_KEY=API_KEY_BARU_KAMU
GEMINI_MODEL=gemini-3.6-flash
```

Jalankan:

```bash
streamlit run app.py
```

Buka:

```text
http://localhost:8501
```

## 4. Mengapa Gemini 3.6 Flash?

Versi project ini menggunakan **Gemini 3.6 Flash melalui Interactions API** dan
structured JSON output. Ini dipilih karena konfigurasi Gemini pada akun yang
digunakan sebelumnya menolak `gemini-2.5-flash`.

Jika muncul error model:
1. pastikan `.env` menggunakan model yang tersedia pada API project,
2. pastikan package diperbarui:
   ```bash
   python3 -m pip install -r requirements.txt --upgrade
   ```
3. restart Streamlit.

## 5. Tiga Test Case Tugas

### A — Complete

```text
Selamat siang Kak, saya Andi. Saya ingin pesan Deep Cleaning sebanyak 1 layanan
untuk rumah 2 lantai. Mohon tim datang langsung (onsite) pada Sabtu, 19 September
2026 pukul 09:00. Alamat lengkapnya Jl. Melati No. 18, Kelurahan Suka Maju,
Kecamatan Medan Johor, Kota Medan. Catatan: tolong fokuskan pembersihan pada
kamar mandi dan dapur.
```

Target: **READY**.

### B — Missing

```text
Kak, saya mau pesan deep cleaning untuk rumah besok. Kira-kira bisa datang?
```

Target: **NEEDS CONFIRMATION**.

### C — Natural / Ambiguous

```text
Kak, kalau Sabtu pagi rumah saya dibersihin bisa nggak? Rumahnya dua lantai,
lokasinya kurang lebih daerah Sunggal. Jamnya fleksibel aja, nanti saya kabarin lagi ya.
```

Target: **NEEDS CONFIRMATION**.

Catat hasil aktual setelah testing. Jangan mengarang hasil yang belum diuji.

## 6. Minimal Business Rules

1. Service harus cocok dengan katalog dan quantity harus jelas.
2. Onsite wajib memiliki alamat.
3. Tipe properti wajib valid.
4. Tanggal dan jam harus cukup pasti; "pagi/sore" tanpa jam tidak dianggap lengkap.
5. Harga/subtotal/total dihitung Python dari catalog, bukan Gemini.

## 7. Screenshot yang Harus Diambil

Setelah aplikasi berjalan, ambil minimal:
- screenshot Case A yang menunjukkan **READY**, 
- screenshot Case B atau C yang menunjukkan **NEEDS CONFIRMATION**.

Screenshot ini merupakan evidence testing untuk submission.

## 8. Demo 3–5 Menit

- 30 detik: user + pain + HMW.
- 60 detik: bagian code yang diubah.
- 90 detik: Case A READY + Case B/C NEEDS CONFIRMATION.
- 30 detik: apa yang masih perlu diperbaiki/dites.

## 9. Keamanan

Jangan:
- memasukkan API key langsung ke source code,
- meng-upload `.env`,
- meng-commit API key ke GitHub.

Gunakan `.env` lokal dan file `.gitignore`.

## 10. Catatan Akademik

Ini adalah demo pembelajaran. Dashboard menggunakan Streamlit session state,
bukan ERP/database produksi. Fokus tugas adalah memahami problem bisnis,
adaptasi schema/prompt/rules, dan testing.


## ⚡ Optimasi Kecepatan

Project ini sudah dioptimalkan untuk demo kelas:
- Gemini client di-reuse sehingga tidak dibuat ulang pada setiap rerun Streamlit.
- Hasil request yang identik di-cache. Jika Case A/B/C dijalankan ulang dengan chat,
  model, tanggal referensi, dan API key yang sama, hasil dapat tampil tanpa request
  Gemini kedua.
- Prompt dibuat lebih ringkas agar input ke model lebih kecil.
- Tombol **Clear AI Cache** tersedia di sidebar jika ingin menguji ulang dari awal.

Catatan: request Gemini pertama tetap membutuhkan waktu jaringan/API. Optimasi ini
terutama mempercepat rerun dan pengujian case yang sama, tanpa menghilangkan peran
Gemini dalam assignment.


### 🛡️ Ekstraksi eksplisit sebagai safety net

Setelah Gemini mengembalikan structured output, project memiliki normalisasi kecil
untuk literal yang benar-benar tertulis di chat, misalnya nama layanan katalog,
"sebanyak 1 layanan", "2 lantai", "onsite", dan alamat setelah "Alamat lengkapnya".
Tujuannya bukan menggantikan Gemini, tetapi mencegah informasi yang sangat jelas
hilang sebelum masuk ke business rules. Harga dan status tetap ditentukan Python.


## Final validation for pricing

Harga satuan selalu diambil dari `SERVICE_CATALOG` di Python. Quantity hanya
boleh berasal dari angka yang benar-benar tertulis pada chat dan dibatasi pada
1–100. Dengan demikian angka yang salah dari output model tidak dapat berubah
menjadi subtotal yang tidak masuk akal. Status `READY` tetap ditentukan oleh
Business Rules.
