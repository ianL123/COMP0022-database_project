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

    const width = 650, height = 650;
    const outerRadius = Math.min(width, height) * 0.5 - 100;
    const innerRadius = outerRadius - 20;

    const svg = d3.select("#chord-chart")
        .html("") // Clear the container
        .append("svg")
        .attr("viewBox", [-width / 2, -height / 2, width, height]);

    // Color Scale: Yellow (low affinity) to Deep Blue (high affinity)
    const colorScale = d3.scaleSequential()
        .domain([0, d3.max(data, d => d.score)])
        .interpolator(d3.interpolateYlGnBu);

    const chord = d3.chord().padAngle(0.04).sortSubgroups(d3.descending)(matrix);
    const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
    const ribbon = d3.ribbon().radius(innerRadius);

    const group = svg.append("g").selectAll("g").data(chord.groups).join("g");

    // Draw Arcs
    group.append("path")
        .attr("fill", "#333")
        .attr("d", arc);

    // Labels
    group.append("text")
        .each(d => { d.angle = (d.startAngle + d.endAngle) / 2; })
        .attr("dy", ".35em")
        .attr("transform", d => `
            rotate(${(d.angle * 180 / Math.PI - 90)})
            translate(${outerRadius + 10})
            ${d.angle > Math.PI ? "rotate(180)" : ""}
        `)
        .attr("text-anchor", d => d.angle > Math.PI ? "end" : "start")
        .text(d => names[d.index])
        .style("font-size", "12px")
        .style("font-weight", "600");

    // Draw Ribbons
    svg.append("g")
        .attr("fill-opacity", 0.8)
        .selectAll("path")
        .data(chord)
        .join("path")
        .attr("class", "chord-ribbon")
        .attr("d", ribbon)
        .attr("fill", d => colorScale(scoreMatrix[d.source.index][d.target.index]))
        .attr("stroke", d => d3.rgb(colorScale(scoreMatrix[d.source.index][d.target.index])).darker())
        .append("title")
        .text(d => `${names[d.source.index]} ↔ ${names[d.target.index]}\nShared Fans: ${matrix[d.source.index][d.target.index]}\nAffinity Score: ${(scoreMatrix[d.source.index][d.target.index] * 100).toFixed(2)}%`);
}