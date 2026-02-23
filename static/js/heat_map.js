async function plotHeatmap() {
    const loadingIndicator = document.getElementById("loading-indicator");

    loadingIndicator.classList.remove("d-none");

    try {
        const res = await fetch("/api/task5_heatmap", { cache: "no-store" });
        if (!res.ok) {
            throw new Error("API error: " + res.status);
        }

        const data = await res.json();

        const traits = data.traits || [];
        const genres = (data.genres || []).map(g => String(g).trim());
        const z = data.z || [];
        const n = data.n || [];

        if (!traits.length || !genres.length || !z.length) {
            loadingIndicator.classList.add("d-none");
            return;
        }

        // Auto-scale color range around 0 to make differences more visible
        let minV = Infinity;
        let maxV = -Infinity;
        for (let i = 0; i < z.length; i++) {
            for (let j = 0; j < z[i].length; j++) {
                const v = z[i][j];
                if (v === null || v === undefined) continue;
                const num = Number(v);
                if (!Number.isFinite(num)) continue;
                if (num < minV) minV = num;
                if (num > maxV) maxV = num;
            }
        }
        const absMax = Math.max(Math.abs(minV), Math.abs(maxV)) || 1e-6;

        const hoverText = traits.map((t, i) =>
            genres.map((g, j) => {
                const corr = z?.[i]?.[j];
                const nn = n?.[i]?.[j] ?? 0;
                const c = (corr === null || corr === undefined) ? "NULL" : Number(corr).toFixed(4);
                return `Trait: ${t}<br>Genre: ${g}<br>corr: ${c}<br>n: ${nn}`;
            })
        );

        const trace = {
            type: "heatmap",
            x: genres,
            y: traits,
            z: z,
            text: hoverText,
            hoverinfo: "text",
            zmin: -absMax,
            zmax: absMax,
            zmid: 0,
            colorscale: "RdBu",
            showscale: true
        };

        const layout = {
            margin: { l: 140, r: 30, t: 10, b: 160 },
            xaxis: { tickangle: -45 },
            yaxis: { automargin: true }
        };

        await Plotly.newPlot("heatmap", [trace], layout, { responsive: true });

        loadingIndicator.classList.add("d-none");
    } catch (e) {
        console.error(e);
        loadingIndicator.classList.add("d-none");
    }
}