const API_BASE = "https://stock-dashboard-api.onrender.com";

let chart = null;

// Load companies
fetch(`${API_BASE}/companies`)
  .then(res => res.json())
  .then(companies => {
    const list = document.getElementById("company-list");

    companies.forEach(symbol => {
      const btn = document.createElement("button");
      btn.textContent = symbol;
      btn.className = `
        w-full text-left px-4 py-2 rounded-lg
        hover:bg-indigo-100 transition font-medium
      `;
      btn.onclick = () => loadStock(symbol);
      list.appendChild(btn);
    });
  });

function loadStock(symbol) {
  document.getElementById("title").innerText = `${symbol} Overview`;

  // Fetch stock data
  fetch(`${API_BASE}/data/${symbol}`)
    .then(res => res.json())
    .then(data => {
      const dates = data.map(d => d.date);
      const closes = data.map(d => d.close);
      const ma7 = data.map(d => d.ma_7);

      // Update stats
      document.getElementById("high52").innerText =
        Math.max(...closes).toFixed(2);

      document.getElementById("low52").innerText =
        Math.min(...closes).toFixed(2);

      const vols = data.map(d => d.volatility).filter(v => v !== null);
      document.getElementById("volatility").innerText =
        vols.length ? vols[vols.length - 1].toFixed(4) : "—";

      // Chart
      if (chart) chart.destroy();

      const ctx = document.getElementById("priceChart").getContext("2d");
      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: dates,
          datasets: [
            {
              label: "Close Price",
              data: closes,
              borderWidth: 2,
              tension: 0.3
            },
            {
              label: "7-Day MA",
              data: ma7,
              borderDash: [6, 6],
              borderWidth: 2,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top"
            }
          }
        }
      });
    });
}
