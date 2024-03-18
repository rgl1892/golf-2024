const value = JSON.parse(document.getElementById('hello-data').textContent);

const data = await d3.json(`https://api.open-meteo.com/v1/forecast?latitude=${value.lat}&longitude=${value.long}&hourly=temperature_2m&forecast_days=1`);
const fixed = d3.transpose([data.hourly.time,data.hourly.temperature_2m]);

function plot() {
    var margin = { top: 10, right: 30, bottom: 20, left: 0 },
        width = 200 - margin.left - margin.right,
        height = 100 - margin.top - margin.bottom;
    
    var svg = d3.select('plot').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    var x = d3.scaleLinear()
                .domain([0,23])
                .range([0,width]);
    var y = d3.scaleLinear()
                .domain([5,35])
                .range([height,0]);
    
    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${width},${0})`)
        .call(d3.axisRight(y).ticks(5));

    // svg.append('g')
    //     .attr('class','axis')
    //     .attr('transform',`translate(${0},${height})`)
    //     .call(d3.axisBottom(x).ticks(0));

    var temp_line = d3.line()
                .x((d,i) => x(d[0].slice(-5,-3)))
                .y((d,i) => y(d[1]));

    var temp = svg.append('path')
                        .attr('fill','none')
                        .attr('stroke','yellow')
                        .attr("stroke-width", 1)
                        .attr("d",temp_line(fixed));
   
}                       

 plot();

