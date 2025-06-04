from dependecies import *
from conf import *
from helper import *
from helper_pengaduan import *
from helper_ulasan import *

##################################################### ML predicted function
##############################################################################

def predict_ulasan():
    get_person_in_ulasan()
    get_place_in_ulasan()
    predict_topic_ulasan()
    transform_prediction_ulasan()

def predict_pengaduan():
    get_person_in_pengaduan()
    get_place_in_pengaduan()
    predict_topic_pengaduan()
    transform_prediction_pengaduan()

def get_person_in_ulasan():
    # Membaca file gmaps_review.xlsx dan persons.txt
    # reviews_file = dataset['file_ulasan']
    persons_file = dataset['daftar_person']
    output_file = dataset['results_persons_ulasan']
    
    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi huruf kecil
        text = text.lower()
        # Hapus tanda baca, tetapi pertahankan spasi
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Hapus spasi berlebihan
        text = re.sub(r"\s+", " ", text).strip()
        return text    
    def load_persons(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    # Fungsi untuk mengecek jumlah kemunculan setiap nama dalam ulasan
    def count_persons_in_review(review, persons):
        person_counts = []
        for person in persons:
            # Gunakan regex untuk mencocokkan nama dengan bentuk tersambung
            pattern = rf"\b{re.escape(person)}\w*\b"
            matches = re.findall(pattern, review, re.IGNORECASE)
            count = len(matches)
            if count > 0:  # Hanya tambahkan jika ditemukan
                person_counts.append((person, count))
        return person_counts

    # ambil data ulasan
    reviews_df = get_data_ulasan()
    reviews_df['snippet'] = reviews_df['snippet'].fillna("").astype(str).apply(clean_text)

    persons = [clean_text(person) for person in load_persons(persons_file)]
    print(f"Daftar persons: {persons}")

    # Proses ulasan untuk mencari person dan jumlahnya
    results = []
    for _, row in reviews_df.iterrows():
        thn = row['thn_ulasan']
        reviewer_id = row['reviewer_id']
        review_text = row['snippet']
        person_counts = count_persons_in_review(review_text, persons)
        
        for person, count in person_counts:
            results.append({
                "thn": thn,
                "reviewer_id": reviewer_id,
                "persons": person,
                "persons_count": count
            })

    # Simpan hasil ke file CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Hasil telah disimpan ke {output_file}")

def get_place_in_ulasan():
    # Membaca file gmaps_review.xlsx dan persons.txt
    # reviews_file = dataset['file_ulasan']
    places_file = dataset['daftar_place']
    output_file = dataset['results_places_ulasan']
    
    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi huruf kecil
        text = text.lower()
        # Hapus tanda baca, tetapi pertahankan spasi
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Hapus spasi berlebihan
        text = re.sub(r"\s+", " ", text).strip()
        return text    
    def load_places(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    # Fungsi untuk mengecek jumlah kemunculan setiap nama dalam ulasan
    def count_places_in_review(review, places):
        place_counts = []
        for place in places:
            # Gunakan regex untuk mencocokkan nama dengan bentuk tersambung
            pattern = rf"\b{re.escape(place)}\w*\b"
            matches = re.findall(pattern, review, re.IGNORECASE)
            count = len(matches)
            if count > 0:  # Hanya tambahkan jika ditemukan
                place_counts.append((place, count))
        return place_counts

    # ambil data ulasan
    reviews_df = get_data_ulasan()
    reviews_df['snippet'] = reviews_df['snippet'].fillna("").astype(str).apply(clean_text)
    

    places = [clean_text(place) for place in load_places(places_file)]
    print(f"Daftar places: {places}")

    # Proses ulasan untuk mencari person dan jumlahnya
    results = []
    for _, row in reviews_df.iterrows():
        thn = row['thn_ulasan']
        reviewer_id = row['reviewer_id']
        review_text = row['snippet']
        place_counts = count_places_in_review(review_text, places)
        
        for place, count in place_counts:
            results.append({
                "thn": thn,
                "reviewer_id": reviewer_id,
                "places": place,
                "places_count": count
            })

    # Simpan hasil ke file CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Hasil telah disimpan ke {output_file}")

def predict_topic_ulasan():
    # File paths
    # input_file = dataset['file_ulasan']
    training_file = dataset['data_training']
    cleaned_file = dataset['results_cleaned_ulasan']
    prediction_file = dataset['results_prediction_ulasan']
    grouped_file = dataset['results_group_prediction_ulasan']

    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi lowercase
        text = text.lower()
        # Hapus karakter tidak diinginkan
        text = re.sub(r'[^a-z0-9\s.]', '', text)
        # Ganti tanda baca berulang dengan satu saja
        text = re.sub(r'[!?.,]{2,}', lambda m: m.group(0)[0], text)
        return text

    # Baca file training data
    training_data = pd.read_excel(training_file)

    # Pastikan kolom 'topic', 'sentimen', dan 'text' ada
    if 'topic' in training_data.columns and 'sentimen' in training_data.columns and 'text' in training_data.columns:
        # Preprocessing Data
        X_topic = training_data['text']
        y_topic = training_data['topic']
        X_sentiment = training_data['text']
        y_sentiment = training_data['sentimen']
        
        x_jenis = training_data['text']
        y_jenis = training_data['jenis']

        # Latih Model Naive Bayes untuk Topic
        topic_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        topic_model.fit(X_topic, y_topic)

        # Latih Model Naive Bayes untuk Sentiment
        sentiment_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        sentiment_model.fit(X_sentiment, y_sentiment)

        # Latih Model Naive Bayes untuk Jenis
        jenis_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        jenis_model.fit(x_jenis, y_jenis)

        # Baca file gmaps_review.xlsx
        # df = pd.read_excel(input_file)
        df = get_data_ulasan()

        # Pastikan kolom yang akan digunakan ada
        if 'reviewer_id' in df.columns and 'fixed_review' in df.columns:
            # Membuat daftar untuk menyimpan hasil
            cleaned_data = []
            prediction_data = []

            # Memecah teks snippet berdasarkan titik dan membersihkan
            for _, row in df.iterrows():
                record_no = row['record_no']
                thn_ulasan = row['thn_ulasan']
                reviewer_id = row['reviewer_id']
                snippet = row['fixed_review']
                if isinstance(snippet, str):  # Pastikan snippet adalah string
                    snippet = clean_text(snippet)  # Bersihkan teks
                    sentences = snippet.split('.')  # Pecah berdasarkan titik
                    for sentence in sentences:
                        sentence = sentence.strip()  # Hilangkan spasi di awal/akhir kalimat
                        if sentence:  # Abaikan kalimat kosong
                            cleaned_data.append({'reviewer_id': reviewer_id, 'snippet_cleaned': sentence})
                            # Prediksi topic dan sentiment untuk setiap kalimat
                            predicted_topic = topic_model.predict([sentence])[0]
                            predicted_sentiment = sentiment_model.predict([sentence])[0]
                            predicted_jenis = jenis_model.predict([sentence])[0]
                            prediction_data.append({
                                'record_no': record_no,
                                'thn': thn_ulasan,
                                'reviewer_id': reviewer_id,
                                'sentence':sentence,
                                'predicted_jenis': predicted_jenis,
                                'predicted_topic': predicted_topic,
                                'predicted_sentiment': predicted_sentiment
                            })

            # Membuat DataFrame dari hasil pembersihan
            cleaned_df = pd.DataFrame(cleaned_data)
            prediction_df = pd.DataFrame(prediction_data)

            # Membuat DataFrame untuk hasil grup
            grouped_df = (
                prediction_df.groupby(['thn','record_no','reviewer_id', 'predicted_topic', 'predicted_sentiment'])
                .size()
                .reset_index(name='count')
            )

            # Simpan hasil ke file
            cleaned_df.to_csv(cleaned_file, index=False, encoding='utf-8')
            prediction_df.to_csv(prediction_file, index=False, encoding='utf-8')
            grouped_df.to_csv(grouped_file, index=False, encoding='utf-8')

            print(f"Hasil pembersihan disimpan ke {cleaned_file}")
            print(f"Hasil prediksi disimpan ke {prediction_file}")
            print(f"Hasil grup disimpan ke {grouped_file}")
        else:
            print("Kolom 'reviewer_id' atau 'snippet' tidak ditemukan dalam file gmaps_review.xlsx")
    else:
        print("Kolom 'topic', 'sentimen', atau 'text' tidak ditemukan dalam file training_data.xls")


def transform_prediction_ulasan():
    # Baca file input
    # input_file = 'dataset/cleaned_review_prediction_group.csv'
    input_file = dataset['results_group_prediction_ulasan']

    # output_file = 'dataset/transformed_review_prediction.csv'
    output_file = dataset['results_transformed_prediction_ulasan']

    # Load dataset
    df = pd.read_csv(input_file)

    # Hapus sentimen "biasa" jika ada sentimen "positif" atau "negatif" pada topik yang sama
    def remove_biasa(group):
        if 'biasa' in group['predicted_sentiment'].values:
            if 'positif' in group['predicted_sentiment'].values or 'negatif' in group['predicted_sentiment'].values:
                return group[group['predicted_sentiment'] != 'biasa']
        return group

    df = df.groupby(['reviewer_id', 'predicted_topic'], group_keys=False).apply(remove_biasa)

    # Kelompokkan data berdasarkan reviewer_id dan predicted_topic
    grouped = df.groupby(['reviewer_id', 'predicted_topic'])

    # List untuk menyimpan indeks baris yang akan dihapus
    rows_to_drop = []
    # List untuk menyimpan baris yang diperbarui
    updated_rows = []

    for (reviewer_id, topic), group in grouped:
        # Filter baris dengan predicted_sentiment "positif" dan "negatif"
        positif = group[group['predicted_sentiment'] == 'positif']
        negatif = group[group['predicted_sentiment'] == 'negatif']
        
        if not positif.empty and not negatif.empty:
            # Ambil nilai count
            count_positif = positif['count'].values[0]
            count_negatif = negatif['count'].values[0]
            
            if count_positif > count_negatif:
                # Pilih positif, update count
                updated_row = positif.iloc[0].copy()
                updated_row['count'] = count_positif - count_negatif
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)
            elif count_negatif > count_positif:
                # Pilih negatif, update count
                updated_row = negatif.iloc[0].copy()
                updated_row['count'] = count_negatif - count_positif
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)
            else:
                # Jika count sama, jadikan sentimen "biasa"
                updated_row = positif.iloc[0].copy()
                updated_row['predicted_sentiment'] = 'biasa'
                updated_row['count'] = count_positif  # Nilai count tetap sama
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)

    # Hapus baris yang terlibat konflik
    df.drop(rows_to_drop, inplace=True)

    # Tambahkan baris yang diperbarui ke dataframe
    df = pd.concat([df, pd.DataFrame(updated_rows)], ignore_index=True)

    # Simpan hasil ke file baru
    df.to_csv(output_file, index=False)
    print(f"Transformasi selesai. Data disimpan di: {output_file}")

#################################################################################################################################

def get_person_in_pengaduan():
    persons_file = dataset['daftar_person']
    output_file = dataset['results_persons_pengaduan']
    
    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi huruf kecil
        text = text.lower()
        # Hapus tanda baca, tetapi pertahankan spasi
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Hapus spasi berlebihan
        text = re.sub(r"\s+", " ", text).strip()
        return text    
    def load_persons(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    # Fungsi untuk mengecek jumlah kemunculan setiap nama dalam ulasan
    def count_persons_in_review(review, persons):
        person_counts = []
        for person in persons:
            # Gunakan regex untuk mencocokkan nama dengan bentuk tersambung
            pattern = rf"\b{re.escape(person)}\w*\b"
            matches = re.findall(pattern, review, re.IGNORECASE)
            count = len(matches)
            if count > 0:  # Hanya tambahkan jika ditemukan
                person_counts.append((person, count))
        return person_counts

    # ambil data pengaduan
    reviews_df = get_data_pengaduan()
    reviews_df['isi_pengaduan'] = reviews_df['isi_pengaduan'].fillna("").astype(str).apply(clean_text)

    persons = [clean_text(person) for person in load_persons(persons_file)]
    # print(f"Daftar persons: {persons}")

    # Proses ulasan untuk mencari person dan jumlahnya
    results = []
    for _, row in reviews_df.iterrows():
        thn = row['thn_pengaduan']
        pengaduan_id = row['pengaduan_id']
        review_text = row['isi_pengaduan']
        person_counts = count_persons_in_review(review_text, persons)
        
        for person, count in person_counts:
            results.append({
                "thn": thn,
                "pengaduan_id": pengaduan_id,
                "persons": person,
                "persons_count": count
            })

    # Simpan hasil ke file CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Hasil telah disimpan ke {output_file}")


def get_place_in_pengaduan():
    places_file = dataset['daftar_place']
    output_file = dataset['results_places_pengaduan']
    
    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi huruf kecil
        text = text.lower()
        # Hapus tanda baca, tetapi pertahankan spasi
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Hapus spasi berlebihan
        text = re.sub(r"\s+", " ", text).strip()
        return text    
    def load_places(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    # Fungsi untuk mengecek jumlah kemunculan setiap nama dalam ulasan
    def count_places_in_review(review, places):
        place_counts = []
        for place in places:
            # Gunakan regex untuk mencocokkan nama dengan bentuk tersambung
            pattern = rf"\b{re.escape(place)}\w*\b"
            matches = re.findall(pattern, review, re.IGNORECASE)
            count = len(matches)
            if count > 0:  # Hanya tambahkan jika ditemukan
                place_counts.append((place, count))
        return place_counts

    # ambil data pengaduan
    reviews_df = get_data_pengaduan()
    reviews_df['isi_pengaduan'] = reviews_df['isi_pengaduan'].fillna("").astype(str).apply(clean_text)

    places = [clean_text(place) for place in load_places(places_file)]
    # print(f"Daftar place: {places}")

    # Proses ulasan untuk mencari person dan jumlahnya
    results = []
    for _, row in reviews_df.iterrows():
        thn = row['thn_pengaduan']
        pengaduan_id = row['pengaduan_id']
        review_text = row['isi_pengaduan']
        place_counts = count_places_in_review(review_text, places)
        
        for place, count in place_counts:
            results.append({
                "thn": thn,
                "pengaduan_id": pengaduan_id,
                "places": place,
                "places_count": count
            })

    # Simpan hasil ke file CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Hasil telah disimpan ke {output_file}")

def predict_topic_pengaduan():
    # File paths
    input_file = dataset['file_pengaduan']
    training_file = dataset['data_training']
    cleaned_file = dataset['results_cleaned_pengaduan']
    prediction_file = dataset['results_prediction_pengaduan']
    grouped_file = dataset['results_group_prediction_pengaduan']

    # Fungsi untuk membersihkan teks
    def clean_text(text):
        # Ubah menjadi lowercase
        text = text.lower()
        # Hapus karakter tidak diinginkan
        text = re.sub(r'[^a-z0-9\s.]', '', text)
        # Ganti tanda baca berulang dengan satu saja
        text = re.sub(r'[!?.,]{2,}', lambda m: m.group(0)[0], text)
        return text

    # Baca file training data
    # training_data = pd.read_excel(training_file)
    training_data = pd.read_excel(training_file)

    # Pastikan kolom 'topic', 'sentimen', dan 'text' ada
    if 'topic' in training_data.columns and 'sentimen' in training_data.columns and 'text' in training_data.columns:
        # Preprocessing Data
        X_topic = training_data['text']
        y_topic = training_data['topic']
        X_sentiment = training_data['text']
        y_sentiment = training_data['sentimen']
        
        x_jenis = training_data['text']
        y_jenis = training_data['jenis']

        # Latih Model Naive Bayes untuk Topic
        topic_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        topic_model.fit(X_topic, y_topic)

        # Latih Model Naive Bayes untuk Sentiment
        sentiment_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        sentiment_model.fit(X_sentiment, y_sentiment)

        # Latih Model Naive Bayes untuk Jenis
        jenis_model = Pipeline([
            ('vectorizer', CountVectorizer()),  # Konversi teks menjadi fitur
            ('classifier', MultinomialNB())    # Model Naive Bayes
        ])
        jenis_model.fit(x_jenis, y_jenis)

        # Baca file pengaduan
        # df = pd.read_excel(input_file)
        df = get_data_pengaduan()

        # Pastikan kolom yang akan digunakan ada
        if 'pengaduan_id' in df.columns and 'fixed_pengaduan' in df.columns:
            # Membuat daftar untuk menyimpan hasil
            cleaned_data = []
            prediction_data = []

            # Memecah teks snippet berdasarkan titik dan membersihkan
            for _, row in df.iterrows():
                record_no = row['record_no']
                thn_pengaduan = row['thn_pengaduan']
                pengaduan_id = row['pengaduan_id']
                snippet = row['fixed_pengaduan']
                if isinstance(snippet, str):  # Pastikan snippet adalah string
                    snippet = clean_text(snippet)  # Bersihkan teks
                    sentences = snippet.split('.')  # Pecah berdasarkan titik
                    for sentence in sentences:
                        sentence = sentence.strip()  # Hilangkan spasi di awal/akhir kalimat
                        if sentence:  # Abaikan kalimat kosong
                            cleaned_data.append({'pengaduan_id': pengaduan_id, 'snippet_cleaned': sentence})
                            # Prediksi topic dan sentiment untuk setiap kalimat
                            predicted_topic = topic_model.predict([sentence])[0]
                            predicted_sentiment = sentiment_model.predict([sentence])[0]
                            predicted_jenis = jenis_model.predict([sentence])[0]
                            prediction_data.append({
                                'record_no': record_no,
                                'thn': thn_pengaduan,
                                'pengaduan_id': pengaduan_id,
                                'sentence':sentence,
                                'predicted_jenis': predicted_jenis,
                                'predicted_topic': predicted_topic,
                                'predicted_sentiment': predicted_sentiment
                            })

            # Membuat DataFrame dari hasil pembersihan
            cleaned_df = pd.DataFrame(cleaned_data)
            prediction_df = pd.DataFrame(prediction_data)

            # Membuat DataFrame untuk hasil grup
            grouped_df = (
                prediction_df.groupby(['thn','record_no','pengaduan_id', 'predicted_topic', 'predicted_sentiment'])
                .size()
                .reset_index(name='count')
            )

            # Simpan hasil ke file
            cleaned_df.to_csv(cleaned_file, index=False, encoding='utf-8')
            prediction_df.to_csv(prediction_file, index=False, encoding='utf-8')
            grouped_df.to_csv(grouped_file, index=False, encoding='utf-8')

            print(f"Hasil pembersihan disimpan ke {cleaned_file}")
            print(f"Hasil prediksi disimpan ke {prediction_file}")
            print(f"Hasil grup disimpan ke {grouped_file}")
        else:
            print("Kolom 'pengaduan_id' atau 'snippet' tidak ditemukan dalam file gmaps_review.xlsx")
    else:
        print("Kolom 'topic', 'sentimen', atau 'text' tidak ditemukan dalam file training_data.xls")

def transform_prediction_pengaduan():
    # Baca file input
    # input_file = 'dataset/cleaned_review_prediction_group.csv'
    input_file = dataset['results_group_prediction_pengaduan']

    # output_file = 'dataset/transformed_review_prediction.csv'
    output_file = dataset['results_transformed_prediction_pengaduan']

    # Load dataset
    df = pd.read_csv(input_file)

    # Hapus sentimen "biasa" jika ada sentimen "positif" atau "negatif" pada topik yang sama
    def remove_biasa(group):
        if 'biasa' in group['predicted_sentiment'].values:
            if 'positif' in group['predicted_sentiment'].values or 'negatif' in group['predicted_sentiment'].values:
                return group[group['predicted_sentiment'] != 'biasa']
        return group

    df = df.groupby(['pengaduan_id', 'predicted_topic'], group_keys=False).apply(remove_biasa)

    # Kelompokkan data berdasarkan reviewer_id dan predicted_topic
    grouped = df.groupby(['pengaduan_id', 'predicted_topic'])

    # List untuk menyimpan indeks baris yang akan dihapus
    rows_to_drop = []
    # List untuk menyimpan baris yang diperbarui
    updated_rows = []

    for (reviewer_id, topic), group in grouped:
        # Filter baris dengan predicted_sentiment "positif" dan "negatif"
        positif = group[group['predicted_sentiment'] == 'positif']
        negatif = group[group['predicted_sentiment'] == 'negatif']
        
        if not positif.empty and not negatif.empty:
            # Ambil nilai count
            count_positif = positif['count'].values[0]
            count_negatif = negatif['count'].values[0]
            
            if count_positif > count_negatif:
                # Pilih positif, update count
                updated_row = positif.iloc[0].copy()
                updated_row['count'] = count_positif - count_negatif
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)
            elif count_negatif > count_positif:
                # Pilih negatif, update count
                updated_row = negatif.iloc[0].copy()
                updated_row['count'] = count_negatif - count_positif
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)
            else:
                # Jika count sama, jadikan sentimen "biasa"
                updated_row = positif.iloc[0].copy()
                updated_row['predicted_sentiment'] = 'biasa'
                updated_row['count'] = count_positif  # Nilai count tetap sama
                updated_rows.append(updated_row)
                rows_to_drop.extend(positif.index)
                rows_to_drop.extend(negatif.index)

    # Hapus baris yang terlibat konflik
    df.drop(rows_to_drop, inplace=True)

    # Tambahkan baris yang diperbarui ke dataframe
    df = pd.concat([df, pd.DataFrame(updated_rows)], ignore_index=True)

    # Simpan hasil ke file baru
    df.to_csv(output_file, index=False)
    print(f"Transformasi selesai. Data disimpan di: {output_file}")