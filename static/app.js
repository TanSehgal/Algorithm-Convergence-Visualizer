function updateInputs() {
    const method = document.getElementById("method").value;
    const container = document.getElementById("dynamicInputs");
    const fxField = document.getElementById("fxField");
    let html = "";

    if (method === "bisection" || method === "regula_falsi") {
        fxField.style.display = "flex";
        html += `
            <div class="field">
                <label for="a">Lower bound (a)</label>
                <input type="number" id="a" step="any" value="1">
            </div>
            <div class="field">
                <label for="b">Upper bound (b)</label>
                <input type="number" id="b" step="any" value="2">
            </div>`;
    } else if (method === "newton") {
        fxField.style.display = "flex";
        html += `
            <div class="field full">
                <label for="x0">Initial guess (x₀)</label>
                <input type="number" id="x0" step="any" value="1.5">
            </div>`;
    } else if (method === "secant") {
        fxField.style.display = "flex";
        html += `
            <div class="field">
                <label for="x0">Initial guess x₀</label>
                <input type="number" id="x0" step="any" value="1">
            </div>
            <div class="field">
                <label for="x1">Initial guess x₁</label>
                <input type="number" id="x1" step="any" value="2">
            </div>`;
    } else if (method === "fixed_point") {
        fxField.style.display = "none";
        html += `
            <div class="field full">
                <label for="g_function">Iteration function g(x)</label>
                <input type="text" id="g_function" placeholder="Example: (x + 2)**(1/3)" value="(x + 2)**(1/3)">
            </div>
            <div class="field full">
                <label for="x0">Initial guess (x₀)</label>
                <input type="number" id="x0" step="any" value="1.5">
            </div>`;
    }

    container.innerHTML = html;
}

function setStatus(state, text) {
    const badge = document.getElementById("statusBadge");
    badge.className = `status ${state}`;
    badge.textContent = text;
}

async function solveMethod() {
    const method = document.getElementById("method").value;
    const payload = {
        method: method,
        function: document.getElementById("function")?.value || "",
        tolerance: document.getElementById("tolerance").value,
        max_iter: document.getElementById("max_iter").value,
    };

    if (document.getElementById("a")) payload.a = document.getElementById("a").value;
    if (document.getElementById("b")) payload.b = document.getElementById("b").value;
    if (document.getElementById("x0")) payload.x0 = document.getElementById("x0").value;
    if (document.getElementById("x1")) payload.x1 = document.getElementById("x1").value;
    if (document.getElementById("g_function")) payload.g_function = document.getElementById("g_function").value;

    setStatus("idle", "Running");
    document.getElementById("result").innerHTML = "Calculating...";

    try {
        const response = await fetch("/solve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (result.error) {
            setStatus("error", "Error");
            document.getElementById("result").innerHTML = `Error: ${result.error}`;
            document.getElementById("tableContainer").innerHTML = "";
            Plotly.purge("plot");
            return;
        }

        setStatus("success", "Success");
        const iterations = result.iterations?.length || 0;
        document.getElementById("result").innerHTML = `
            <strong>Approximate Root:</strong> ${formatNumber(result.root)}<br>
            <strong>Total Iterations:</strong> ${iterations}
        `;

        createTable(result.iterations || []);
        createPlot(result.iterations || []);
    } catch (error) {
        setStatus("error", "Error");
        document.getElementById("result").innerHTML = `Error: ${error.message}`;
        document.getElementById("tableContainer").innerHTML = "";
        Plotly.purge("plot");
    }
}

function formatNumber(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "-";
    return Number(value).toFixed(8);
}

function createTable(data) {
    const container = document.getElementById("tableContainer");
    if (!data.length) {
        container.innerHTML = "<p>No iteration data available.</p>";
        return;
    }

    const keys = Object.keys(data[0]);
    let html = "<table><thead><tr>";
    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });
    html += "</tr></thead><tbody>";

    data.forEach(row => {
        html += "<tr>";
        keys.forEach(key => {
            const value = row[key];
            html += `<td>${typeof value === "number" ? formatNumber(value) : (value ?? "-")}</td>`;
        });
        html += "</tr>";
    });

    html += "</tbody></table>";
    container.innerHTML = html;
}

function createPlot(data) {
    if (!data.length) {
        Plotly.purge("plot");
        return;
    }

    const iterations = data.map(row => row.iter);
    const errors = data.map(row => row.error === null || row.error === undefined ? null : row.error);
    const approximations = data.map(row => {
        if (row.c !== undefined) return row.c;
        if (row.x_next !== undefined) return row.x_next;
        return null;
    });

    const errorTrace = {
        x: iterations,
        y: errors,
        mode: "lines+markers",
        name: "Error",
        hovertemplate: "Iteration %{x}<br>Error %{y:.8f}<extra></extra>",
        yaxis: "y1",
    };

    const approxTrace = {
        x: iterations,
        y: approximations,
        mode: "lines+markers",
        name: "Approximation",
        hovertemplate: "Iteration %{x}<br>Approx %{y:.8f}<extra></extra>",
        yaxis: "y2",
    };

    const layout = {
        title: "Convergence Behavior",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(255,255,255,0.02)",
        font: { color: "#e8f0ff" },
        xaxis: {
            title: "Iteration",
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.08)",
        },
        yaxis: {
            title: "Error",
            type: "log",
            autorange: true,
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.08)",
        },
        yaxis2: {
            title: "Approximation",
            overlaying: "y",
            side: "right",
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.08)",
        },
        legend: {
            orientation: "h",
            y: 1.12,
            x: 0,
        },
        margin: { l: 70, r: 70, t: 60, b: 60 },
    };

    Plotly.newPlot("plot", [errorTrace, approxTrace], layout, { responsive: true });
}

updateInputs();
