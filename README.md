# AI-for-Business-Syafira-Ishmal-
1. Business Problem Canvas
Menjelaskan 4 latar belakang masalah bisnis cleaning service:  
PDF
User: Admin operasional / pemilik usaha Cleaning Service.  
PDF
Pain: Admin membuang banyak waktu untuk chat berulang karena customer tidak memberikan detail pembersihan (seperti alamat, jumlah lantai, atau jam pembersihan).  
PDF
Evidence: Bukti nyata berupa obrolan customer yang sangat singkat, contohnya: "Mbak, mau pesan cleaning buat besok ya" (tanpa menyebut alamat dan tipe rumah).  
PDF
Impact: Penjadwalan tim kebersihan berantakan, tim membawa peralatan yang salah ke lokasi, dan terjadi pembatalan pesanan di hari-H.  
PDF

2. Problem Statement & How Might We (HMW)
Dua kalimat rumusan masalah final:  
PDF
Problem Statement:
Admin cleaning service membutuhkan cara untuk mengekstrak dan memverifikasi kelengkapan data pemesanan dari chat customer secara otomatis karena informasi spesifikasi properti dan jadwal sering tidak lengkap, sehingga penjadwalan tim cleaner terlambat dan sering terjadi kesalahan estimasi biaya.  
PDF

How Might We (HMW):
Bagaimana kita dapat membantu admin cleaning service memastikan spesifikasi properti dan alamat pembersihan lengkap sebelum order dijadwalkan?  
PDF
4. Tabel 3 Test Case (Hasil Pengujian Chat)
Tabel bukti bahwa program kalian sudah diuji dengan 3 variasi chat customer:  
PDF
Case	Jenis Chat	Contoh Chat Input	Status Hasil	Penjelasan
A	Lengkap	"Halo kak, saya Budi. Mau Deep Cleaning 2 Lantai untuk Sabtu 19 September jam 10 pagi di Jalan Cemara No. 12 Medan."	READY	
Data lengkap (nama, layanan, jadwal, lokasi ada), aturan bisnis meloloskan.  
PDF

B	Data Kurang	"Kak, mau minta tolong bersihkan rumah besok ya."	NEEDS CONFIRMATION	
Alamat, jam, dan jumlah lantai kosong. Sistem mendeteksi data kurang (missing fields).  
PDF

C	Ambigu	"Sore kak, rumah kotor banget habis renovasi 2 lantai. Bisa bersihkan sore nanti atau besok di Sunggal?"	NEEDS CONFIRMATION	
Pilihan waktu ambigu/membingungkan, sistem meminta konfirmasi jam pasti.
