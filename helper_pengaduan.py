from dependecies import *
from conf import *


# buat engine db dari conf.py
# engine = create_engine_db()
#

# Fungsi untuk membaca data pengaduan
def get_data_pengaduan():
    # Membaca data menggunakan koneksi
    with engine.connect() as connection:
        query = text("SELECT * FROM pengaduan")
        df = pd.read_sql(query, connection)  
    # Ekstrak year
    df['thn_pengaduan'] = df['tgl_pengaduan'].dt.year
    # Ekstrak bulan
    df['bln'] = df['tgl_pengaduan'].dt.month
    df.sort_values(by="pengaduan_id", ascending=False, inplace=True)
    return df

def get_last_record_pengaduan():
    df = get_data_pengaduan()
    last_record = df['record_no'].max()
    return last_record

def get_data_pengaduan_detail():
    # Membaca data menggunakan koneksi
    with engine.connect() as connection:
        query = text("SELECT * FROM pengaduan_detail")
        df = pd.read_sql(query, connection)
    df.sort_values(by="record_no", ascending=True, inplace=True)
    return df

def load_and_group_data_pengaduan(thn='semua',topik='semua',status='semua'):
    # Baca tabel utama dan tambahan
    df1 = get_data_pengaduan()
    print (df1)
    if thn != 'semua':
        df1 = df1.query("thn_pengaduan == @thn")
    if status != 'semua':
        df1 = df1.query("status_pengaduan == @status")

    # Baca tabel transformed
    df2 = pd.read_csv(dataset['results_transformed_prediction_pengaduan'])
    if thn != 'semua':
        df2 = df2.query("thn == @thn")
    if topik != 'semua':
        df2 = df2.query("predicted_topic == @topik")
    
    persons_df = pd.read_csv(dataset['results_persons_pengaduan'])
    #print (persons_df)
    places_df = pd.read_csv(dataset['results_places_pengaduan'])    
    # Gabungkan data
    merged_data = df1.merge(df2, on=['record_no', 'pengaduan_id'], how='right')
    merged_data = merged_data.merge(persons_df, on='pengaduan_id', how='left')
    merged_data = merged_data.merge(places_df, on='pengaduan_id', how='left')
    
    # Filter snippet yang kosong
    merged_data = merged_data[merged_data['fixed_pengaduan'].notna() & (merged_data['fixed_pengaduan'] != '')]
    # Hapus duplikasi data berdasarkan semua kolom
    merged_data = merged_data.drop_duplicates()
    print(merged_data)    
    # Kelompokkan berdasarkan record_no dan reviewer_id
    grouped_data = []
    # Urutkan data berdasarkan record_no secara descending
    for (record_no, pengaduan_id), group in merged_data.groupby(['record_no', 'pengaduan_id']):
        main_data = {
            'record_no': record_no,
            'pengaduan_id': pengaduan_id,
            'nama': group.iloc[0]['nama'],
            'sumber': group.iloc[0]['sumber_pengaduan'],
            'fixed_pengaduan': group.iloc[0]['fixed_pengaduan'],
            'solusi_pengaduan': group.iloc[0]['solusi_pengaduan'],
            'status_pengaduan': group.iloc[0]['status_pengaduan'],
            'tgl_pengaduan': group.iloc[0]['tgl_pengaduan'],
            'thn_pengaduan': group.iloc[0]['thn_pengaduan']
        }
        # Data prediksi (hilangkan duplikasi)
        predicted_data = group[['predicted_topic', 'predicted_sentiment', 'count']].drop_duplicates().to_dict(orient='records')
        # Data persons (hilangkan duplikasi)
        persons_data = group[['persons', 'persons_count']].drop_duplicates().dropna().to_dict(orient='records')
        # Data places (hilangkan duplikasi)
        places_data = group[['places', 'places_count']].drop_duplicates().dropna().to_dict(orient='records')
        
        grouped_data.append({
            'main_data': main_data,
            'predicted_data': predicted_data,
            'persons_data': persons_data,
            'places_data': places_data,
        })
    # (Opsional) Urutkan grouped_data berdasarkan record_no
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    # Debug: Cek urutan setelah grouped_data dibuat
    # print("Grouped data record_no (desc):", [item['main_data']['record_no'] for item in grouped_data])    
    return grouped_data

# fungsi hapus pengaduan
# data pada tabel pengaduan_detail juga akan dihapus
def delete_row_pengaduan(pengaduan_id):
    try:
        # print("Menghapus ID:", pengaduan_id)
        # Query untuk menghapus data
        query = text("DELETE FROM pengaduan WHERE pengaduan_id = :pengaduan_id")
        query_detail = text("DELETE FROM pengaduan_detail WHERE pengaduan_id = :pengaduan_id")

        # Menggunakan transaksi eksplisit
        with engine.connect() as connection:
            with connection.begin():  # Memulai transaksi
                result = connection.execute(query, {"pengaduan_id": pengaduan_id})
                result2 = connection.execute(query_detail, {"pengaduan_id": pengaduan_id}
                                            )
                # Periksa apakah ada baris yang dihapus
                if result.rowcount == 0:
                    return jsonify({"error": f"Pengaduan dengan ID {pengaduan_id} tidak ditemukan"}), 404

                print(f"Pengaduan dengan ID {pengaduan_id} berhasil dihapus.")
                return jsonify({"success": True, "message": f"Pengaduan dengan ID {pengaduan_id} berhasil dihapus"}), 200

    except SQLAlchemyError as e:
        print("Error:", str(e))
        return jsonify({"error": "Terjadi kesalahan saat menghapus data pengaduan"}), 500