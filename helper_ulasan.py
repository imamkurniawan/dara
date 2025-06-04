from dependecies import *
from conf import *

##################################

# buat engine db dari conf.py
# engine = create_engine_db()

# Fungsi untuk membaca data ulasan
def get_data_ulasan():
    
    # Baca tabel MySQL
    # Membaca data menggunakan koneksi
    with engine.connect() as connection:
        query = text("SELECT * FROM ulasan")
        df = pd.read_sql(query, connection)

    # Pilih kolom yang ingin ditampilkan
    # selected_columns = ["record_no","reviewer_id","name","link","thumbnail","reviews","photos","localGuide","rating","duration", "tgl_ulasan", "snippet", "fixed_review", "likes", "thn_ulasan"]  # Ganti dengan nama kolom yang ingin ditampilkan
    # df = df[selected_columns]

    # Konversi dengan format yang benar
    df['tgl_ulasan'] = pd.to_datetime(df['tgl_ulasan'], dayfirst=True)
    # Ekstrak year
    # df['thn'] = df['tgl_ulasan'].dt.year
    df.sort_values(by="record_no", ascending=False, inplace=True)
    return df

def get_last_record():
    df = get_data_ulasan()
    last_record = df['record_no'].max()
    return last_record

def calculate_review_stats(df):
    total_reviews = len(df)
    average_rating = df['rating'].mean()
    average_rating = round(average_rating,2)
    return total_reviews, average_rating

def get_ratings_per_year_and_value(df):
    ratings_per_year_value = df.groupby(['thn', 'rating']).size().reset_index(name='count')
    pivot_table = ratings_per_year_value.pivot(index='thn', columns='rating', values='count').fillna(0)
    return pivot_table

def get_total_ulasan_tahunan():
    df = get_data_ulasan()
    # Group by berdasarkan tahun dan hitung jumlah record
    result = df.groupby('thn').size().reset_index(name='jumlah_records')
    return result

def get_total_rating():
    df = get_data_ulasan()
    # Group by berdasarkan tahun dan hitung jumlah record
    result = df.groupby('rating').size().reset_index(name='jumlah_records')
    return result

def calculate_sentiment():
    # ambil file transformed prediction
    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    total_sentimen = len(df)
    df_positif = df.query("predicted_sentiment == 'positif'")
    total_positif = len(df_positif)
    persen_positif = int(round((total_positif/total_sentimen)*100,0))
    df_negatif = df.query("predicted_sentiment == 'negatif'")
    total_negatif = len(df_negatif)
    persen_negatif = int(round((total_negatif/total_sentimen)*100,0))
    df_biasa = df.query("predicted_sentiment == 'biasa'")
    total_biasa = len(df_biasa)
    persen_biasa = int(round((total_biasa/total_sentimen)*100,0))
    data = {
        'total_sentimen':total_sentimen,
        'total_positif':total_positif,
        'total_negatif':total_negatif,
        'total_biasa':total_biasa,
        'persen_positif':persen_positif,
        'persen_negatif':persen_negatif,
        'persen_biasa':persen_biasa
    }
    return(data)


def load_and_group_data(thn='semua',topik='semua',sentimen='semua'):
    # Baca tabel utama dan tambahan
    df1 = get_data_ulasan()
    if thn != 'semua':
        df1 = df1.query("thn_ulasan == @thn")

    # Baca tabel transformed
    df2 = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    if thn != 'semua':
        df2 = df2.query("thn == @thn")
    if topik != 'semua':
        df2 = df2.query("predicted_topic == @topik")
    if sentimen != 'semua':
        df2 = df2.query("predicted_sentiment == @sentimen")
    
    persons_df = pd.read_csv(dataset['results_persons_ulasan'])
    places_df = pd.read_csv(dataset['results_places_ulasan'])    
    
    # Gabungkan data
    merged_data = df1.merge(df2, on=['record_no', 'reviewer_id'], how='right')
    merged_data = merged_data.merge(persons_df, on='reviewer_id', how='left')
    merged_data = merged_data.merge(places_df, on='reviewer_id', how='left')
    print(merged_data)
    # Filter snippet yang kosong
    merged_data = merged_data[merged_data['snippet'].notna() & (merged_data['snippet'] != '')]
    # Hapus duplikasi data berdasarkan semua kolom
    merged_data = merged_data.drop_duplicates()    
    # Kelompokkan berdasarkan record_no dan reviewer_id
    grouped_data = []
    # Urutkan data berdasarkan record_no secara descending
    for (record_no, reviewer_id), group in merged_data.groupby(['record_no', 'reviewer_id']):
        main_data = {
            'record_no': record_no,
            'reviewer_id': reviewer_id,
            'name': group.iloc[0]['name'],
            'link': group.iloc[0]['link'],
            'localGuide': group.iloc[0]['localGuide'],
            'rating': group.iloc[0]['rating'],
            'snippet': group.iloc[0]['snippet'],
            'fixed_review': group.iloc[0]['fixed_review'],
            'likes': group.iloc[0]['likes'],
            'tgl_ulasan': group.iloc[0]['tgl_ulasan'],
            'thn_ulasan': group.iloc[0]['thn_ulasan']
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
            'places_data': places_data
        })
    # (Opsional) Urutkan grouped_data berdasarkan record_no
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    # Debug: Cek urutan setelah grouped_data dibuat
    # print("Grouped data record_no (desc):", [item['main_data']['record_no'] for item in grouped_data])    
    return grouped_data