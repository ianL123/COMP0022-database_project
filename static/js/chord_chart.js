// ===== Continuous Gradient Warp (3 control knots) =====
// t1/t2/t3 control where u=0.25/0.50/0.75 happens along score axis
let currentKnots = [0.25, 0.50, 0.75];

// warpScale: score (0..1) -> u (0..1) continuous, piecewise linear
let warpScale = null;

function normalizeAndSortKnots(arr) {
    let t = arr.map(x => Math.max(0, Math.min(0.99, +x))).sort((a, b) => a - b);

    const eps = 0.01;
    for (let i = 1; i < t.length; i++) {
        if (t[i] <= t[i - 1]) {
            t[i] = Math.min(0.99, t[i - 1] + eps);
        }
    }

    t[2] = Math.min(t[2], 0.99);
    return t;
}

function rebuildWarpScale() {
    warpScale = d3.scaleLinear()
        .domain([0, currentKnots[0], currentKnots[1], currentKnots[2], 1])
        .range([0, 0.25, 0.50, 0.75, 1])
        .clamp(true);
}

function colorOfScore(score) {
    const u = warpScale(score);
    return d3.interpolateYlGnBu(u);
}

function bindKnotTuner(scoreMatrix) {
    const ids = ["t1", "t2", "t3"];
    const valIds = ["t1Val", "t2Val", "t3Val"];

    const inputs = ids.map(id => document.getElementById(id));
    const labels = valIds.map(id => document.getElementById(id));

    if (inputs.some(x => !x) || labels.some(x => !x)) {
        return;
    }

    function syncUI(knots) {
        knots.forEach((v, i) => {
            inputs[i].value = v.toFixed(2);
            labels[i].textContent = v.toFixed(2);
        });
    }

    function update() {
        const raw = inputs.map(x => parseFloat(x.value));
        currentKnots = normalizeAndSortKnots(raw);
        syncUI(currentKnots);
        rebuildWarpScale();

        d3.select("#chord-chart")
            .selectAll(".chord-ribbon")
            .transition()
            .duration(120)
            .attr("fill", d => {
                const s = scoreMatrix[d.source.index][d.target.index];
                return colorOfScore(s);
            })
            .attr("stroke", d => {
                const s = scoreMatrix[d.source.index][d.target.index];
                return s > currentKnots[1]
                    ? d3.rgb(colorOfScore(s)).darker()
                    : "none";
            })
            .attr("fill-opacity", d => {
                const s = scoreMatrix[d.source.index][d.target.index];
                const u = warpScale(s);
                return d3.scalePow()
                    .exponent(2)
                    .domain([0, 1])
                    .range([0.1, 0.85])(u);
            });
    }

    syncUI(currentKnots);
    inputs.forEach(inp => inp.addEventListener("input", update));
}

// ===== Tooltip helpers (shared by arc + ribbon) =====
function ensureTooltipEl() {
    let el = document.getElementById("genre-tooltip");
    if (el) {
        return el;
    }

    el = document.createElement("div");
    el.id = "genre-tooltip";
    el.style.position = "fixed";
    el.style.pointerEvents = "none";
    el.style.zIndex = "9999";
    el.style.display = "none";

    el.style.background = "rgba(20, 20, 20, 0.92)";
    el.style.color = "#ffffff";
    el.style.padding = "10px 12px";
    el.style.borderRadius = "10px";
    el.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.35)";
    el.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif";
    el.style.fontSize = "12px";
    el.style.lineHeight = "1.35";
    el.style.minWidth = "280px";
    el.style.maxWidth = "360px";

    document.body.appendChild(el);
    return el;
}

function escapeHtml(str) {
    return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll("\"", "&quot;")
        .replaceAll("'", "&#39;");
}

function positionTooltip(el, event) {
    const offset = 14;
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    const rect = el.getBoundingClientRect();
    let x = event.clientX + offset;
    let y = event.clientY + offset;

    if (x + rect.width > vw - 8) {
        x = event.clientX - rect.width - offset;
    }
    if (y + rect.height > vh - 8) {
        y = event.clientY - rect.height - offset;
    }

    el.style.left = `${Math.max(8, x)}px`;
    el.style.top = `${Math.max(8, y)}px`;
}

function formatTopFans(rows) {
    if (!rows.length) {
        return `<div style="opacity:0.65;">No links found.</div>`;
    }

    return rows.map(r => {
        return `
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;">
                    ${escapeHtml(r.name)}
                </span>
                <span style="opacity:0.9;">
                    ${r.value.toLocaleString()} (${r.pct.toFixed(1)}%)
                </span>
            </div>
        `;
    }).join("");
}

function formatTopAffinity(rows) {
    if (!rows.length) {
        return `<div style="opacity:0.65;">No links found.</div>`;
    }

    return rows.map(r => {
        return `
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;">
                    ${escapeHtml(r.name)}
                </span>
                <span style="opacity:0.9;">
                    ${r.value.toFixed(2)}
                </span>
            </div>
        `;
    }).join("");
}

function computeTotalsForGenre(i, matrix) {
    // total fans for percentage denominator (exclude self)
    let total = 0;
    for (let j = 0; j < matrix.length; j++) {
        if (j === i) {
            continue;
        }
        total += (matrix[i][j] || 0);
    }
    return total;
}

function computeTop3ForGenre(i, names, matrix, scoreMatrix) {
    const fanRows = [];
    const affRows = [];

    const totalFans = computeTotalsForGenre(i, matrix);

    for (let j = 0; j < names.length; j++) {
        if (j === i) {
            continue;
        }

        const fans = matrix[i][j] || 0;
        const aff = scoreMatrix[i][j] || 0;

        if (fans > 0) {
            const pct = totalFans > 0 ? (fans / totalFans) * 100 : 0;
            fanRows.push({ name: names[j], value: fans, pct: pct });
        }

        if (fans > 0 && aff > 0) {
            affRows.push({ name: names[j], value: aff });
        }
    }

    fanRows.sort((a, b) => b.value - a.value);
    affRows.sort((a, b) => b.value - a.value);

    return {
        topFans: fanRows.slice(0, 3),
        topAff: affRows.slice(0, 3)
    };
}

function showArcTooltip(tooltipEl, event, genreName, topFans, topAff) {
    tooltipEl.innerHTML = `
        <div style="font-weight:700;font-size:13px;margin-bottom:6px;">
            ${escapeHtml(genreName)}
        </div>

        <div style="margin-top:6px;">
            <div style="font-weight:700;opacity:0.95;margin-bottom:4px;">
                Shared Fans (Top 3)
            </div>
            <div style="display:flex;flex-direction:column;gap:3px;">
                ${formatTopFans(topFans)}
            </div>
        </div>

        <div style="margin-top:10px;">
            <div style="font-weight:700;opacity:0.95;margin-bottom:4px;">
                Affinity Score (Top 3)
            </div>
            <div style="display:flex;flex-direction:column;gap:3px;">
                ${formatTopAffinity(topAff)}
            </div>
        </div>
    `;

    tooltipEl.style.display = "block";
    positionTooltip(tooltipEl, event);
}

function showRibbonTooltip(tooltipEl, event, sourceName, targetName, sharedFans, affinityScore) {

    tooltipEl.innerHTML = `
        <div style="font-weight:700;font-size:13px;margin-bottom:6px;">
            ${escapeHtml(sourceName)} ↔ ${escapeHtml(targetName)}
        </div>

        <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px;">
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <span style="opacity:0.8;">Shared Fans</span>
                <span style="opacity:0.95;">${(sharedFans || 0).toLocaleString()}</span>
            </div>
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <span style="opacity:0.8;">Affinity Score</span>
                <span style="opacity:0.95;">${(affinityScore || 0).toFixed(2)}</span>
            </div>
        </div>
    `;

    tooltipEl.style.display = "block";
    positionTooltip(tooltipEl, event);
}


// ===== Main Draw Function =====
function drawChordChart(data, manualSize=540) {
    // Clear the old chart so they don't stack
    d3.select("#chord-chart").html("");

    const names = Array.from(new Set(data.flatMap(d => [d.source, d.target])));
    const index = new Map(names.map((name, i) => [name, i]));

    const matrix = Array.from(
        { length: names.length },
        () => new Array(names.length).fill(0)
    );

    const scoreMatrix = Array.from(
        { length: names.length },
        () => new Array(names.length).fill(0)
    );

    data.forEach(d => {
        matrix[index.get(d.source)][index.get(d.target)] = d.value;
        matrix[index.get(d.target)][index.get(d.source)] = d.value;

        scoreMatrix[index.get(d.source)][index.get(d.target)] = d.score;
        scoreMatrix[index.get(d.target)][index.get(d.source)] = d.score;
    });

    // Use the manualSize for width and height
    const width = manualSize;
    const height = manualSize;

    // Keep your radius math proportional to the new size
    const outerRadius = Math.min(width, height) * 0.5 - 120;
    const innerRadius = outerRadius - 25;

    const svg = d3.select("#chord-chart")
                  .append("svg")
                  .attr("width", width)
                  .attr("height", height)
                  .attr("viewBox", [-width / 2, -height / 2, width, height]);

    rebuildWarpScale();

    const chord = d3.chord()
        .padAngle(0.04)
        .sortSubgroups(d3.descending)(matrix);

    const arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    const ribbon = d3.ribbon()
        .radius(innerRadius);

    const group = svg.append("g")
        .selectAll("g")
        .data(chord.groups)
        .join("g");

    const tooltipEl = ensureTooltipEl();

    // Draw Arcs + hover tooltip
    group.append("path")
        .attr("class", "genre-arc")
        .attr("fill", "#2c3e50")
        .attr("d", arc)
        .on("mouseenter", function(event, d) {
            const i = d.index;
            const genreName = names[i];
            const top = computeTop3ForGenre(i, names, matrix, scoreMatrix);

            showArcTooltip(tooltipEl, event, genreName, top.topFans, top.topAff);

            d3.select(this).attr("fill", "#1f2d3a");
        })
        .on("mousemove", function(event) {
            if (tooltipEl.style.display === "block") {
                positionTooltip(tooltipEl, event);
            }
        })
        .on("mouseleave", function() {
            tooltipEl.style.display = "none";
            d3.select(this).attr("fill", "#2c3e50");
        });

    // Labels
    group.append("text")
        .each(d => {
            d.angle = (d.startAngle + d.endAngle) / 2;
        })
        .attr("dy", ".35em")
        .attr("transform", d => `
            rotate(${(d.angle * 180 / Math.PI - 90)})
            translate(${outerRadius + 12})
            ${d.angle > Math.PI ? "rotate(180)" : ""}
        `)
        .attr("text-anchor", d => d.angle > Math.PI ? "end" : "start")
        .text(d => names[d.index])
        .style("font-family", "sans-serif")
        .style("font-size", "13px")
        .style("font-weight", "600");

    // Draw Ribbons (custom tooltip, no <title>)
    svg.append("g")
        .selectAll("path")
        .data(chord)
        .join("path")
        .attr("class", "chord-ribbon")
        .attr("d", ribbon)
        .attr("fill", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return colorOfScore(s);
        })
        .attr("fill-opacity", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            const u = warpScale(s);
            return d3.scalePow()
                .exponent(2)
                .domain([0, 1])
                .range([0.1, 0.85])(u);
        })
        .attr("stroke", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return s > currentKnots[1]
                ? d3.rgb(colorOfScore(s)).darker()
                : "none";
        })
        .style("mix-blend-mode", "multiply")
        .on("mouseenter", function(event, d) {
            const i = d.source.index;
            const j = d.target.index;

            const sourceName = names[i];
            const targetName = names[j];

            const sharedFans = matrix[i][j];
            const affinityScore = scoreMatrix[i][j];

            showRibbonTooltip(tooltipEl, event, sourceName, targetName, sharedFans, affinityScore);
        })
        .on("mousemove", function(event) {
            if (tooltipEl.style.display === "block") {
                positionTooltip(tooltipEl, event);
            }
        })
        .on("mouseleave", function() {
            tooltipEl.style.display = "none";
        });

    bindKnotTuner(scoreMatrix);
}
