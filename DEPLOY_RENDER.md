# 🚀 Panduan Deploy FastAPI Ke Render.com

Dokumen ini berisi panduan lengkap untuk melakukan deploy aplikasi backend **Talangraga Umroh** (FastAPI + PostgreSQL + Alembic) ke platform [Render.com](https://render.com). 

Kami telah memperbarui konfigurasi proyek agar **100% Cloud-Ready**:
1. **`app/core/config.py`**: Ditambahkan validator otomatis untuk mengonversi URL PostgreSQL (`postgresql://` menjadi `postgresql+psycopg2://`) agar kompatibel dengan driver database SQLAlchemy & psycopg2.
2. **`alembic/env.py`**: Diperbarui agar secara dinamis menggunakan variabel lingkungan `DATABASE_URL` untuk menjalankan migrasi database otomatis di production.
3. **`render.yaml`**: Dibuat file Render Blueprint untuk deployment otomatis satu klik (1-Click Deployment) yang otomatis membuatkan PostgreSQL Database dan menghubungkannya dengan Web Service FastAPI Anda.

---

## 🛠️ Persiapan Awal
Sebelum melakukan deploy, pastikan:
1. Kode Anda sudah dipush ke repository Git online (**GitHub** atau **GitLab**).
2. Anda telah memiliki akun di [Render.com](https://render.com).
3. Anda memiliki akun [Cloudinary](https://cloudinary.com) untuk penyimpanan file/gambar media.

---

## ⚡ Metode A: Menggunakan Render Blueprint (Sangat Direkomendasikan - 1-Click Deployment)
Render Blueprint menggunakan file `render.yaml` yang sudah kami buat untuk otomatis membuat database PostgreSQL dan Web Service FastAPI secara bersamaan.

### Langkah-langkah:
1. **Push Perubahan**: Pastikan file `render.yaml` baru sudah ter-push ke repository GitHub Anda.
2. **Hubungkan ke Render**:
   - Masuk ke dashboard [Render.com](https://dashboard.render.com).
   - Klik tombol **New +** di kanan atas dan pilih **Blueprint**.
3. **Pilih Repository**:
   - Hubungkan akun GitHub Anda jika belum, lalu cari dan pilih repository `talangraga-umroh-fastapi`.
4. **Konfigurasi Blueprint**:
   - Berikan nama grup (misalnya: `talangraga-umroh`).
   - Render akan mendeteksi file `render.yaml` secara otomatis.
   - Anda akan diminta mengisi beberapa parameter yang kosong/tidak aman untuk disinkronkan langsung (seperti kredensial Cloudinary).
5. **Isi Environment Variables**:
   Isi nilai variabel berikut di bagian konfigurasi halaman:
   - `CLOUDINARY_CLOUD_NAME`: *[Cloud Name Anda]*
   - `CLOUDINARY_API_KEY`: *[API Key Anda]*
   - `CLOUDINARY_API_SECRET`: *[API Secret Anda]*
6. **Deploy**:
   - Klik **Apply**.
   - Render akan otomatis membuat database PostgreSQL terlebih dahulu (`talangraga-db`), lalu membuat Web Service FastAPI (`talangraga-backend`), dan menghubungkan keduanya secara otomatis!

---

## 📝 Metode B: Deployment Manual (Langkah-demi-Langkah)
Jika Anda tidak ingin menggunakan Blueprint, Anda dapat membuat layanannya satu per satu secara manual.

### Langkah 1: Buat PostgreSQL Database di Render
1. Masuk ke dashboard Render, klik **New +** -> **PostgreSQL**.
2. Konfigurasikan database Anda:
   - **Name**: `talangraga-db`
   - **Database**: `talangraga`
   - **User**: `postgres`
   - **Region**: Pilih yang terdekat dengan pengguna Anda (misalnya `Singapore` / `ap-southeast`).
   - **Plan**: `Free` (atau sesuai kebutuhan).
3. Klik **Create Database**.
4. Setelah database aktif, salin **Internal Database URL** (digunakan untuk koneksi antar-layanan Render). Contoh formatnya: `postgresql://postgres:password@dpg-xxxxxx-a.singapore-postgres.render.com/talangraga`.

### Langkah 2: Buat Web Service untuk FastAPI
1. Di dashboard Render, klik **New +** -> **Web Service**.
2. Pilih repository GitHub `talangraga-umroh-fastapi`.
3. Konfigurasikan Web Service:
   - **Name**: `talangraga-backend`
   - **Region**: Pilih region yang sama dengan database (misalnya `Singapore`).
   - **Branch**: `main` (atau branch utama Anda).
   - **Runtime**: **Docker** 👈 *(Sangat penting! Render akan otomatis menggunakan `Dockerfile` multi-stage yang sudah ada)*.
   - **Plan**: `Free` (atau sesuai kebutuhan).

### Langkah 3: Tambahkan Environment Variables (Manual)
Masuk ke tab **Environment** pada Web Service Anda, lalu tambahkan variabel-variabel berikut:

| Key | Value (Rekomendasi Production) | Deskripsi |
| :--- | :--- | :--- |
| `ENV` | `production` | Mengubah mode aplikasi menjadi Production |
| `APP_NAME` | `Talangraga Umroh Backend` | Nama aplikasi Anda |
| `API_PREFIX` | `/api` | Prefiks routing API |
| `DATABASE_URL` | *[Internal Database URL dari Langkah 1]* | URL koneksi ke PostgreSQL Render |
| `SECRET_KEY` | *[Hasil generate random string]* | Token JWT Secret Key (lihat tips di bawah) |
| `REFRESH_SECRET_KEY` | *[Hasil generate random string]* | Token JWT Refresh Secret Key |
| `ALGORITHM` | `HS256` | Algoritma enkripsi JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Masa berlaku Token Akses (1 minggu) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Masa berlaku Refresh Token |
| `CLOUDINARY_CLOUD_NAME` | *[Cloud Name Cloudinary Anda]* | Akun Cloudinary |
| `CLOUDINARY_API_KEY` | *[API Key Cloudinary Anda]* | Kredensial Cloudinary |
| `CLOUDINARY_API_SECRET` | *[API Secret Cloudinary Anda]* | Kredensial Cloudinary |

> 💡 **Tips Menghasilkan SECRET_KEY Baru secara Aman**:
> Jalankan perintah berikut di terminal lokal Anda untuk membuat string acak 32-karakter heksadesimal yang aman:
> ```bash
> openssl rand -hex 32
> ```

---

## 🔄 Bagaimana Database Migration Berjalan?
Anda **tidak perlu menjalankan migrasi database secara manual** di Render!
Berkat file `Dockerfile` dan `docker-entrypoint.sh` Anda yang sudah dikonfigurasi:
```bash
# Isi docker-entrypoint.sh
alembic upgrade head
exec "$@"
```
Setiap kali Render melakukan build dan start kontainer Docker Anda:
1. `docker-entrypoint.sh` akan dijalankan terlebih dahulu.
2. Perintah `alembic upgrade head` akan dieksekusi secara otomatis untuk memeriksa dan menerapkan migrasi database terbaru ke PostgreSQL Render Anda.
3. Setelah migrasi sukses, FastAPI (`uvicorn`) akan dijalankan.

---

## 🔍 Verifikasi Setelah Deploy
1. **Cek Build Logs**: Di halaman Web Service Anda di Render, periksa tab **Events** dan **Logs**. Pastikan proses build Docker sukses dan logs menampilkan:
   ```text
   INFO  [alembic.runtime.migration] Running upgrade -> xxxxxxxx, migration_name
   ...
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```
2. **Uji API**: Akses URL aplikasi Render Anda di browser (misalnya: `https://talangraga-backend.onrender.com/docs` atau `https://talangraga-backend.onrender.com/api/docs`).
3. **Cek Koneksi Database**: Coba gunakan endpoint `/api/auth/register` atau `/api/auth/login` untuk memastikan API dapat menulis dan membaca data dari PostgreSQL secara lancar.

---

## ⚠️ Catatan Penting untuk Layanan Free Tier di Render.com
* **Cold Start**: Pada free tier, jika tidak ada request masuk dalam waktu 15 menit, kontainer aplikasi Anda akan masuk ke mode "tidur" (*spin down*). Request berikutnya akan memicu *spin up* (cold start) yang memakan waktu 30-50 detik sebelum API merespons kembali.
* **Database Free Tier**: Database PostgreSQL pada Free Tier Render akan otomatis terhapus atau non-aktif setelah **90 hari**. Untuk kebutuhan production jangka panjang, disarankan untuk upgrade ke database berbayar (mulai dari $7/month).
