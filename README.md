# Monitoring hotspot areal perusahaan (GitHub Pages)

## Setup
1. Buat repository **public** baru di GitHub, misalnya `monitor-hotspot`.
2. Upload semua isi paket ini ke **root** repository, termasuk folder `.github/workflows`.
3. Buka **Settings > Pages > Build and deployment** lalu pilih **Deploy from a branch**, `main`, `/ (root)` dan Save.
4. Daftar akun NASA Earthdata dan dapatkan **FIRMS MAP_KEY** melalui https://firms.modaps.eosdis.nasa.gov/api/ .
5. Buka **Settings > Secrets and variables > Actions > New repository secret**, beri nama `FIRMS_MAP_KEY`, isi kunci FIRMS Anda. Jangan masukkan kunci ke HTML atau file publik.
6. Buka **Actions > Update NASA FIRMS hotspots > Run workflow**. Setelah sukses, `hotspots.json` akan diperbarui dan halaman akan menampilkan data terbaru.
7. Alamat halaman: `https://USERNAME.github.io/monitor-hotspot/` (ganti USERNAME dengan akun Anda).

Workflow terjadwal tiap 2 jam, bergantung ketersediaan GitHub Actions dan pembaruan data NASA. Untuk repository publik, perhatikan batas penggunaan layanan gratis dan ketentuan API. Workflow mungkin perlu izin write di Settings > Actions > General > Workflow permissions. Jika gagal push, aktifkan **Read and write permissions**. Jadwal Actions tidak dijamin berjalan tepat waktu dan dapat dinonaktifkan pada repository tidak aktif.

## Data SHP
`BATAS_BLOK.shp` (55 fitur) dipakai untuk membuat batas gabungan `areal.geojson`, sedangkan `PETAK_ID.shp` (1039 fitur) untuk lapisan petak. Data asli SHP tidak perlu diunggah ke repository karena GeoJSON sudah tersedia.

## Keterangan
Hotspot adalah deteksi anomali panas oleh satelit, bukan kepastian kebakaran. Buffer menggunakan jarak dari polygon dan titik pada peta. Koordinat disajikan dalam WGS84. Peta memerlukan koneksi internet ke penyedia tiles dan CDN. GitHub Pages hanya menampilkan data, pengambilan FIRMS dijalankan oleh GitHub Actions.
