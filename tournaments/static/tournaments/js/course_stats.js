const value = JSON.parse(document.getElementById('hello-data').textContent);

var root = document.location.hostname
const data = await d3.json(`/api/scores?hole__course=${value.course_id}`);


const table_height = document.getElementById("chart-18").offsetTop - document.getElementById("chart-1").offsetTop


console.log(data);

function plot(data){

    var margin = { top: 62, right: 20, bottom: 20, left: 20 },
        width = 500 - margin.left - margin.right,
        height = table_height - margin.top - margin.bottom;

    var svg = d3.select('#chart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    var x = d3.scaleLinear()
                .domain([0,10])
                .range([0,width])
    
    var y = d3.scaleLinear()
                .domain([18,1])
                .range([height,0])

    svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${0},${height})`)
                .call(d3.axisBottom(x));
        
    svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${0},${0})`)
                .call(d3.axisLeft(y));
        
    svg.selectAll('bar')
                .data(data)
                .enter()
                .append('rect')
                .attr("x", (d, i) => x(d.strokes))
                .attr('y', d => y(d.hole.hole_number))
                .attr("width", 10)
                .attr("height", 10)
                .attr("fill", "var(--bs-body-color)")
                .attr('stroke', 'black');


    
}

plot(data);