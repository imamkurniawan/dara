from dependecies import *

############################## Config Host ###################################
##############################################################################
HOSTNAME = 'https://rsud.mataramkota.go.id:5555'

def create_hostname():
    return 'https://rsud.mataramkota.go.id:5555'

def create_host():
    host = socket.gethostname()
    host = 'https://'+socket.gethostbyname(host)
    return host

COBA_HOST = create_host()

############################## Config Database MySQL #########################
##############################################################################
# Konfigurasi koneksi database
def create_engine_db():
    # menggunakan mysqlalchemy
    host = 'localhost'
    user = 'root'
    password = ''
    database_name = 'dara_db'
    
    # String koneksi database
    # DATABASE_URL = "mysql+pymysql://root:@localhost/dara_db"
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{database_name}"

    # Membuat engine SQLAlchemy
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Nonaktifkan connection pooling
        pool_recycle=3600,   # Refresh koneksi setiap 1 jam
        pool_pre_ping=True   # Cek koneksi sebelum digunakan
    )
    return engine

'''
def open_database_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Koneksi berhasil!")
    except Exception as e:
        print("Koneksi gagal:", e)
'''

engine = create_engine_db()
print(engine)
# with engine.connect() as connection:
#    print ('koneksi berhasil')


############################ Config Dataset ##################################
##############################################################################
dataset = {
    # File input
    'file_ulasan':'dataset/gmaps_review.xlsx',
    'file_pengaduan':'dataset/pengaduan.xlsx',
    'data_unit':'dataset/data_unit.xlsx',

    # File proses
    'daftar_person':'dataset/persons.txt',
    'daftar_place':'dataset/places.txt',
    'data_training':"dataset/training_data.xlsx",

    # File Hasil
    'results_persons_ulasan':'dataset/persons_ulasan_results.csv',
    'results_places_ulasan':'dataset/places_ulasan_results.csv',
    'results_persons_pengaduan':'dataset/persons_pengaduan_results.csv',
    'results_places_pengaduan':'dataset/places_pengaduan_results.csv',
    
    'results_cleaned_ulasan':'dataset/results_cleaned_ulasan.csv',
    'results_prediction_ulasan':'dataset/results_prediction_ulasan.csv',
    'results_group_prediction_ulasan':'dataset/results_group_prediction_ulasan.csv',
    'results_transformed_prediction_ulasan':'dataset/results_transformed_prediction_ulasan.csv',

    'results_cleaned_pengaduan':'dataset/results_cleaned_pengaduan.csv',
    'results_prediction_pengaduan':'dataset/results_prediction_pengaduan.csv',
    'results_group_prediction_pengaduan':'dataset/results_group_prediction_pengaduan.csv',
    'results_transformed_prediction_pengaduan':'dataset/results_transformed_prediction_pengaduan.csv',

    # file faq
    'file_faq':'dataset/faq.xlsx',

    # file log pengunjung
    'log_file':'dataset/pengunjung.csv'
}


############################ Config User ##################################
###########################################################################

# Fungsi untuk membaca data users
def get_data_users():
    # Membaca data menggunakan koneksi
    with engine.connect() as connection:
        query = text("SELECT * FROM users")
        df = pd.read_sql(query, connection)  
    return df

 
##################### Config API google maps reviews #########################
# Melakukan scrapping data ulasan google maps review menggunakan scrapingdog #
##############################################################################
def get_google_reviews(page_token=""):
    #api_key = "679cecbb3e5da8505e80ebb4" #imamkurniawan.ntb@gmail.com
    api_key = "68a29ff70ffa466114cb8648" #imamkurniawan.moba@gmail.com
    url = "https://api.scrapingdog.com/google_maps/reviews"
    data_id = "0x2dcdbf4240a7ae15:0x7c96adfc5edd7c11"
  
    params = {
        "api_key": api_key,
        "data_id": data_id,
        "language": "id",
        "sort_by" : "newestFirst",
        "next_page_token" : page_token
        #"next_page_token" : "CAESY0NBRVFDaHBFUTJwRlNVRlNTWEJEWjI5QlVEY3lSM1p4TW14bExWOWZSV2hEZUVGMGIwNTNYMEZLUWtveGVIaG1PRUZCUVVGQlIyZHVPVEl4UVVOaExYSmhWamMwV1VGRFNVRQ=="
    }
  
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return (data)
    else:
        return (f"Request failed with status code: {response.status_code}")

def get_google_reviews_json():
    data = get_google_reviews()
    return jsonify(data)

####################### End of Google reviews API config ####################### 