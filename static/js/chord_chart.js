// ===== Threshold State =====
let currentThresholds = [0.2, 0.4, 0.6, 0.8];
let colorScale = null;

function build5Colors() {
    const interp = d3.interpolateYlGnBu;
    return [0.15, 0.35, 0.55, 0.75, 0.95].map(t => interp(t));
}

function normalizeAndSortThresholds(arr) {
    let t = arr.map(x => Math.max(0, Math.min(0.99, +x))).sort((a, b) => a - b);
    const eps = 0.01;
    for (let i = 1; i < t.length; i++) {
        if (t[i] <= t[i - 1]) {
            t[i] = Math.min(0.99, t[i - 1] + eps);
        }
    }
    return t;
}

function rebuildColorScale() {
    colorScale = d3.scaleThreshold()
        .domain(currentThresholds)
        .range(build5Colors());
}

function bindThresholdTuner(scoreMatrix) {
    const ids = ["t1", "t2", "t3", "t4"];
    const valIds = ["t1Val", "t2Val", "t3Val", "t4Val"];

    const inputs = ids.map(id => document.getElementById(id));
    const labels = valIds.map(id => document.getElementById(id));

    if (inputs.some(x => !x) || labels.some(x => !x)) {
        return;
    }

    function syncUI(thresholds) {
        thresholds.forEach((v, i) => {
            inputs[i].value = v.toFixed(2);
            labels[i].textContent = v.toFixed(2);
        });
    }

    function update() {
        const raw = inputs.map(x => parseFloat(x.value));
        currentThresholds = normalizeAndSortThresholds(raw);
        syncUI(currentThresholds);
        rebuildColorScale();

        d3.select("#chord-chart")
            .selectAll(".chord-ribbon")
            .transition()
            .duration(120)
            .attr("fill", d => colorScale(scoreMatrix[d.source.index][d.target.index]))
            .attr("stroke", d => {
                const s = scoreMatrix[d.source.index][d.target.index];
                return s > currentThresholds[2]
                    ? d3.rgb(colorScale(s)).darker()
                    : "none";
            });
    }

    syncUI(currentThresholds);
    inputs.forEach(inp => inp.addEventListener("input", update));
}


// ===== Main Draw Function =====
function drawChordChart(data) {

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

    const width = 720;
    const height = 720;
    const outerRadius = Math.min(width, height) * 0.5 - 120;
    const innerRadius = outerRadius - 25;

    const svg = d3.select("#chord-chart")
        .html("")
        .append("svg")
        .attr("viewBox", [-width / 2, -height / 2, width, height]);

    rebuildColorScale();

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

    group.append("path")
        .attr("fill", "#2c3e50")
        .attr("d", arc);

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

    svg.append("g")
        .selectAll("path")
        .data(chord)
        .join("path")
        .attr("class", "chord-ribbon")
        .attr("d", ribbon)
        .attr("fill", d => colorScale(scoreMatrix[d.source.index][d.target.index]))
        .attr("fill-opacity", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return d3.scalePow()
                .exponent(2)
                .domain([0, 1])
                .range([0.1, 0.85])(s);
        })
        .attr("stroke", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return s > currentThresholds[2]
                ? d3.rgb(colorScale(s)).darker()
                : "none";
        })
        .style("mix-blend-mode", "multiply")
        .append("title")
        .text(d => {
            const s = names[d.source.index];
            const t = names[d.target.index];
            const score = scoreMatrix[d.source.index][d.target.index];
            return `${s} ↔ ${t}
Shared Fans: ${matrix[d.source.index][d.target.index]}
Affinity Score: ${(score * 100).toFixed(2)}%`;
        });

    bindThresholdTuner(scoreMatrix);
}
