
// Grafik sentimen
async function fetchDataSentiment() {  

    try {
      const response = await fetch(url_sentimen);
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

  async function createSentimentChart() {
    const data = await fetchDataSentiment();
    if (!data) {
      console.error("No data available for the chart.");
      return;
    }

    const ctx = document.getElementById('my-Sentiment-Review-Chart').getContext('2d');
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
  createSentimentChart();

    // Grafik Topik
    async function fetchChartData() {    
    try {
      const response = await fetch(url_topik);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const rawData = await response.json();
      console.log('Data fetched:', rawData);
      return rawData;
    } catch (error) {
      console.error('Error fetching chart data:', error);
      return null;
    }
  }

async function createTopicChart() {
  const data = await fetchChartData();
  if (!data) {
    console.error('No data available to render the chart.');
    return;
  }

  const ctx = document.getElementById('my-Topic-Chart').getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Jumlah Ulasan per Topik',
        data: data.counts,
        backgroundColor: data.labels.map(label => {
          if (label === "administrasi") return 'blue';
          if (label === "fasilitas") return 'purple';
          if (label === "komunikasi") return 'orange';
          if (label === "pelayanan") return 'green';
          if (label === "umum") return 'grey';
          return 'lightgrey';
        }),
        borderColor: data.labels.map(label => {
          if (label === "administrasi") return 'darkblue';
          if (label === "fasilitas") return 'darkpurple';
          if (label === "komunikasi") return 'darkorange';
          if (label === "pelayanan") return 'darkgreen';
          if (label === "umum") return 'darkgrey';
          return 'darkgrey';
        }),
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

createTopicChart();