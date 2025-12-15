const API_BASE = "https://stock-dashboard-kkpr.onrender.com";
let activeRangeBtn = null;
let chart = null;
let currentSymbol = null;

// Load companies
fetch(`${API_BASE}/companies`)
  .then(res => res.json())
  .then(companies => {
    populateCompareDropdowns(companies);

    const list = document.getElementById("company-list");

    companies.forEach((symbol, idx) => {
      const btn = document.createElement("button");
      btn.textContent = symbol;
      btn.className =
        "w-full text-left px-4 py-2 rounded-lg hover:bg-indigo-100";

      btn.onclick = () => loadStock(symbol, 30);
      list.appendChild(btn);

      // AUTO LOAD FIRST STOCK
      if (idx === 0) {
        loadStock(symbol, 30);
      }
    });
  });


function reload(days) {
  if (currentSymbol) loadStock(currentSymbol, days);
}

function loadStock(symbol, days = 30) {
  currentSymbol = symbol;
  document.getElementById("title").innerText = `${symbol} Overview`;

  fetch(`${API_BASE}/data/${symbol}?days=${days}`)
    .then(res => res.json())
    .then(data => {
      const dates = data.map(d => d.date);
      const closes = data.map(d => d.close);
      const ma7 = data.map(d => d.ma_7);

      document.getElementById("high52").innerText =
        Math.max(...closes).toFixed(2);

      document.getElementById("low52").innerText =
        Math.min(...closes).toFixed(2);

      const vols = data.map(d => d.volatility).filter(v => v !== null);
      document.getElementById("volatility").innerText =
        vols.length ? vols.at(-1).toFixed(4) : "—";

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
            legend: { position: "top" }
          }
        }
      });

      // ✅ Enable range buttons AFTER data loads
      document.querySelectorAll(".range-btn").forEach(b => {
        b.disabled = false;
        b.classList.remove("opacity-50");
      });
    });
}


function compareStocks() {
  const s1 = document.getElementById("compare1").value;
  const s2 = document.getElementById("compare2").value;

  if (!s1 || !s2 || s1 === s2) {
    alert("Select two different stocks");
    return;
  }

  const modal = document.getElementById("compare-modal");
  const result = document.getElementById("compare-result");
  const windowText = document.getElementById("compare-window");

  modal.classList.remove("hidden");
  result.innerHTML = "Loading comparison...";
  windowText.innerText = "";

  fetch(`${API_BASE}/compare?symbol1=${s1}&symbol2=${s2}`)
    .then(res => res.json())
    .then(data => {
      if (!data[s1] || !data[s2]) {
        throw new Error("Invalid compare response");
      }

      const d1 = data[s1];
      const d2 = data[s2];

      const pct1 = (d1.return * 100).toFixed(2);
      const pct2 = (d2.return * 100).toFixed(2);

      windowText.innerText = `Comparison Window: ${data.comparison_window}`;

      result.innerHTML = `
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-semibold mb-2">${s1}</h4>
          <p>Start Price: <b>${d1.start_close.toFixed(2)}</b></p>
          <p>End Price: <b>${d1.end_close.toFixed(2)}</b></p>
          <p class="mt-1">
            Return:
            <span class="font-bold text-emerald-600">
              ${pct1}%
            </span>
          </p>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-semibold mb-2">${s2}</h4>
          <p>Start Price: <b>${d2.start_close.toFixed(2)}</b></p>
          <p>End Price: <b>${d2.end_close.toFixed(2)}</b></p>
          <p class="mt-1">
            Return:
            <span class="font-bold text-emerald-600">
              ${pct2}%
            </span>
          </p>
        </div>
      `;
    })
    .catch(err => {
      console.error(err);
      result.innerHTML =
        "<p class='text-red-500'>Comparison data unavailable</p>";
    });
}

function closeCompareModal() {
  document.getElementById("compare-modal").classList.add("hidden");
}

function populateCompareDropdowns(companies) {
  const c1 = document.getElementById("compare1");
  const c2 = document.getElementById("compare2");

  companies.forEach(s => {
    c1.innerHTML += `<option value="${s}">${s}</option>`;
    c2.innerHTML += `<option value="${s}">${s}</option>`;
  });
}

function setRange(btn, days) {
  document.querySelectorAll(".range-btn").forEach(b =>
    b.classList.remove("bg-indigo-600", "text-white")
  );

  btn.classList.add("bg-indigo-600", "text-white");
  reload(days);
}
