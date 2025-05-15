async function fetchDataReview() {
    const response = await fetch('/chart_topik_ulasan');
    return await response.json();
}

async function createTopicChart() {
    const data = await fetchDataReview();

    // Tambahkan warna berdasarkan topik
    const colors = [
        "rgba(3, 247, 52, 0.6)",       // Warna untuk topik administrasi
        "rgba(247, 162, 6, 0.6)",     // Warna untuk topik fasilitas
        "rgba(255, 0, 144, 0.6)",     // Warna untuk topik komunikasi
        "rgba(25, 0, 255, 0.6)",      // Warna untuk topik pelayanan
        "rgba(50, 50, 50, 0.6)"       // Warna untuk topik umum
    ];

    // Mengatur warna berdasarkan indeks label
    const backgroundColors = data.labels.map((_, index) => colors[index % colors.length]);

    const updatedDatasets = data.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: backgroundColors, // Assign warna unik ke setiap bar
        borderColor: backgroundColors.map(color => color.replace("0.6", "1")), // Border dengan opacity 1
    }));

    const ctx = document.getElementById('my-Topic-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar', // jenis grafik: bar, line, pie, dll.
        data: {
            labels: data.labels,
            datasets: updatedDatasets,
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                }
            },
            plugins: {
                legend: {
                    display: false, // Menampilkan legenda
                },
            },
        }
    });
}

async function fetchKomposisiUlasan() {
    const response = await fetch('/chart_komposisi_ulasan');
    return await response.json();
}
async function createKomposisiChart() {
    const data = await fetchKomposisiUlasan();
    const ctx = document.getElementById('my-Komposisi-Chart').getContext('2d');
    new Chart(ctx, {
        type: 'radar', // jenis grafik: bar, line, pie, dll.
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false, // Menampilkan legenda
                },
            },
            scales: {
                r: {
                    ticks: {
                        display: false
                    }
                }
            }
        }
    });
}

async function fetchDataTopic() {
    const response = await fetch('/chart_data_topik_ulasan_pertahun');
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

// sentimen
async function fetchDataSentiment() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun');
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
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                }
            }
        }
    });
}


createTopicChart();
createKomposisiChart();
createAnnualTopicChart();
createAnnualSentimentChart();

// sentimen
async function fetchDataSentimentPelayanan() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun?topik=pelayanan');
    return await response.json();
}

async function createAnnualSentimentChartPelayanan() {
    const data = await fetchDataSentimentPelayanan();

    // Warna berdasarkan label
    const colorsMap = {
        positif: "rgba(2, 106, 28, 0.6)",   // Hijau untuk positif
        negatif: "rgba(247, 6, 6, 0.6)",   // Merah untuk negatif
        biasa: "rgba(92, 93, 92, 0.6)"     // Abu untuk netral/biasa
    };

    // Map dataset dengan warna yang sesuai
    const datasets = data.datasets.map(dataset => {
        const color = colorsMap[dataset.label.toLowerCase()] || "rgba(128, 128, 128, 0.6)"; // Default warna abu
        return {
            ...dataset,
            backgroundColor: color,         // Warna area fill
            borderColor: color,            // Warna garis
            pointBackgroundColor: color,   // Warna poin
            pointBorderColor: color        // Warna border poin
        };
    });

    const ctx = document.getElementById('my-Annual-Sentiment-Chart-Pelayanan').getContext('2d');
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
                    stacked: false
                },
                y: {
                    stacked: false,
                    max: 120,
                    beginAtZero: true,
                }
            }
        }
    });
}

createAnnualSentimentChartPelayanan();

// sentimen fasilitas
async function fetchDataSentimentFasilitas() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun?topik=fasilitas');
    return await response.json();
}

async function createAnnualSentimentChartFasilitas() {
    const data = await fetchDataSentimentFasilitas();

    // Warna berdasarkan label
    const colorsMap = {
        positif: "rgba(2, 106, 28, 0.6)",   // Hijau untuk positif
        negatif: "rgba(247, 6, 6, 0.6)",   // Merah untuk negatif
        biasa: "rgba(92, 93, 92, 0.6)"     // Abu untuk netral/biasa
    };

    // Map dataset dengan warna yang sesuai
    const datasets = data.datasets.map(dataset => {
        const color = colorsMap[dataset.label.toLowerCase()] || "rgba(128, 128, 128, 0.6)"; // Default warna abu
        return {
            ...dataset,
            backgroundColor: color,         // Warna area fill
            borderColor: color,            // Warna garis
            pointBackgroundColor: color,   // Warna poin
            pointBorderColor: color        // Warna border poin
        };
    });

    const ctx = document.getElementById('my-Annual-Sentiment-Chart-Fasilitas').getContext('2d');
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
                    stacked: false
                },
                y: {
                    stacked: false,
                    max: 120,
                    beginAtZero: true,
                }
            }
        }
    });
}

createAnnualSentimentChartFasilitas();

// sentimen Administrasi
async function fetchDataSentimentAdministrasi() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun?topik=administrasi');
    return await response.json();
}

async function createAnnualSentimentChartAdministrasi() {
    const data = await fetchDataSentimentAdministrasi();

    // Warna berdasarkan label
    const colorsMap = {
        positif: "rgba(2, 106, 28, 0.6)",   // Hijau untuk positif
        negatif: "rgba(247, 6, 6, 0.6)",   // Merah untuk negatif
        biasa: "rgba(92, 93, 92, 0.6)"     // Abu untuk netral/biasa
    };

    // Map dataset dengan warna yang sesuai
    const datasets = data.datasets.map(dataset => {
        const color = colorsMap[dataset.label.toLowerCase()] || "rgba(128, 128, 128, 0.6)"; // Default warna abu
        return {
            ...dataset,
            backgroundColor: color,         // Warna area fill
            borderColor: color,            // Warna garis
            pointBackgroundColor: color,   // Warna poin
            pointBorderColor: color        // Warna border poin
        };
    });

    const ctx = document.getElementById('my-Annual-Sentiment-Chart-Administrasi').getContext('2d');
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
                    stacked: false
                },
                y: {
                    stacked: false,
                    max: 120,
                    beginAtZero: true,
                }
            }
        }
    });
}

createAnnualSentimentChartAdministrasi();

// Fungsi untuk mengambil data sentimen komunikasi
async function fetchDataSentimentKomunikasi() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun?topik=komunikasi');
    return await response.json();
}

// Fungsi untuk membuat chart sentimen tahunan
async function createAnnualSentimentChartKomunikasi() {
    const data = await fetchDataSentimentKomunikasi();

    // Warna berdasarkan label
    const colorsMap = {
        positif: "rgba(2, 106, 28, 0.6)",   // Hijau untuk positif
        negatif: "rgba(247, 6, 6, 0.6)",   // Merah untuk negatif
        biasa: "rgba(92, 93, 92, 0.6)"     // Abu untuk netral/biasa
    };

    // Map dataset dengan warna yang sesuai
    const datasets = data.datasets.map(dataset => {
        const color = colorsMap[dataset.label.toLowerCase()] || "rgba(128, 128, 128, 0.6)"; // Default warna abu
        return {
            ...dataset,
            backgroundColor: color,         // Warna area fill
            borderColor: color,            // Warna garis
            pointBackgroundColor: color,   // Warna poin
            pointBorderColor: color        // Warna border poin
        };
    });

    // Buat chart menggunakan Chart.js
    const ctx = document.getElementById('my-Annual-Sentiment-Chart-Komunikasi').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels, // Label untuk sumbu x
            datasets: datasets  // Dataset dengan warna yang telah disesuaikan
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
                    stacked: false
                },
                y: {
                    stacked: false,
                    max: 120,
                    beginAtZero: true,
                }
            }
        }
    });
}

// Panggil fungsi untuk membuat chart
createAnnualSentimentChartKomunikasi();



// sentimen Umum
async function fetchDataSentimentUmum() {
    const response = await fetch('/chart_analisis_sentimen_ulasan_pertahun?topik=umum');
    return await response.json();
}

async function createAnnualSentimentChartUmum() {
    const data = await fetchDataSentimentUmum();

    // Warna berdasarkan label
    const colorsMap = {
        positif: "rgba(2, 106, 28, 0.6)",   // Hijau untuk positif
        negatif: "rgba(247, 6, 6, 0.6)",   // Merah untuk negatif
        biasa: "rgba(92, 93, 92, 0.6)"     // Abu untuk netral/biasa
    };

    // Map dataset dengan warna yang sesuai
    const datasets = data.datasets.map(dataset => {
        const color = colorsMap[dataset.label.toLowerCase()] || "rgba(128, 128, 128, 0.6)"; // Default warna abu
        return {
            ...dataset,
            backgroundColor: color,         // Warna area fill
            borderColor: color,            // Warna garis
            pointBackgroundColor: color,   // Warna poin
            pointBorderColor: color        // Warna border poin
        };
    });

    const ctx = document.getElementById('my-Annual-Sentiment-Chart-Umum').getContext('2d');
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
                    stacked: false
                },
                y: {
                    stacked: false,
                    max: 120,
                    beginAtZero: true,
                }
            }
        }
    });
}

createAnnualSentimentChartUmum();


// Grafik sentimen  total
async function fetchDataSentimentTotal() {  

    try {
      const response = await fetch('/chart_sentimen_ulasan_filter');
      const rawData = await response.json();

      // Format data untuk Chart.js
      return {
        labels: rawData.labels, // Label dari API
        datasets: [{
          label: 'Sentimen Ulasan',
          data: rawData.counts, // Nilai dari API
          backgroundColor: rawData.labels.map(label => {
            if (label === "biasa") return 'grey';
            if (label === "negatif") return 'red';
            if (label === "positif") return 'green';
          }),
          borderColor: rawData.labels.map(label => {
            if (label === "biasa") return 'darkgrey';
            if (label === "negatif") return 'darkred';
            if (label === "positif") return 'darkgreen';
          }),
          borderWidth: 1
        }]
      };
    } catch (error) {
      console.error("Error fetching data:", error);
      return null;
    }
  }

  async function createSentimentTotalChart() {
    const data = await fetchDataSentimentTotal();
    if (!data) {
      console.error("No data available for the chart.");
      return;
    }

    const ctx = document.getElementById('my-Sentiment-Total-Review-Chart').getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'right',
          },
          tooltip: {
            callbacks: {
              label: function(tooltipItem) {
                const label = tooltipItem.label || '';
                const value = tooltipItem.raw || 0;
                return `${label}: ${value}`;
              }
            }
          }
        },
        cutout:'70%'
      }
    });
  }  
  // Panggil fungsi untuk membuat grafik
  createSentimentTotalChart();