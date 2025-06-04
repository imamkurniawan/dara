from dependecies import *
from conf import *
from helper import *
from helper_ulasan import *
from helper_pengaduan import *
from helper_ml import *

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Untuk keperluan flash message

# Registrasi helper filter humanize_date ke Jinja
app.jinja_env.filters['humanize_date'] = humanize_date

# Registrasi helper filter highlight_replace ke jinja
app.jinja_env.filters['highlight_replace'] = highlight_replace

# ambil tahun dan bulan sekarang
current_date = date.today()
thn_now = current_date.year
bln_now = current_date.month

# ambil host dari conf.py
host = create_host()

# buat engine db dari conf.py
engine = create_engine_db()

#### Fungsi rekam log pengunjung ####
# Matikan log bawaan Flask (opsional)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log_file = dataset['log_file']

# if not os.path.exists(log_file):
#    open(log_file, 'w').close()

# Buat file dan header kalau belum ada
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['waktu', 'ip', 'url', 'referer', 'user_agent'])

def log_info_pengunjung():
    path = request.path
    # Abaikan request file statis
    if path.startswith('/static') or path.startswith('/js') or path.endswith(('.css', '.js', '.jpg', '.png', '.woff2', '.ico')):
        return
    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    url = request.url
    referer = request.referrer or 'Langsung (direct)'
    user_agent = request.headers.get('User-Agent', 'Unknown')
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([waktu, ip, url, referer, user_agent])

####################################################### HTML Templates Backend
##############################################################################
# Halaman untuk menangani error
@app.errorhandler(Exception)
def handle_exception(e):
    return render_template("error.html", error=e), 500

# jalankan dulu sebelum request
@app.before_request
def sebelum_request():
    # Tangani hasil return dari cek_login()
    redirect_response = cek_login()
    if redirect_response:
        return redirect_response  # Jika ada redirect, kembalikan response tersebut
    
    # tulis log
    log_info_pengunjung()

# cek sudah login apa belum
def cek_login():
    allowed_routes = ['login', 'static', 'lacak_pengaduan']  # Route yang diizinkan tanpa login
    if request.endpoint not in allowed_routes and not session.get('user'):
        return redirect(url_for('login'))

@app.route('/login',  methods=['GET','POST'])
def login():
    pesan = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        df_users = get_data_users()
        df_users = df_users[(df_users['username'] == username) & (df_users['password'] == password)]
        # df_users = df_users.to_dict(orient="records")
        # print(df_users)
        if not df_users.empty:
            data_users = df_users.to_dict(orient="records")
            # print(f"Login berhasil! Selamat datang, {user['status']}.")
            session['user'] = username
            session['status'] = data_users[0]['status']
            return redirect(url_for('index'))
        else:
            pesan = "Login gagal! Username atau password salah."
    return render_template("login.html",pesan=pesan)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('status', None)
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Muat dan kelompokkan data ulasan
    df = get_data_ulasan()
    data = df.iloc[:4]
    # Konversi DataFrame ke daftar untuk dikirim ke template
    data = data.to_dict(orient="records")  # Mengonversi setiap baris menjadi dictionary

    # Muat data pengaduan
    df_pengaduan = get_data_pengaduan()
    jml_pengaduan = len(df_pengaduan)
    df_pengaduan_proses = df_pengaduan.query("status_pengaduan == 'Proses'")
    jml_pengaduan_proses = len(df_pengaduan_proses)
    df_pengaduan_selesai = df_pengaduan.query("status_pengaduan == 'selesai'")
    jml_pengaduan_selesai = len(df_pengaduan_selesai)
    stat_pengaduan = {
        "jml_pengaduan":jml_pengaduan,
        "jml_pengaduan_proses":jml_pengaduan_proses,
        "jml_pengaduan_selesai":jml_pengaduan_selesai
    }

    data_pengaduan = df_pengaduan.iloc[:4]
    data_pengaduan = data_pengaduan.to_dict(orient="records")

    # ambil statistik ulasan
    stat = calculate_review_stats(df)
    sentimen = calculate_sentiment()    
    return render_template('index.html', data=data, stat=stat, sentimen=sentimen, data_pengaduan=data_pengaduan, stat_pengaduan=stat_pengaduan)

@app.route('/overview')
def overview():
    # ambil total review dan rata-rata rating
    data_ulasan = get_data_ulasan()
    total_reviews, average_rating = calculate_review_stats(data_ulasan)
    
    data_pengaduan = get_data_pengaduan()
    total_pengaduan_internal = len(data_pengaduan)
    # print (data_pengaduan)
    
    # ambil tahun sekarang
    current_date = date.today()
    thn = current_date.year
    data_pengaduan_thn_terkini = data_pengaduan.query("thn_pengaduan == @thn")
    total_pengaduan_internal_terkini = len(data_pengaduan_thn_terkini)
    # print (data_pengaduan_thn_terkini)

    data_pengaduan_selesai = data_pengaduan.query("status_pengaduan == 'Selesai'")
    total_pengaduan_selesai = len(data_pengaduan_selesai)

    data_pengaduan_on_proses = data_pengaduan.query("status_pengaduan == 'Proses'")
    total_pengaduan_on_proses = len(data_pengaduan_on_proses)

    # ambil sentimen
    sentimen = calculate_sentiment()

    data = {
        'total_reviews':total_reviews,
        'average_rating':average_rating,
        'total_pengaduan_internal':total_pengaduan_internal,
        'total_pengaduan_internal_terkini':total_pengaduan_internal_terkini,
        'total_pengaduan_selesai':total_pengaduan_selesai,
        'total_pengaduan_on_proses':total_pengaduan_on_proses,
        'sentimen':sentimen
    }
    return render_template('mydash.html', data=data, thn=thn)

@app.route('/pengaduan')
def pengaduan():
    current_date = date.today()
    thn = current_date.year
    return render_template('filter_pengaduan.html',thn=thn)

@app.route('/pengaduan_lengkap', methods=["GET","POST"])
def pengaduan_lengkap():
    if request.method != "POST":
        return redirect('/pengaduan')
    else:
        if request.form.get('tahun') != 'semua':
            thn_ulasan = int(request.form.get('tahun'))
        else:
            thn_ulasan = 'semua'
        topik = request.form.get('topik')
        status = request.form.get('status')
        
        # Muat dan kelompokkan data
        data = load_and_group_data_pengaduan(thn_ulasan, topik, status)
        count = len(data)
        filter = {
            'thn': thn_ulasan,
            'topik': topik,
            'status': status,
            'count':count
        }
        # return f'tes {thn_ulasan}{topik}{status}{data}'
        return render_template('pengaduan_with_topic.html', data=data, filter=filter)
        

@app.route('/persons_pengaduan')
def persons_pengaduan():
    df = pd.read_csv(dataset['results_persons_pengaduan'])
    df = df.groupby(["persons"]).size().reset_index(name='count')
    df.sort_values(by="count", ascending=False, inplace=True)
    data = df.to_dict(orient="records")
    
    return render_template("persons_pengaduan.html",data=data)

@app.route("/person_pengaduan_review",methods=["GET","POST"])
def person_pengaduan_review():
    person = request.args.get('person')
    df = pd.read_csv(dataset['results_persons_pengaduan'])
    df = df.query("persons == @person")
    # Ambil reviewer_id dari filtered_df
    pengaduan_ids = df['pengaduan_id'].unique()
    
    # Baca dataset pengaduan
    # df_reviews = pd.read_excel(dataset['file_pengaduan'])
    df_reviews = get_data_pengaduan()
    df_reviews.sort_values(by="record_no", ascending=False, inplace=True)    
    
    # Filter df_reviews berdasarkan reviewer_id
    filtered_reviews = df_reviews[df_reviews['pengaduan_id'].isin(pengaduan_ids)]
    
    # ambil topic
    # topic_reviews = pd.read_csv('dataset/transformed_review_prediction.csv')
    topic_reviews = pd.read_csv(dataset['results_transformed_prediction_pengaduan'])
    filtered_topic = topic_reviews[topic_reviews['pengaduan_id'].isin(pengaduan_ids)]

    merged_data = filtered_reviews.merge(filtered_topic, on=['record_no', 'pengaduan_id'], how='left')    
    # merged_data.sort_values(by="record_no", ascending=False, inplace=True)    
    # Kelompokkan berdasarkan record_no dan reviewer_id
    grouped_data = []
    # Urutkan data berdasarkan record_no secara descending
    for (record_no, pengaduan_id), group in merged_data.groupby(['record_no', 'pengaduan_id']):
        main_data = {
            'record_no': record_no,
            'pengaduan_id': pengaduan_id,
            'nama': group.iloc[0]['nama'],
            'sumber_pengaduan': group.iloc[0]['sumber_pengaduan'],
            'fixed_pengaduan': group.iloc[0]['fixed_pengaduan'],
            'status_pengaduan': group.iloc[0]['status_pengaduan'],
            'tgl_pengaduan': group.iloc[0]['tgl_pengaduan'],
            'thn_pengaduan': group.iloc[0]['thn']
     }        
        predicted_data = group[['record_no','predicted_topic', 'predicted_sentiment', 'count']].drop_duplicates().to_dict(orient='records')
        grouped_data.append({
                'main_data': main_data,
                'topic': predicted_data
            })    
    # Sort berdasarkan record_no descending
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    return render_template("person_pengaduan_review.html",data=grouped_data, person=person)

@app.route('/places_pengaduan')
def places_pengaduan():
    df = pd.read_csv(dataset['results_places_pengaduan'])
    df = df.groupby(["places"]).size().reset_index(name='count')
    df.sort_values(by="count", ascending=False, inplace=True)
    data = df.to_dict(orient="records")
    
    return render_template("places_pengaduan.html",data=data)

@app.route("/place_pengaduan_review",methods=["GET","POST"])
def place_pengaduan_review():
    place = request.args.get('place')
    df = pd.read_csv(dataset['results_places_pengaduan'])
    df = df.query("places == @place")
    # Ambil reviewer_id dari filtered_df
    pengaduan_ids = df['pengaduan_id'].unique()
    
    # Baca dataset pengaduan
    # df_reviews = pd.read_excel(dataset['file_pengaduan'])
    df_reviews = get_data_pengaduan()
    # df_reviews.sort_values(by="record_no", ascending=False, inplace=True)    
    
    # Filter df_reviews berdasarkan reviewer_id
    filtered_reviews = df_reviews[df_reviews['pengaduan_id'].isin(pengaduan_ids)]
    
    # ambil topic
    # topic_reviews = pd.read_csv('dataset/transformed_review_prediction.csv')
    topic_reviews = pd.read_csv(dataset['results_transformed_prediction_pengaduan'])
    filtered_topic = topic_reviews[topic_reviews['pengaduan_id'].isin(pengaduan_ids)]

    merged_data = filtered_reviews.merge(filtered_topic, on=['record_no', 'pengaduan_id'], how='left')    
    # merged_data.sort_values(by="record_no", ascending=False, inplace=True)    
    # Kelompokkan berdasarkan record_no dan reviewer_id
    grouped_data = []
    # Urutkan data berdasarkan record_no secara descending
    for (record_no, pengaduan_id), group in merged_data.groupby(['record_no', 'pengaduan_id']):
        main_data = {
            'record_no': record_no,
            'pengaduan_id': pengaduan_id,
            'nama': group.iloc[0]['nama'],
            'sumber_pengaduan': group.iloc[0]['sumber_pengaduan'],
            'fixed_pengaduan': group.iloc[0]['fixed_pengaduan'],
            'status_pengaduan': group.iloc[0]['status_pengaduan'],
            'tgl_pengaduan': group.iloc[0]['tgl_pengaduan'],
            'thn_pengaduan': group.iloc[0]['thn']
     }        
        predicted_data = group[['record_no','predicted_topic', 'predicted_sentiment', 'count']].drop_duplicates().to_dict(orient='records')
        grouped_data.append({
                'main_data': main_data,
                'topic': predicted_data
            })    
    # Sort berdasarkan record_no descending
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    return render_template("place_pengaduan_review.html",data=grouped_data, place=place)


@app.route('/filter_ulasan', methods=["GET","POST"])
def filter_ulasan():
    return render_template('filter_reviews.html')

@app.route('/ulasan_lengkap', methods=["GET","POST"])
def ulasan_lengkap():
    if request.method != "POST":
        return redirect('/filter_ulasan')
    else:
        if request.form.get('tahun') != 'semua':
            thn_ulasan = int(request.form.get('tahun'))
        else:
            thn_ulasan = 'semua'
        topik = request.form.get('topik')
        sentimen = request.form.get('sentimen')
        
        # Muat dan kelompokkan data
        data = load_and_group_data(thn_ulasan, topik, sentimen)
        count = len(data)
        filter = {
            'thn': thn_ulasan,
            'topik': topik,
            'sentimen': sentimen,
            'count':count
        }
        return render_template('reviews_with_topic.html', data=data, filter=filter)

@app.route('/persons')
def persons():
    df = pd.read_csv(dataset['results_persons_ulasan'])
    df = df.groupby(["persons"]).size().reset_index(name='count')
    df.sort_values(by="count", ascending=False, inplace=True)
    data = df.to_dict(orient="records")

    return render_template("persons.html",data=data)

@app.route("/person_review",methods=["GET","POST"])
def person_review():
    person = request.args.get('person')
    df = pd.read_csv(dataset['results_persons_ulasan'])
    df = df.query("persons == @person")
    # Ambil reviewer_id dari filtered_df
    reviewer_ids = df['reviewer_id'].unique()
    
    # Baca dataset 'gmaps_review.xlsx'
    df_reviews = pd.read_excel('dataset/gmaps_review.xlsx')
    # df_reviews.sort_values(by="record_no", ascending=False, inplace=True)    
    
    # Filter df_reviews berdasarkan reviewer_id
    filtered_reviews = df_reviews[df_reviews['reviewer_id'].isin(reviewer_ids)]
    
    # ambil topic
    # topic_reviews = pd.read_csv('dataset/transformed_review_prediction.csv')
    topic_reviews = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    filtered_topic = topic_reviews[topic_reviews['reviewer_id'].isin(reviewer_ids)]

    merged_data = filtered_reviews.merge(filtered_topic, on=['record_no', 'reviewer_id'], how='left')    
    # merged_data.sort_values(by="record_no", ascending=False, inplace=True)    
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
        predicted_data = group[['record_no','predicted_topic', 'predicted_sentiment', 'count']].drop_duplicates().to_dict(orient='records')
        grouped_data.append({
                'main_data': main_data,
                'topic': predicted_data
            })    
    # Sort berdasarkan record_no descending
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    return render_template("person_review.html",data=grouped_data, person=person)

@app.route('/places')
def places():
    df = pd.read_csv(dataset['results_places_ulasan'])
    df = df.groupby(["places"]).size().reset_index(name='count')
    df.sort_values(by="count", ascending=False, inplace=True)
    data = df.to_dict(orient="records")

    return render_template("places.html",data=data)

@app.route("/place_review",methods=["GET","POST"])
def place_review():
    place = request.args.get('place')
    df = pd.read_csv(dataset['results_places_ulasan'])
    df = df.query("places == @place")
    # Ambil reviewer_id dari filtered_df
    reviewer_ids = df['reviewer_id'].unique()

    # Baca dataset 'gmaps_review.xlsx'
    df_reviews = pd.read_excel(dataset['file_ulasan'])
    # df_reviews.sort_values(by="record_no", ascending=False, inplace=True)    
    
    # Filter df_reviews berdasarkan reviewer_id
    filtered_reviews = df_reviews[df_reviews['reviewer_id'].isin(reviewer_ids)]
    
    # ambil topic
    # topic_reviews = pd.read_csv('dataset/transformed_review_prediction.csv')
    topic_reviews = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    filtered_topic = topic_reviews[topic_reviews['reviewer_id'].isin(reviewer_ids)]

    merged_data = filtered_reviews.merge(filtered_topic, on=['record_no', 'reviewer_id'], how='left')    
    # merged_data.sort_values(by="record_no", ascending=False, inplace=True)    
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
        predicted_data = group[['record_no','predicted_topic', 'predicted_sentiment', 'count']].drop_duplicates().to_dict(orient='records')
        grouped_data.append({
                'main_data': main_data,
                'topic': predicted_data
            })    
    # Sort berdasarkan record_no descending
    grouped_data = sorted(grouped_data, key=lambda x: x['main_data']['record_no'], reverse=True)
    return render_template("place_review.html",data=grouped_data, place=place)

@app.route('/analisis_topik_ulasan')
def analisis_topik_ulasan():
    return render_template('analisis_topik_ulasan.html')

@app.route('/laporan_pengaduan_bulanan', methods=["GET","POST"])
def laporan_pengaduan_bulanan():
    if not request.form.get('thn'):
        thn = thn_now
        bln = bln_now
    else:
        thn = int(request.form.get('thn'))
        bln = int(request.form.get('bln'))
    nama_bln = get_month_name(bln)
    if thn == 0:
        thn_label = ""
    else:
        thn_label = thn
    label = f'Laporan Pengaduan {nama_bln} {thn_label}'

    df_pengaduan = get_data_pengaduan()
    df_pengaduan = df_pengaduan.query("status_pengaduan != 'Tolak'")
    df_pengaduan['thn'] = df_pengaduan['tgl_pengaduan'].dt.year
    df_pengaduan['bln'] = df_pengaduan['tgl_pengaduan'].dt.month

    df_pengaduan = df_pengaduan.query("thn == @thn")
    df_pengaduan = df_pengaduan.query("bln == @bln")

    df_pengaduan.sort_values(by="record_no", ascending=True, inplace=True)

    data_pengaduan = df_pengaduan.to_dict(orient="records")    

    print (thn,bln, label)
    print (data_pengaduan)
    # return f'Ini laporan pengaduan Bulanan {data_pengaduan}'
    return render_template('laporan_pengaduan_bulanan.html', data_pengaduan=data_pengaduan, thn=thn, bln=bln,label=label)

@app.route('/download_laporan_pengaduan_bulanan', methods=["GET","POST"])
def download_laporan_pengaduan_bulanan():
    thn = int(request.args.get('thn'))
    bln = int(request.args.get('bln'))

    df_pengaduan = get_data_pengaduan()
    
    df_pengaduan = df_pengaduan.query("status_pengaduan != 'Tolak'")
    
    df_pengaduan['thn'] = df_pengaduan['tgl_pengaduan'].dt.year
    
    df_pengaduan['bln'] = df_pengaduan['tgl_pengaduan'].dt.month

    df_pengaduan = df_pengaduan.query("thn == @thn")
    
    df_pengaduan = df_pengaduan.query("bln == @bln")

    df_pengaduan.sort_values(by="record_no", ascending=True, inplace=True)
    # Pilih kolom yang ingin ditampilkan
    selected_columns = ["tgl_pengaduan","nama","telepon","alamat","isi_pengaduan","sumber_pengaduan","solusi_pengaduan"]  # Ganti dengan nama kolom yang ingin ditampilkan
    df_pengaduan = df_pengaduan[selected_columns]

    print(thn, bln)    

    output_file = f"export/lapbul_{thn}{bln}.xlsx"
    df_pengaduan.to_excel(output_file, index=False)

    # Kirim file Excel sebagai respons download
    return send_file(output_file, as_attachment=True)

@app.route('/monev_pengaduan_tahunan', methods=["GET","POST"])
def monev_pengaduan_tahunan():
    # if request.form.get('tahun') != 'semua':
    if not request.form.get('thn'):
        thn = thn_now
    else:
        thn = int(request.form.get('thn'))
    
    df_pengaduan = get_data_pengaduan()
    df_pengaduan['thn'] = df_pengaduan['tgl_pengaduan'].dt.year
    df_pengaduan = df_pengaduan.query("thn == @thn")
    df_pengaduan['bln'] = df_pengaduan['tgl_pengaduan'].dt.month

    df_bulan_pengaduan = df_pengaduan.groupby(["bln"]).size().reset_index(name='count')
    print (df_bulan_pengaduan)
    data_bulan = df_bulan_pengaduan.to_dict(orient="records")
    df_sumber_pengaduan = df_pengaduan.groupby(["bln","sumber_pengaduan"]).size().reset_index(name='count')
    print (df_sumber_pengaduan)
    data_sumber = df_sumber_pengaduan.to_dict(orient="records")

    total_pengaduan = df_pengaduan['record_no'].count()
    df_sumber_pengaduan_total = df_pengaduan.groupby(["sumber_pengaduan"]).size().reset_index(name='count')
    print (df_sumber_pengaduan_total)
    data_sumber_total = df_sumber_pengaduan_total.to_dict(orient="records")

    # Tabel Status Pengaduan
    df_status = df_pengaduan.groupby(["status_pengaduan"]).size().reset_index(name='count')

    # Ambil jumlah atau default ke 0 jika tidak ada record
    selesai_count = df_status.loc[df_status['status_pengaduan'] == 'Selesai', 'count'].sum() if 'Selesai' in df_status['status_pengaduan'].values else 0
    proses_count = df_status.loc[df_status['status_pengaduan'] == 'Proses', 'count'].sum() if 'Proses' in df_status['status_pengaduan'].values else 0
    tunda_count = df_status.loc[df_status['status_pengaduan'] == 'Tolak', 'count'].sum() if 'Tolak' in df_status['status_pengaduan'].values else 0

    # Buat dictionary
    status_selesai = {'status_pengaduan': 'Selesai', 'jml': int(selesai_count)}
    status_proses = {'status_pengaduan': 'Proses', 'jml': int(proses_count)}
    status_tunda = {'status_pengaduan': 'Tolak', 'jml': int(tunda_count)}


    data_status = [
        status_selesai,
        status_proses,
        status_tunda
    ]

    nama_bulan = [
        "", "Januari", "Februari", "Maret", "April",
        "Mei", "Juni", "Juli", "Agustus", "September",
        "Oktober", "November", "Desember"
    ]

    return render_template(
        'monev_pengaduan_tahunan.html', 
        thn=thn, data_bulan=enumerate(data_bulan, start=1), 
        data_sumber=data_sumber, 
        data_status=data_status, 
        nama_bulan=nama_bulan,
        total_pengaduan=total_pengaduan,
        data_sumber_total=data_sumber_total
    )

@app.route('/download_tbl_01')
def download_tbl_01():
    # install library
    # pip install lxml
    # pip install html5lib

    thn = request.args.get('thn')
    
    host = 'http://localhost:5000/'
    login_url = host+"login"  # URL login Flask
    data_url = host+f"monev_pengaduan_tahunan?thn={thn}"  # URL data tabel
    
    print(data_url)

    session = requests.Session()

    # Login ke aplikasi Flask
    login_payload = {
        'username': 'admin@dara.com',  # Ganti dengan username yang valid
        'password': 'admin'   # Ganti dengan password yang valid
    }
    login_response = session.post(login_url, data=login_payload)

    if login_response.status_code != 200:
        return "Login gagal", 401

    try:
        # Ambil halaman dengan sesi login
        response = session.get(data_url)
        response.raise_for_status()  # Pastikan permintaan berhasil

        # Baca tabel dari HTML
        tables = pd.read_html(response.text, flavor="html5lib")
        if not tables:
            return "Tabel tidak ditemukan pada halaman", 404

        # Simpan tabel pertama ke file Excel
        df = tables[0]
        output_file = "output.xlsx"
        df.to_excel(output_file, index=False)

        # Kirim file Excel sebagai respons download
        return send_file(output_file, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500



#============ list data ulasan pada fitur manajemen data
@app.route('/entry_pengaduan')
def entry_pengaduan():  
    # if 'user' not in session:
    #    return redirect(url_for('login'))
    # Ambil data dari Excel
    df = get_data_pengaduan()
    # Konversi DataFrame ke daftar untuk dikirim ke template
    data = df.to_dict(orient="records")  # Mengonversi setiap baris menjadi dictionary
    columns = df.columns.tolist()  # Mendapatkan nama kolom
    last_record = get_last_record()
    # print(last_record)

    return render_template("entry_pengaduan.html", data=data, columns=columns)

# download pengaduan menjadi file xlsx
@app.route('/download-pengaduan')
def download_pengaduan():
    
    df = pd.read_excel(dataset['file_pengaduan'])
    
    # 2. Simpan ke Excel di memory pakai openpyxl
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    # 3. Kirim file ke browser sebagai attachment
    return send_file(
        output,
        download_name='data_pengaduan.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/detail_pengaduan')
def detail_pengaduan():
    record_no = request.args.get('recNo')
    pengaduan_id = int(request.args.get('revID'))

    # df = pd.read_excel(dataset['file_pengaduan'])
    df = get_data_pengaduan()
    df = df.query("pengaduan_id == @pengaduan_id")
    data = df.to_dict(orient="records")

    # df_detail dari tabel pengaduan_detail
    df_detail = get_data_pengaduan_detail()
    df_detail = df_detail.query("pengaduan_id == @pengaduan_id")
    detail = df_detail.to_dict(orient="records")

    host = ip_server
    key = data[0]['token']
    LONG_URL = ip_server+'/lacak_pengaduan?key='+key
    API_URL = f"http://tinyurl.com/api-create.php?url={LONG_URL}"
    response = requests.get(API_URL)
    SHORT_URL = response.text

    return render_template("detail_pengaduan.html", data=data, detail=detail, host=host, LONG_URL=LONG_URL, SHORT_URL=SHORT_URL)

# Route untuk menghapus pengaduan
@app.route('/hapus_pengaduan', methods=["POST"])
def hapus_pengaduan():
    try:
        # Ambil data dari form
        record_no = int(request.form.get('recNo'))
        pengaduan_id = int(request.form.get('revID'))

        # panggil fungsi hapus database MySQL (helper_ulasan)
        delete_row_pengaduan(pengaduan_id)
        # Flash pesan sukses
        # flash(f"Ulasan dengan record_no {record_no} berhasil dihapus. {result_message}", "success")

    except ValueError as e:
        # Flash pesan kesalahan jika record_no tidak ditemukan
        flash(str(e), "danger")
    except Exception as e:
        # Flash pesan kesalahan umum
        flash(f"Terjadi kesalahan: {str(e)}", "danger")
    # Redirect kembali ke halaman utama
    return redirect(url_for('entry_pengaduan'))
    
# Form tambah Data Pengaduan
@app.route('/form_entry_pengaduan')
def addPengaduan():
    record_no = get_last_record_pengaduan()+1
    return render_template("form_entry_pengaduan.html", record_no=record_no)

# Posting Data Pengaduan
@app.route('/savePengaduan', methods=['POST'])
def savePengaduan():
    try:
        last_record = get_last_record_pengaduan()
        record_no = last_record + 1

        tgl_pengaduan_str = request.form.get('tgl_pengaduan')
        if not tgl_pengaduan_str:
            return {"error": "Tanggal pengaduan harus diisi."}, 400

        try:
            tgl_pengaduan = datetime.strptime(tgl_pengaduan_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return {"error": "Format tanggal tidak valid. Gunakan format YYYY-MM-DDTHH:MM."}, 400

        thn = tgl_pengaduan.year
        pengaduan_id = int(thn) * 1000000 + record_no
        name = request.form.get('name')
        telepon = request.form.get('telepon')
        alamat = request.form.get('alamat')
        penerima_pengaduan = 'humas'
        sumber_pengaduan = request.form.get('sumber_pengaduan')
        kategori_pengaduan = request.form.get('kategori_pengaduan')
        isi_pengaduan = request.form.get('isi_pengaduan')
        fixed_pengaduan = isi_pengaduan
        progress_pengaduan = 'Pengaduan masuk'
        status_pengaduan = 'Proses'
        tgl_progress = tgl_pengaduan
        solusi_pengaduan = ''
        token = hashlib.md5(str(pengaduan_id).encode('utf-8')).hexdigest()

        lama = 0
        keterangan = isi_pengaduan
        actor = 'pelapor'

        data = {
            "record_no": record_no,
            "pengaduan_id": pengaduan_id,
            "tgl_pengaduan": tgl_pengaduan,
            "nama": name,
            "telepon": telepon,
            "alamat": alamat,
            "sumber_pengaduan": sumber_pengaduan,
            "penerima_pengaduan": penerima_pengaduan,
            "kategori_pengaduan": kategori_pengaduan,
            "isi_pengaduan": isi_pengaduan,
            "fixed_pengaduan": fixed_pengaduan,
            "solusi_pengaduan": solusi_pengaduan,
            "progress_pengaduan": progress_pengaduan,
            "status_pengaduan": status_pengaduan,
            "tgl_progress": tgl_progress,
            "token": token
        }

        query = text("""
            INSERT INTO pengaduan (
                record_no, pengaduan_id, tgl_pengaduan, nama, telepon, alamat, sumber_pengaduan, 
                penerima_pengaduan, kategori_pengaduan, isi_pengaduan, fixed_pengaduan, 
                solusi_pengaduan, progress_pengaduan, status_pengaduan, tgl_progress, token
            ) VALUES (
                :record_no, :pengaduan_id, :tgl_pengaduan, :nama, :telepon, :alamat, :sumber_pengaduan, 
                :penerima_pengaduan, :kategori_pengaduan, :isi_pengaduan, :fixed_pengaduan, 
                :solusi_pengaduan, :progress_pengaduan, :status_pengaduan, :tgl_progress, :token
            )
        """)

        data_detail = {
            "pengaduan_id": pengaduan_id,
            "tgl": tgl_progress,
            "lama": lama,
            "progress_pengaduan": progress_pengaduan,
            "status_pengaduan": status_pengaduan,
            "keterangan": keterangan,
            "actor": actor
        }

        query_detail = text("""
            INSERT INTO pengaduan_detail (
                pengaduan_id, tgl, lama, progress_pengaduan, status_pengaduan, keterangan, actor
            ) VALUES (
                :pengaduan_id, :tgl, :lama, :progress_pengaduan, :status_pengaduan, :keterangan, :actor
            )
        """)

        # Gunakan transaksi eksplisit
        with engine.connect() as connection:
            with connection.begin():  # Pastikan transaksi dikomit
                connection.execute(query, data)
                connection.execute(query_detail, data_detail)
                print("Data berhasil ditambahkan.")
        # return {"success": True, "message": "Data pengaduan berhasil disimpan."}, 200

    except SQLAlchemyError as e:
        print("Error:", str(e))
        return {"error": "Gagal menyimpan data pengaduan. Silakan coba lagi."}, 500
    
    # run model predict for pengaduan
    predict_pengaduan()       
    return redirect('/entry_pengaduan')


@app.route('/form_verifikasi_humas')
def form_verifikasi_humas():
    # record_no = request.args.get('recNo')
    pengaduan_id = int(request.args.get('revID'))
    df = get_data_pengaduan()    
    df = df.query("pengaduan_id == @pengaduan_id")
    data = df.to_dict(orient="records")
    return render_template("form_verifikasi_humas.html", data=data)

@app.route('/update_pengaduan_detail', methods=['POST'])
def update_pengaduan_detail():
    pengaduan_id = request.form.get('pengaduan_id')
    tgl_awal = request.form.get('tgl_awal')
    if tgl_awal:
        tgl_awal = datetime.strptime(tgl_awal, '%a, %d %b %Y %H:%M:%S %Z')
    tgl = request.form.get('tgl')
    tgl = datetime.strptime(tgl, '%Y-%m-%dT%H:%M')    
    # Hitung selisih
    delta = tgl - tgl_awal
    # Konversi ke menit
    minutes_difference = delta.total_seconds() / 60
    lama = minutes_difference
    # print(tgl_awal, tgl, lama)

    progress_pengaduan = request.form.get('progress_pengaduan')
    status_pengaduan = request.form.get('status_pengaduan')
    keterangan = request.form.get('keterangan')
    if progress_pengaduan == 'Verifikasi unit':
        actor = 'unit'
    else:
        actor = 'humas'

    data_detail = {
        "pengaduan_id": pengaduan_id,
        "tgl": tgl,
        "lama": lama,
        "progress_pengaduan": progress_pengaduan,
        "status_pengaduan": status_pengaduan,
        "keterangan": keterangan,
        "actor": actor
    }
    data_update = {
        "pengaduan_id": pengaduan_id,
        "progress_pengaduan": progress_pengaduan,
        "status_pengaduan": status_pengaduan,
        "tgl_progress": tgl
    }
    query_detail = text("""
        INSERT INTO pengaduan_detail (
            pengaduan_id, tgl, lama, progress_pengaduan, status_pengaduan, keterangan, actor
        ) VALUES (
            :pengaduan_id, :tgl, :lama, :progress_pengaduan, :status_pengaduan, :keterangan, :actor
        )
    """)
    query_update = text("""
        UPDATE pengaduan
        SET progress_pengaduan = :progress_pengaduan,
            status_pengaduan = :status_pengaduan,
            tgl_progress = :tgl_progress
        WHERE pengaduan_id = :pengaduan_id
    """)
    # Gunakan transaksi eksplisit
    with engine.connect() as connection:
        with connection.begin():  # Pastikan transaksi dikomit
            connection.execute(query_detail, data_detail)
            connection.execute(query_update, data_update)
            print("Data berhasil ditambahkan dan diupdate.")
    # return "Data berhasil diproses."
    # return f"{data}"
    return redirect('/detail_pengaduan?revID='+pengaduan_id)

@app.route('/form_teruskan_pengaduan')
def form_teruskan_pengaduan():
    pengaduan_id = int(request.args.get('revID'))
    df = get_data_pengaduan()    
    df = df.query("pengaduan_id == @pengaduan_id")
    data = df.to_dict(orient="records")

    #return f"<h1>Form teruskan pengaduan</h1>"
    return render_template('form_teruskan_pengaduan.html', data=data)

@app.route('/form_verifikasi_unit')
def form_verifikasi_unit():
    pengaduan_id = int(request.args.get('revID'))
    df = get_data_pengaduan()    
    df = df.query("pengaduan_id == @pengaduan_id")
    data = df.to_dict(orient="records")

    # return f"Form verifikasi unit"
    return render_template('form_verifikasi_unit.html', data=data)

@app.route('/form_penyelesaian_pengaduan')
def form_penyelesaian_pengaduan():
    pengaduan_id = int(request.args.get('revID'))
    df = get_data_pengaduan()    
    df = df.query("pengaduan_id == @pengaduan_id")
    data = df.to_dict(orient="records")

    return render_template('form_penyelesaian_pengaduan.html', data=data)

#====================================================


@app.route('/entry_ulasan')
def reviews():
    # Ambil data dari Excel
    df = get_data_ulasan()
    data = df.to_dict(orient="records")
    columns = df.columns.tolist()
    last_record = get_last_record()

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(data)
    total_pages = math.ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data[start:end]

    return render_template(
        "entry_ulasan.html",
        data=paginated_data,
        columns=columns,
        page=page,
        total_pages=total_pages
    )

# download ulasan menjadi file xlsx
@app.route('/download-ulasan')
def download_ulasan():
    
    df = pd.read_excel(dataset['file_ulasan'])
    
    # 2. Simpan ke Excel di memory pakai openpyxl
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    # 3. Kirim file ke browser sebagai attachment
    return send_file(
        output,
        download_name='data_ulasan.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# Form tambah Data Ulasan
@app.route('/form_entry_ulasan')
def addReview():
    return render_template("form_entry_ulasan.html")

# Posting Data Ulasan
@app.route('/saveUlasan',methods=['POST'])
def saveUlasan():
    last_record = get_last_record()
    record_no = last_record+1
    # Mengambil data dari form
    reviewer_id = request.form.get('reviewer_id')
    name = request.form.get('name')
    link = f'https://www.google.com/maps/contrib/{reviewer_id}?hl=id&ved=1t:31294&ictx=111'
    thumbnail = request.form.get('thumbnail') or ''  # Opsional
    # reviews = request.form.get('review')
    reviews = 0
    photos = request.form.get('photos') or 0  # Opsional
    localGuide = request.form.get('localGuide') or ''  # Opsional
    levelGuide = request.form.get('levelGuide') or ''
    rating = request.form.get('rating')
    duration = request.form.get('duration') or ''  # Opsional
    tgl_entry = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Tanggal saat ini

    tgl_ulasan = request.form.get('tgl_ulasan')
    # Parsing string ke datetime
    tgl_ulasan = datetime.strptime(tgl_ulasan, '%Y-%m-%dT%H:%M')
    # Format ulang ke string tanpa 'T'
    tgl_ulasan = tgl_ulasan.strftime('%Y-%m-%d %H:%M:%S')

    snippet = request.form.get('review') or ''  # Opsional
    fixed_review = snippet
    likes = request.form.get('likes') or 0  # Opsional
    images = request.form.get('images') or ''  # Opsional
    response_from_owner = request.form.get('response_from_owner') or ''  # Opsional
    thn_ulasan = tgl_ulasan.split('-')[0] if tgl_ulasan else ''  # Tahun dari tanggal ulasan
    thn_ulasan = int(thn_ulasan)

    # Mengunduh thumbnail dan menyimpan dengan nama reviewer_id.jpg
    output_folder = 'static/reviewer_thumbnail'
    if thumbnail is None or thumbnail == "":
        thumbnail = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqDShlwPIXpZeHVOlDLQ8MrkAY3TDZr2OxCg&s'
    response = requests.get(thumbnail, stream=True)
    if response.status_code == 200:
        # Simpan file menggunakan reviewer_id sebagai nama file
        file_name = os.path.join(output_folder, f'{reviewer_id}.jpg')
        with open(file_name, 'wb') as f:
            f.write(response.content)
            print(f"Thumbnail untuk reviewer_id {reviewer_id} berhasil diunduh.")
    else:
        print(f"Thumbnail untuk reviewer_id {reviewer_id} gagal diunduh. Status code: {response.status_code}")
    

    data_ulasan = {
            "record_no": record_no,
            "reviewer_id": reviewer_id,
            "name": name,
            "link": link,
            "thumbnail": thumbnail,
            "reviews": reviews,
            "photos": photos,
            "localGuide": localGuide,
            "levelGuide": levelGuide,
            "rating": rating,
            "duration": duration,
            "tgl_entry": tgl_entry,
            "tgl_ulasan": tgl_ulasan,
            "snippet": snippet,
            "fixed_review": fixed_review,
            "likes": likes,
            "images": images,
            "response_from_owner": response_from_owner,
            "thn_ulasan": thn_ulasan
        }
    
    query_ulasan = text("""
            INSERT INTO ulasan (
                record_no, reviewer_id, name, link, thumbnail, reviews, photos, localGuide, levelGuide, rating, duration, tgl_entry,
                tgl_ulasan, snippet, fixed_review, likes, images, response_from_owner, thn_ulasan
            ) VALUES (
                :record_no, :reviewer_id, :name, :link, :thumbnail, :reviews, :photos, :localGuide, :levelGuide, :rating, :duration, :tgl_entry,
                :tgl_ulasan, :snippet, :fixed_review, :likes, :images, :response_from_owner, :thn_ulasan
            )
        """)
    
    # Gunakan transaksi eksplisit
    with engine.connect() as connection:
        with connection.begin():  # Pastikan transaksi dikomit
            connection.execute(query_ulasan, data_ulasan)
            print("Data berhasil ditambahkan dan diupdate.")
    

    predict_ulasan()
    return redirect('/entry_ulasan')

# Lihat ulasan satu - persatu
@app.route('/detail_ulasan',methods=['GET',"POST"])
def detail_ulasan():
    record_no = request.args.get('recNo')
    reviewer_id = request.args.get('revID')
    # reviewer_id = int(reviewer_id)
    name = request.args.get('name')
    ulasan = request.args.get('rev')
    thumbnail = request.args.get('thumbnail')

    # df = pd.read_excel(dataset['file_ulasan'])
    df = get_data_ulasan()
    df = df.query("reviewer_id == @reviewer_id")
    data = df.to_dict(orient="records")
    
    return render_template('detail_ulasan.html', data=data)

def delete_row_by_record_no(record_no):
    try:
        print("Menghapus ulasan :", record_no)
        # Query untuk menghapus data
        query = text("DELETE FROM ulasan WHERE record_no = :record_no")
        # Menggunakan transaksi eksplisit
        with engine.connect() as connection:
            with connection.begin():  # Memulai transaksi
                result = connection.execute(query, {"record_no": record_no})                
    except SQLAlchemyError as e:
        print("Error:", str(e))
        return jsonify({"error": "Terjadi kesalahan saat menghapus data pengaduan"}), 500

# Fungsi untuk menghapus gambar
def delete_image(reviewer_id):
    # Folder lokasi gambar
    IMAGE_FOLDER = "static/reviewer_thumbnail/"

    # Bangun path lengkap file
    file_path = os.path.join(IMAGE_FOLDER, f"{reviewer_id}.jpg")

    # Periksa apakah file ada
    if os.path.exists(file_path):
        os.remove(file_path)  # Hapus file
        return f"Gambar dengan reviewer_id {reviewer_id} berhasil dihapus."
    else:
        return f"Gambar dengan reviewer_id {reviewer_id} tidak ditemukan."

# Route untuk menghapus ulasan
@app.route('/hapus_ulasan', methods=["POST"])
def hapus_ulasan():
    try:
        # Ambil data dari form
        record_no = int(request.form.get('recNo'))
        reviewer_id = request.form.get('revID')

        # Hapus data dari file Excel dan gambar
        delete_row_by_record_no(record_no)
        result_message = delete_image(reviewer_id)

        # Flash pesan sukses
        flash(f"Ulasan dengan record_no {record_no} berhasil dihapus. {result_message}", "success")
    except ValueError as e:
        # Flash pesan kesalahan jika record_no tidak ditemukan
        flash(str(e), "danger")
    except Exception as e:
        # Flash pesan kesalahan umum
        flash(f"Terjadi kesalahan: {str(e)}", "danger")
    # Redirect kembali ke halaman utama
    return redirect(url_for('reviews'))

@app.route('/about')
def about():

    return render_template('about.html')

@app.route('/dokumentasi')
def dokumentasi():

    return render_template('dokumentasi.html')

@app.route('/faq')
def faq():
    df = pd.read_excel(dataset['file_faq'])
    data = df.to_dict(orient='records')
    return render_template('faq.html',faq=data)

@app.route('/settings')
def settings():
    if session['status'] == 'admin':
        return render_template('settings.html')
    else:
        return render_template('setting_forbiden.html')
    
@app.route('/setting_pengguna')
def setting_pengguna():
    users = get_data_users()
    users = users.to_dict(orient="records")
    return render_template('settings_pengguna.html',users=users)

@app.route('/setting_unit')
def setting_unit():
    df = pd.read_excel(dataset['data_unit'])
    unit = df.to_dict(orient="records")
    return render_template('settings_unit.html',unit=unit)

@app.route('/setting_data_latih')
def setting_data_latih():
    df_latih = pd.read_excel(dataset['data_training'])
    jml_record = len(df_latih)

    df_topic = df_latih.groupby("topic").size().reset_index(name='jumlah_records')
    df_topic["persen"] = round(df_topic["jumlah_records"]/jml_record * 100,2)        
    data_latih = df_topic.to_dict(orient="records")

    df_jenis = df_latih.groupby("jenis").size().reset_index(name='jumlah_records')
    df_jenis["persen"] = round(df_jenis["jumlah_records"]/jml_record * 100,2)
    data_latih2 = df_jenis.to_dict(orient="records")

    df_sentimen = df_latih.groupby("sentimen").size().reset_index(name='jumlah_records')
    df_sentimen["persen"] = round(df_sentimen["jumlah_records"]/jml_record * 100,2)
    data_latih3 = df_sentimen.to_dict(orient="records")

    return render_template('settings_data_latih.html',dataset=dataset, data_latih=data_latih, data_latih2=data_latih2, data_latih3=data_latih3)

@app.route('/lacak_pengaduan', methods=["GET","POST"])
def lacak_pengaduan():
    token = request.args.get('key')

    df_pengaduan = get_data_pengaduan()
    df_pengaduan = df_pengaduan.query("token == @token")
    data_pengaduan = df_pengaduan.to_dict(orient="records")

    pengaduan_id = data_pengaduan[0]['pengaduan_id']
    # print(pengaduan_id)

    df_detail = get_data_pengaduan_detail()
    df_detail = df_detail.query("pengaduan_id == @pengaduan_id")
    data_detail = df_detail.to_dict(orient="records")

    return render_template('lacak_pengaduan.html', 
    data_pengaduan=data_pengaduan,
    data_detail=data_detail
    )

##########################################################################################################################
##########################################################################################################################

# API for predict
@app.route('/predict',methods=['GET',"POST"])
def predict():
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
    training_data = pd.read_excel(dataset['data_training'])

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
        
    
    text = request.args.get('text')
    text = clean_text(text)

    proba_topic = topic_model.predict_proba([text])[0]
    label_topic = topic_model.predict([text])[0]
    kelas_topic = topic_model.named_steps['classifier'].classes_
    proba_topic_dict = dict(zip(kelas_topic, proba_topic))
    idx_max_topic = np.argmax(proba_topic)
    max_label_topic = topic_model.named_steps['classifier'].classes_[idx_max_topic]
    max_proba_topic = proba_topic[idx_max_topic]


    proba_sentiment = sentiment_model.predict_proba([text])[0]
    label_sentiment = sentiment_model.predict([text])[0]
    kelas_sentiment = sentiment_model.named_steps['classifier'].classes_
    proba_sentiment_dict = dict(zip(kelas_sentiment, proba_sentiment))
    idx_max_sentiment = np.argmax(proba_sentiment)
    max_label_sentiment = sentiment_model.named_steps['classifier'].classes_[idx_max_sentiment]
    max_proba_sentiment = proba_sentiment[idx_max_sentiment]

    proba_jenis = jenis_model.predict_proba([text])[0]
    label_jenis = jenis_model.predict([text])[0]
    kelas_jenis = jenis_model.named_steps['classifier'].classes_
    proba_jenis_dict = dict(zip(kelas_jenis, proba_jenis))
    idx_max_jenis = np.argmax(proba_jenis)
    max_label_jenis = jenis_model.named_steps['classifier'].classes_[idx_max_jenis]
    max_proba_jenis = proba_jenis[idx_max_jenis]

    results = {
    "clean_text": text,
    "jenis": {"predicted":max_label_jenis, "proba":round(max_proba_jenis * 100, 2)},
    "topic": {"predicted":max_label_topic, "proba":round(max_proba_topic * 100, 2)},
    "sentiment": {"predicted":max_label_sentiment, "proba":round(max_proba_sentiment * 100, 2)}
    } 

    return results


##################################################### RestFull API for chartJS
##############################################################################

#---------------------- Chart Ulasan -----------------------------#

@app.route('/chart_data_ulasan_pertahun')
def chart_data_ulasan_pertahun():
    df = get_data_ulasan()
    df = df.groupby('thn_ulasan').size().reset_index(name='jumlah_records')
    labels = df['thn_ulasan'].tolist()
    data_values = df['jumlah_records'].tolist()
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": f"Ulasan pertahun",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_data_rating_pertahun')
def chart_data_rating_pertahun():
    df = get_data_ulasan()    
    # Kelompokkan data berdasarkan tahun dan rating
    df = df.groupby(['thn_ulasan', 'rating']).size().reset_index(name='jumlah_records')
    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn_ulasan', columns='rating', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
        "rgba(154, 205, 50, 0.6)",  # Warna untuk rating 4
        "rgba(75, 192, 75, 0.6)"  # Warna untuk rating 5
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"Rating {category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            "borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

@app.route('/chart_reviewer')
def chart_reviewer():
    df = get_data_ulasan()
    # Menghitung distribusi True dan False
    data_count = df['localGuide'].value_counts()  # Kolom 'status' berisi True/False
    labels = data_count.index.tolist()       # ['True', 'False']
    data_values = data_count.values.tolist() # [count_true, count_false]
    # Siapkan data untuk Chart.js
    data = {
        "labels": labels,
        "datasets": [
            {
                "data": data_values,
                "backgroundColor": ["rgba(75, 192, 192, 0.6)", "rgba(255, 99, 132, 0.6)"],  # Warna untuk True dan False
                "hoverBackgroundColor": ["rgba(75, 192, 192, 0.8)", "rgba(255, 99, 132, 0.8)"],  # Warna hover
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_total_rating')
def chart_total_rating():
    df = get_data_ulasan()
    df = df.groupby('rating').size().reset_index(name='jumlah_records')
    # Urutkan rating dari 5 ke 1
    df = df.sort_values('rating', ascending=False)
    # Siapkan data untuk Chart.js
    labels = df['rating'].tolist()
    data_values = df['jumlah_records'].tolist()
    # Warna berdasarkan rating
    colors = {
        5: "rgba(75, 192, 75, 0.6)",      # Hijau
        4: "rgba(154, 205, 50, 0.6)",    # YellowGreen
        3: "rgba(255, 255, 0, 0.6)",     # Kuning
        2: "rgba(255, 165, 0, 0.6)",     # Oranye
        1: "rgba(255, 69, 0, 0.6)"       # Merah
    }
    background_colors = [colors[rating] for rating in labels]
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Jumlah Ulasan per Rating",
                "backgroundColor": background_colors,
                "borderColor": background_colors,
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_data_topik_ulasan_pertahun')
def chart_data_topik_ulasan_pertahun():
    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    df = df.groupby(['thn','predicted_topic']).size().reset_index(name='jumlah_records')
    
    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn', columns='predicted_topic', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
        "rgba(154, 205, 50, 0.6)",  # Warna untuk rating 4
        "rgba(75, 192, 75, 0.6)"  # Warna untuk rating 5
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"{category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            "borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

@app.route('/chart_data_sentimen_ulasan_pertahun')
def chart_data_sentimen_ulasan_pertahun():
    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    df = df.groupby(['thn','predicted_sentiment']).size().reset_index(name='jumlah_records')
    # print (df)
    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn', columns='predicted_sentiment', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"{category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            "borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

@app.route('/chart_sentimen_ulasan_filter',methods=(['GET','POST']))
def chart_sentimen_ulasan_filter():
    thn = request.args.get('thn')
    topik = request.args.get('topik')
    sentimen = request.args.get('sentimen')

    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    if (thn is not None) and (thn != 'semua'):
        thn = int(thn)
        df = df.query("thn == @thn")
    if (topik is not None) and (topik != 'semua'):
        df = df.query("predicted_topic == @topik")
    if (sentimen is not None) and (sentimen != 'semua'):
        df = df.query("predicted_sentiment == @sentimen")

    df = df.groupby('predicted_sentiment').size().reset_index(name='count')

    # Convert data to JSON
    data = {
        "labels": df['predicted_sentiment'].tolist(),
        "counts": df['count'].tolist()
    }    
    return jsonify(data)

@app.route('/chart_topik_ulasan_filter',methods=(['GET','POST']))
def chart_topik_ulasan_filter():
    thn = request.args.get('thn')
    topik = request.args.get('topik')
    sentimen = request.args.get('sentimen')

    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    if (thn is not None) and (thn != 'semua'):
        thn = int(thn)
        df = df.query("thn == @thn")
    if (topik is not None) and (topik != 'semua'):
        df = df.query("predicted_topic == @topik")
    if (sentimen is not None) and (sentimen != 'semua'):
        df = df.query("predicted_sentiment == @sentimen")

    df = df.groupby('predicted_topic').size().reset_index(name='count')

    # print(thn, topik, sentimen)
    
    # Convert data to JSON
    data = {
        "labels": df['predicted_topic'].tolist(),
        "counts": df['count'].tolist()
    }    
    return jsonify(data)

#----------------- Chart Pengaduan ---------------------#

@app.route('/chart_data_pengaduan_pertahun')
def chart_data_pengaduan_pertahun():
    df = get_data_pengaduan()
    df = df.groupby('thn_pengaduan').size().reset_index(name='jumlah_records')
    labels = df['thn_pengaduan'].tolist()
    data_values = df['jumlah_records'].tolist()
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": f"Pengaduan",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_data_pengaduan_perbulan')
def chart_data_pengaduan_perbulan():
    import calendar
    import pandas as pd
    
    current_date = date.today()
    thn = current_date.year
    
    df = get_data_pengaduan()
    df = df.query("thn_pengaduan == @thn")
    
    # Buat daftar semua bulan dalam setahun
    all_months = pd.DataFrame({'bln': range(1, 13)})
    
    # Hitung jumlah records per bulan
    df = df.groupby('bln').size().reset_index(name='jumlah_records')
    
    # Gabungkan dengan daftar semua bulan
    df = pd.merge(all_months, df, on='bln', how='left')
    
    # Isi nilai NaN dengan 0 untuk bulan yang tidak memiliki data
    df['jumlah_records'] = df['jumlah_records'].fillna(0)
    
    # Konversi nama bulan menjadi string (opsional)
    df['bln'] = df['bln'].apply(lambda x: calendar.month_name[x])
    
    labels = df['bln'].tolist()
    data_values = df['jumlah_records'].tolist()
    
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": f"Pengaduan",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)


@app.route('/chart_sumber_pengaduan')
def chart_sumber_pengaduan():
    df = get_data_pengaduan()
    df = df.groupby('sumber_pengaduan').size().reset_index(name='count')
    
    # Convert data to JSON
    data = {
        "labels": df['sumber_pengaduan'].tolist(),
        "counts": df['count'].tolist()
    }    
    return jsonify(data)

@app.route('/chart_data_topik_pengaduan_pertahun')
def chart_data_topik_pengaduan_pertahun():
    df = pd.read_csv(dataset['results_transformed_prediction_pengaduan'])
    df = df.groupby(['thn','predicted_topic']).size().reset_index(name='jumlah_records')
    
    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn', columns='predicted_topic', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
        "rgba(154, 205, 50, 0.6)",  # Warna untuk rating 4
        "rgba(75, 192, 75, 0.6)"  # Warna untuk rating 5
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"{category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            #"borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

@app.route('/chart_data_sumber_pengaduan_pertahun')
def chart_data_sumber_pengaduan_pertahun():
    df = get_data_pengaduan()
    df = df.groupby(['thn_pengaduan','sumber_pengaduan']).size().reset_index(name='jumlah_records')
    
    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn_pengaduan', columns='sumber_pengaduan', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
        "rgba(154, 205, 50, 0.6)",  # Warna untuk rating 4
        "rgba(75, 192, 75, 0.6)"  # Warna untuk rating 5
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"{category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            #"borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

@app.route('/chart_topik_pengaduan_filter',methods=(['GET','POST']))
def chart_topik_pengaduan_filter():
    thn = request.args.get('thn')
    topik = request.args.get('topik')
    # status = request.args.get('status')

    df = pd.read_csv(dataset['results_transformed_prediction_pengaduan'])
    if (thn is not None) and (thn != 'semua'):
        thn = int(thn)
        df = df.query("thn == @thn")
    if (topik is not None) and (topik != 'semua'):
        df = df.query("predicted_topic == @topik")
    
    df = df.groupby('predicted_topic').size().reset_index(name='count')

    # Convert data to JSON
    data = {
        "labels": df['predicted_topic'].tolist(),
        "counts": df['count'].tolist()
    }    
    return jsonify(data)


#------ Analisis Topik Ulasan

# bar chart
@app.route('/chart_topik_ulasan')
def chart_topik_ulasan():
    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    df = df.groupby('predicted_topic').size().reset_index(name='jumlah_records')
    labels = df['predicted_topic'].tolist()
    data_values = df['jumlah_records'].tolist()
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": f"Topik",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_komposisi_ulasan')
def chart_komposisi_ulasan():
    df = pd.read_csv(dataset['results_prediction_ulasan'])
    df = df.groupby('predicted_jenis').size().reset_index(name='jumlah_records')
    labels = df['predicted_jenis'].tolist()
    data_values = df['jumlah_records'].tolist()
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": f"Jenis",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "data": data_values,
            }
        ],
    }
    return jsonify(data)

@app.route('/chart_analisis_sentimen_ulasan_pertahun',methods=(['GET','POST']))
def chart_analisis_sentimen_ulasan_pertahun():
    topik = request.args.get('topik')
    df = pd.read_csv(dataset['results_transformed_prediction_ulasan'])
    if (topik is not None) and (topik != 'semua'):
        df = df.query("predicted_topic == @topik")
    df = df.groupby(['thn','predicted_sentiment']).size().reset_index(name='jumlah_records')

    # Pivot data untuk mempermudah proses
    pivot_data = df.pivot(index='thn', columns='predicted_sentiment', values='jumlah_records').fillna(0)
    # Siapkan data untuk Chart.js
    labels = pivot_data.index.tolist()  # Tahun sebagai label
    datasets = []
    colors = [
        "rgba(255, 69, 0, 0.6)",  # Warna untuk rating 1
        "rgba(255, 165, 0, 0.6)",  # Warna untuk rating 2
        "rgba(255, 255, 0, 0.6)",  # Warna untuk rating 3
    ]
    for i, category in enumerate(pivot_data.columns):
        datasets.append({
            "label": f"{category}",
            "data": pivot_data[category].tolist(),
            "fill": False,
            "borderColor": colors[i % len(colors)],  # Pilih warna secara berulang
            "tension": 0.1
        })
    data = {
        "labels": labels,
        "datasets": datasets
    }
    return jsonify(data)

##################################################### External Execute Batch
##############################################################################
#@app.route('/run_model')
#def run_model():
#    cmd = "python3"
#    subprocess.run([cmd,"persons.py"])
#    subprocess.run([cmd,"places.py"])
#    subprocess.run([cmd,"plot_wordcloud.py"])
#    subprocess.run([cmd,"cleaned_review_part02.py"])
#    subprocess.run([cmd ,"transform_review_prediction.py"])
#    return redirect(url_for('ulasan_lengkap'))

@app.route('/coba')
def coba():
    predict_ulasan()
    predict_pengaduan()
    #return 'berhasil'
    return redirect(url_for("index"))


##############################################################################
################################## MAIN PROGRAM ##############################

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
