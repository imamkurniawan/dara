// ulasan
async function fetchDataReview() {
    const response = await fetch('/chart_data_pengaduan_pertahun');
    return await response.json();
}
async function createAnnualPengaduanChart() {
    const data = await fetchDataReview();
    const ctx = document.getElementById('my-Annual-Pengaduan-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'line', // jenis grafik: bar, line, pie, dll.
        data: data,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

// pengaduan perbulan
async function fetchDataPengaduanPerbulan() {
    const response = await fetch('/chart_data_pengaduan_perbulan');
    return await response.json();
}
async function createMonthlyPengaduanChart() {
    const data = await fetchDataPengaduanPerbulan();
    const ctx = document.getElementById('my-Monthly-Pengaduan-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar', // jenis grafik: bar, line, pie, dll.
        data: data,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

// Rating
async function fetchDataRating() {
    const response = await fetch('/chart_data_rating_pertahun');
    return await response.json();
}

async function createAnnualRatingChart() {
    const data = await fetchDataRating();

    // Tambahkan warna berdasarkan rating
    const colors = [
        "rgba(255, 69, 0, 0.6)",       // Warna untuk rating 1 (red)
        "rgba(255, 165, 0, 0.6)",     // Warna untuk rating 2 (orange)
        "rgba(255, 255, 0, 0.6)",     // Warna untuk rating 3 (yellow)
        "rgba(154, 205, 50, 0.6)",    // Warna untuk rating 4 (yellowgreen)
        "rgba(75, 192, 75, 0.6)"      // Warna untuk rating 5 (green)
    ];

    const datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: colors[index % colors.length] // Warna bar berdasarkan urutan dataset
    }));

    const ctx = document.getElementById('my-Annual-Rating-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels, // Label sumbu x (misalnya tahun)
            datasets: datasets  // Dataset dengan warna
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

// topik
async function fetchDataTopic() {
    const response = await fetch('/chart_data_topik_pengaduan_pertahun');
    return await response.json();
}

async function createAnnualTopicChart() {
    const data = await fetchDataTopic();

    // Tambahkan warna berdasarkan rating
    const colors = [
        "rgba(3, 247, 52, 0.6)",       // Warna untuk topik administrasi
        "rgba(247, 162, 6, 0.6)",     // Warna untuk topik fasilitas
        "rgba(255, 0, 144, 0.6)",     // Warna untuk topik komunikasi
        "rgba(25, 0, 255, 0.6)",      // Warna untuk topik pelayanan
        "rgba(50, 50, 50, 0.6)"       // Warna untuk topik umum
    ];

    const datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: colors[index % colors.length] // Warna bar berdasarkan urutan dataset
    }));

    const ctx = document.getElementById('my-Annual-Topic-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels, // Label sumbu x (misalnya tahun)
            datasets: datasets  // Dataset dengan warna
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                }
            },
            scales: {
                x: {
                    stacked: true // Mengaktifkan mode stacked pada sumbu x
                },
                y: {
                    stacked: true, // Mengaktifkan mode stacked pada sumbu y
                    beginAtZero: true
                }
            }
        }
    });
}

// sumber pengaduan
async function fetchDataSumber() {
    const response = await fetch('/chart_data_sumber_pengaduan_pertahun');
    return await response.json();
}

async function createAnnualSumberChart() {
    const data = await fetchDataSumber();

    // Tambahkan warna berdasarkan rating
    const colors = [
        "rgba(3, 247, 52, 0.6)",       // Warna untuk topik administrasi
        "rgba(247, 162, 6, 0.6)",     // Warna untuk topik fasilitas
        "rgba(255, 0, 144, 0.6)",     // Warna untuk topik komunikasi
        "rgba(25, 0, 255, 0.6)",      // Warna untuk topik pelayanan
        "rgba(50, 50, 50, 0.6)"       // Warna untuk topik umum
    ];

    const datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        //backgroundColor: colors[index % colors.length] // Warna bar berdasarkan urutan dataset
    }));

    const ctx = document.getElementById('my-Annual-Sumber-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels, // Label sumbu x (misalnya tahun)
            datasets: datasets  // Dataset dengan warna
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                }
            },
            scales: {
                x: {
                    stacked: false // Mengaktifkan mode stacked pada sumbu x
                },
                y: {
                    stacked: false, // Mengaktifkan mode stacked pada sumbu y
                    beginAtZero: true
                }
            }
        }
    });
}

// sentimen
async function fetchDataSentiment() {
    const response = await fetch('/chart_data_sentimen_ulasan_pertahun');
    return await response.json();
}

async function createAnnualSentimentChart() {
    const data = await fetchDataSentiment();

    // Tambahkan warna berdasarkan rating
    const colors = [
        "rgba(92, 93, 92, 0.6)",       // Warna untuk sentimen netral (biasa)
        "rgba(247, 6, 6, 0.6)",     // Warna untuk sentimen negatif
        "rgba(2, 106, 28, 0.6)",     // Warna untuk sentimen positif
    ];

    const datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: colors[index % colors.length] // Warna bar berdasarkan urutan dataset
    }));

    const ctx = document.getElementById('my-Annual-Sentiment-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels, // Label sumbu x (misalnya tahun)
            datasets: datasets  // Dataset dengan warna
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    // stacked: true
                },
                y: {
                    // stacked: true,
                    beginAtZero: true,
                }
            }
        }
    });
}

createAnnualPengaduanChart()
createMonthlyPengaduanChart()
// createAnnualRatingChart()
createAnnualTopicChart()
createAnnualSumberChart()
//createAnnualSentimentChart()