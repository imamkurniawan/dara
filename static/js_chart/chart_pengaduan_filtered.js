fetch(url_topik)
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