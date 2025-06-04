from dependecies import *

# fungsi ubah date menjadi durasi (cth: '3 hari yang lalu, seminggu yg lalu,') 
def humanize_date(date):
    return arrow.get(date).humanize(locale='id')  # Bahasa Indonesia

# Fungsi higlight word (untup person dan place) 
# @app.template_filter('highlight_replace')
def highlight_replace(text, word):
    text = text.lower()
    return text.replace(word, f"<span class='white_color blue1_bg'>&nbsp;{word}&nbsp;</span>")
# Registrasi filter
# app.jinja_env.filters['highlight_replace'] = highlight_replace

# Fungsi ambil nama bulan
def get_month_name(bln):
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    if 1 <= bln <= 12:
        return months[bln - 1]
    else:
        return ""
