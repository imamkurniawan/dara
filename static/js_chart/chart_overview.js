async function fetchDataReview() {
    const response = await fetch('/chart_data_ulasan_pertahun');
    return await response.json();
}
async function createAnnualReviewChart() {
    const data = await fetchDataReview();
    const ctx = document.getElementById('my-Annual-Review-Chart').getContext('2d');
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

async function fetchDataRating() {
    const response = await fetch('/chart_data_rating_pertahun');
    return await response.json();
}
async function createAnnualRatingChart() {
    const data = await fetchDataRating();
    const ctx = document.getElementById('my-Annual-Rating-Chart').getContext('2d');
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

async function fetchDataLocalGuide() {
    const response = await fetch('/chart_reviewer');
    return await response.json();
}

async function createReviewerChart() {
const data = await fetchDataLocalGuide(); // Fungsi untuk mengambil data dari API
const ctx = document.getElementById('my-LocalGuide-Chart').getContext('2d');
// Hitung total data untuk persentase
const total = data.datasets[0].data.reduce((acc, value) => acc + value, 0);
// Tetapkan warna berdasarkan label
const colors = data.labels.map(label => {
    if (label === true) return "rgba(75, 192, 75, 0.6)"; // Hijau untuk True
    if (label === false) return "rgba(255, 99, 132, 0.6)"; // Merah untuk False
    return "rgba(150, 150, 150, 0.6)"; // Default warna abu-abu
});
// Tetapkan warna hover
const hoverColors = data.labels.map(label => {
    if (label === true) return "rgba(75, 192, 75, 0.8)"; // Hijau lebih gelap untuk hover
    if (label === false) return "rgba(255, 99, 132, 0.8)"; // Merah lebih gelap untuk hover
    return "rgba(150, 150, 150, 0.8)"; // Default warna hover abu-abu
});
new Chart(ctx, {
    type: 'doughnut', // Tipe grafik donut
    data: {
        ...data,
        datasets: [{
            ...data.datasets[0],
            backgroundColor: colors, // Warna dasar
            hoverBackgroundColor: hoverColors, // Warna saat hover
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom' // Posisi legenda
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const label = context.label || ''; // Label kategori
                        const value = context.raw || 0; // Nilai mentah
                        const percentage = ((value / total) * 100).toFixed(2); // Hitung persentase
                        return `${label}: ${value} (${percentage}%)`; // Label + Persentase
                    }
                }
            }
        },
        cutout: '70%', // Atur diameter lubang di tengah
    }
  });
}

async function fetchTotalRatingsData() {
    const response = await fetch('/chart_total_rating');
    return await response.json();
}

async function createTotalRatingChart() {
    const data = await fetchTotalRatingsData();
    const ctx = document.getElementById('my-Total-Rating-Chart').getContext('2d');

    new Chart(ctx, {
        type: 'bar', // Jenis grafik bar
        data: data,
        options: {
            indexAxis: 'y', // Membuat grafik horizontal
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                    position: 'top',
                },
            },
            scales: {
                x: {
                    beginAtZero: true, // Sumbu x mulai dari nol
                    title: {
                        display: true,
                        text: 'Jumlah Ulasan',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Rating',
                    },
                },
            },
        },
    });
}

async function fetchAnnualReviewTopic() {
    const response = await fetch('/chart_data_topik_ulasan_pertahun');
    return await response.json();
}

async function createAnnualTopicReviewChart() {
    const data = await fetchAnnualReviewTopic()

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

    const ctx = document.getElementById('my-Annual-Review-Topic-Chart').getContext('2d');
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
                    position: 'top',
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


async function fetchDataSentiment() {
    const response = await fetch('/chart_data_sentimen_ulasan_pertahun');
    return await response.json();
}

async function createAnnualSentimentChart() {
    const data = await fetchDataSentiment();

    // Tambahkan warna berdasarkan rating
    const colors = [
        "rgba(92, 93, 92, 0.6)",       // Warna untuk sentimen netral (biasa)
        "rgba(247, 6, 6, 0.6)",       // Warna untuk sentimen negatif
        "rgba(2, 106, 28, 0.6)",      // Warna untuk sentimen positif
    ];

    const datasets = data.datasets.map((dataset, index) => {
        const color = colors[index % colors.length];
        return {
            ...dataset,
            backgroundColor: color,       // Warna area di bawah line
            borderColor: color,           // Warna garis line
            pointBackgroundColor: color,  // Warna titik pada grafik
            pointBorderColor: color,      // Warna border titik
        };
    });

    const ctx = document.getElementById('my-Annual-Sentiment-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
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


createTotalRatingChart();
createReviewerChart();
createAnnualReviewChart();
createAnnualRatingChart();
createAnnualTopicReviewChart()
createAnnualSentimentChart()

// chart pengaduan
fetch('/chart_sumber_pengaduan')
      .then(response => response.json())
      .then(data => {
          const ctx = document.getElementById('sumber-Pengaduan-Chart').getContext('2d');
          new Chart(ctx, {
              type: 'doughnut',
              data: {
                  labels: data.labels,
                  datasets: [{
                      label: 'Jumlah Pengaduan',
                      data: data.counts,
                      
                      borderWidth: 1
                  }]
              },
              options: {
                  responsive: true,
                  plugins: {
                      legend: {
                          position: 'right',
                      },
                      tooltip: {
                          enabled: true
                      }
                  }
              }
          });
      })
      .catch(error => console.error('Error fetching data:', error));


fetch('/chart_topik_pengaduan_filter')
      .then(response => response.json())
      .then(data => {
          const ctx = document.getElementById('topik-Pengaduan-Chart').getContext('2d');
          new Chart(ctx, {
              type: 'doughnut',
              data: {
                  labels: data.labels,
                  datasets: [{
                      label: 'Jumlah Pengaduan',
                      data: data.counts,
                      
                      borderWidth: 1
                  }]
              },
              options: {
                  responsive: true,
                  plugins: {
                      legend: {
                          position: 'right',
                      },
                      tooltip: {
                          enabled: true
                      }
                  }
              }
          });
      })
      .catch(error => console.error('Error fetching data:', error));