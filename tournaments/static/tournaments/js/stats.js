var course = '';
var player = '';
var data = await d3.json(`/api/scores?golf_round__holiday=${course}&player=${player}`);


var val = document.getElementById('player_choice').addEventListener('change',re_plot);

async function getData(){
    var player = document.getElementById('player_choice').value;
    var data = await d3.json(`/api/scores?golf_round__holiday=${course}&player=${player}`)
    return data
}

function re_plot(){
    d3.selectAll("svg").remove();
    var data = getData();
    data.then((data) => plot_to_par(d3.bin().value((d) => d.strokes - d.hole.par)(d3.filter(data, (d) => d.strokes > 0)), [-3, 5]))
    data.then((data) => plot(d3.bin().thresholds(max_stableford).value((d) => d.stableford_score)(data),[-1,max_stableford+1],0,1))
    data.then((data) => plot(d3.bin().thresholds(6).value((d) => d.strokes)(data),[0,max_shots+1],2,2))
}


const page_width = document.getElementById("charts").offsetWidth;
console.log(page_width);
const graph_width = page_width < 1024 ? page_width : page_width*0.37;

const max_shots =  d3.max(data, d => d.strokes),
        max_stableford = d3.max(data, d => d.stableford_score),
        strokes_taken = d3.group(data, (d) => d.strokes),
        furthest_under_par = d3.min(d3.filter(data,(d) => d.strokes > 0 ),function(d){return d.strokes - d.hole.par });


function plot(dataset,x_domain,modifier,id) {

    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom,
        bar_width = width/(x_domain[1]-x_domain[0]+2);
    
    var svg = d3.select(`div.chart-${id}`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    var x = d3.scaleLinear()
                .domain(x_domain)
                .range([0,width]);

    var y = d3.scaleLinear()
                .domain([0,250])
                .range([height,0]);
    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${height})`)
        .call(d3.axisBottom(x).ticks(x_domain[1]-x_domain[0])) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(5));
    
    svg.selectAll('bar')
            .data(dataset)
            .enter()
            .append('rect')
                .attr("x", (d,i) => x(i+modifier) - bar_width/2)
                .attr('y', d => y(d.length) )
                .attr("width", bar_width)
                .attr("height", d => y(0)- y(d.length))

                .attr("fill", "var(--bs-body-color)")
                .attr('stroke','black')
                .append("svg:title")
                    .text((d,i) => `${d.length}`);
}
function plot_to_par(dataset, x_domain) {

   var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom,
        bar_width = width/(x_domain[1]-x_domain[0]+2);

    var svg = d3.select(`div.chart-3`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    var x = d3.scaleLinear()
        .domain(x_domain)
        .range([0, width]);

    var y = d3.scaleLinear()
        .domain([0, 250])
        .range([height, 0]);
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(${0},${height})`)
        .call(d3.axisBottom(x).ticks(x_domain[1] - x_domain[0]));

    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(5));

    svg.selectAll('bar')
        .data(dataset)
        .enter()
        .append('rect')
        .attr("x", function (d, i) {
            try{ return x(d[0].strokes -d[0].hole.par) - bar_width / 2;}
            
            catch (err) { }
        })
        .attr('y', d => y(d.length))
        .attr("width", bar_width)
        .attr("height", d => y(0) - y(d.length))

        .attr("fill", "var(--bs-body-color)")
        .attr('stroke', 'black')
        .append("svg:title")
        .text((d, i) => `${d.length}`);
}

plot(d3.bin().thresholds(max_stableford).value((d) => d.stableford_score)(data),[-1,max_stableford+1],0,1);
plot_to_par(d3.bin().value((d) => d.strokes - d.hole.par)(d3.filter(data, (d) => d.strokes > 0)), [-3, 5]);
plot(d3.bin().thresholds(6).value((d) => d.strokes)(data),[0,max_shots+1],2,2);