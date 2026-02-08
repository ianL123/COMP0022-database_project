// static/js/chord_chart.js
function drawChordChart(data) {
    const names = Array.from(new Set(data.flatMap(d => [d.source, d.target])));
    const index = new Map(names.map((name, i) => [name, i]));
    
    // Matrix for thickness (value) and matrix for color (score)
    const matrix = Array.from({length: names.length}, () => new Array(names.length).fill(0));
    const scoreMatrix = Array.from({length: names.length}, () => new Array(names.length).fill(0));
    
    data.forEach(d => {
        matrix[index.get(d.source)][index.get(d.target)] = d.value;
        matrix[index.get(d.target)][index.get(d.source)] = d.value;
        scoreMatrix[index.get(d.source)][index.get(d.target)] = d.score;
        scoreMatrix[index.get(d.target)][index.get(d.source)] = d.score;
    });

    const width = 720, height = 720;
    const outerRadius = Math.min(width, height) * 0.5 - 120;
    const innerRadius = outerRadius - 25;

    const svg = d3.select("#chord-chart")
        .html("") 
        .append("svg")
        .attr("viewBox", [-width / 2, -height / 2, width, height]);

    // EXPONENTIAL STRATEGY:
    // scaleSequentialPow with exponent(3) ensures that only very high scores
    // get the deep blue colors. Middle-to-low scores will stay significantly lighter.
    const colorScale = d3.scaleSequentialPow(d3.interpolateYlGnBu)
        .exponent(1) 
        .domain([0, d3.max(data, d => d.score)]);

    const chord = d3.chord().padAngle(0.04).sortSubgroups(d3.descending)(matrix);
    const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
    const ribbon = d3.ribbon().radius(innerRadius);

    const group = svg.append("g").selectAll("g").data(chord.groups).join("g");

    // Draw Arcs
    group.append("path")
        .attr("fill", "#2c3e50")
        .attr("d", arc);

    // Labels
    group.append("text")
        .each(d => { d.angle = (d.startAngle + d.endAngle) / 2; })
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

    // Draw Ribbons
    svg.append("g")
        .selectAll("path")
        .data(chord)
        .join("path")
        .attr("class", "chord-ribbon")
        .attr("d", ribbon)
        .attr("fill", d => colorScale(scoreMatrix[d.source.index][d.target.index]))
        // DYNAMIC OPACITY: Higher scores get higher visibility
        .attr("fill-opacity", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return d3.scalePow().exponent(2).domain([0, 1]).range([0.1, 0.85])(s);
        })
        // BORDER: Darker stroke only for high-affinity connections
        .attr("stroke", d => {
            const s = scoreMatrix[d.source.index][d.target.index];
            return s > 0.7 ? d3.rgb(colorScale(s)).darker() : "none";
        })
        .style("mix-blend-mode", "multiply")
        .append("title")
        .text(d => {
            const s = names[d.source.index];
            const t = names[d.target.index];
            const score = scoreMatrix[d.source.index][d.target.index];
            return `${s} ↔ ${t}\nShared Fans: ${matrix[d.source.index][d.target.index]}\nAffinity Score: ${(score * 100).toFixed(2)}%`;
        });
}