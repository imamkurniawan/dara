import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Data asli yang Anda berikan
data_asli = [
    # Data asli Anda di sini (dari record_no 1 sampai 26)
    # ... (saya tidak menulis ulang semua data asli untuk menghemat ruang)
]

# Fungsi untuk membuat data dummy
def generate_dummy_data(start_id, year, count):
    dummy_data = []
    sources = ['Website', 'Whatsapp', 'Instagram', 'Form Pengaduan', 'Langsung', 'BPJS', 'Facebook', 'Tiktok']
    statuses = ['selesai', 'proses']
    addresses = ['Mataram', 'Ampenan', 'Pagesangan', 'Sekarbela', 'Dasan Agung Baru', 'Puncang Sandik', 'Gomong', 'Banjar Mantri']
    
    for i in range(count):
        record_no = start_id + i
        date = datetime(year, random.randint(1, 12), random.randint(1, 28))
        tgl_pengaduan = date.strftime('%Y-%m-%d 00:00:00')
        nama = random.choice(['Budi Santoso', 'Siti Rahma', 'Ahmad Fauzi', 'Dian Sastro', 'Rina Wijaya', 'Fajar Siddiq', 'Anonim', '-'])
        sumber = random.choice(sources)
        
        # Generate berbagai jenis keluhan
        complaints = [
            f"Pendaftaran online error ketika upload dokumen",
            f"Ruang tunggu poli {random.choice(['anak', 'penyakit dalam', 'bedah'])} sangat {random.choice(['panas', 'kotor', 'berisik'])}",
            f"Dokter spesialis {random.choice(['jantung', 'kulit', 'anak'])} sering datang terlambat",
            f"Obat yang diresepkan tidak tersedia di apotek RS",
            f"Perawat di {random.choice(['IGD', 'ruang perawatan', 'poli'])} kurang ramah",
            f"Toilet di lantai {random.randint(1, 5)} sangat kotor dan bau",
            f"Sistem antrian online tidak akurat",
            f"Parkir {random.choice(['motor', 'mobil'])} terlalu sempit dan berbahaya",
            f"AC di ruang tunggu {random.choice(['poli', 'IGD', 'administrasi'])} tidak bekerja",
            f"Petugas loket sangat lambat melayani"
        ]
        
        isi_pengaduan = random.choice(complaints)
        fixed_pengaduan = isi_pengaduan  # Untuk sederhananya kita samakan
        status = random.choice(statuses)
        
        if status == 'selesai':
            solutions = [
                "Sudah diberikan penjelasan dan solusi kepada pasien",
                "Telah dilakukan perbaikan terhadap masalah yang dilaporkan",
                "Telah dilakukan koordinasi dengan unit terkait",
                "Sudah diberikan edukasi kepada pasien terkait prosedur"
            ]
            solusi_pengaduan = random.choice(solutions)
        else:
            solusi_pengaduan = ""
        
        data = {
            'record_no': record_no,
            'reviewer_id': f'={year}*10000+{record_no}',
            'tgl_pengaduan': tgl_pengaduan,
            'tgl_proses': '',
            'tgl_selesai': '',
            'nama': nama,
            'telepon': f'08{random.randint(100000000, 999999999)}' if random.random() > 0.3 else '',
            'alamat': random.choice(addresses) if random.random() > 0.3 else '',
            'sumber': sumber,
            'isi_pengaduan': isi_pengaduan,
            'fixed_pengaduan': fixed_pengaduan,
            'solusi_pengaduan': solusi_pengaduan,
            'status_pengaduan': status
        }
        
        dummy_data.append(data)
    
    return dummy_data

# Generate data dummy
dummy_2020 = generate_dummy_data(27, 2020, 15)
dummy_2021 = generate_dummy_data(42, 2021, 15)
dummy_2022 = generate_dummy_data(57, 2022, 15)
dummy_2023 = generate_dummy_data(72, 2023, 14)  # Karena sudah ada 2 data di 2023
dummy_2025 = generate_dummy_data(86, 2025, 15)

# Gabungkan semua data
all_data = data_asli + dummy_2020 + dummy_2021 + dummy_2022 + dummy_2023 + dummy_2025

# Buat DataFrame
df = pd.DataFrame(all_data)

# Simpan ke Excel
df.to_excel('pengaduan_lengkap.xlsx', index=False)

print("File pengaduan_lengkap.xlsx berhasil dibuat dengan 100 data")