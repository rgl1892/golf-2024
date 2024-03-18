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
    
    data.then((data) => plot(d3.bin().thresholds(6).value((d) => d.strokes)(data),[0,max_shots+1],2,2))
}


const page_width = document.getElementById("charts").offsetWidth;
const graph_width = page_width - 10;

const max_shots =  d3.max(data, d => d.strokes),
        max_stableford = d3.max(data, d => d.stableford_score),
        strokes_taken = d3.group(data, (d) => d.strokes),
        furthest_under_par = d3.min(d3.filter(data,(d) => d.strokes > 0 ),function(d){return d.strokes - d.hole.par });

const thresholds = [-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10];
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


// plot(d3.bin().thresholds([-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10]).value((d) => d.strokes)(data),[0,max_shots+1],2,2);


function svg_plot(id){
    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom;
    
    var svg = d3.select(`div.chart-${id}`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .attr('id',`svg-${id}`)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
        
    svg.append('g')
        .attr('class','axis--x')
        .attr('transform',`translate(${0},${height})`);

    svg.append('g')
        .attr('class','axis--y')
        .attr('transform',`translate(${0},${0})`);
    
}

function add_axes(id,x_domain,y_domain){
    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom;
    var x = d3.scaleLinear()
                .domain(x_domain)
                .range([0,width]);

    var y = d3.scaleLinear()
                .domain(y_domain)
                .range([height,0]);
    
    var svg = d3.select(`#svg-${id}`);

    
    
}

var duration = 5000;

function add_data(dataset, id,type){
    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom;

    var x_domain = [dataset.slice(0)[0][0][`${type}`] - 1,dataset.slice(-1)[0][0][`${type}`] + 1];
    var y_max = 0
    for (let i=0;i<dataset.length;i++){
        if (y_max < dataset[i].length){
            y_max = dataset[i].length
        }
    }
    var y_domain = [0,y_max+y_max*0.05]
    var x = d3.scaleLinear()
                .domain(x_domain)
                .range([0,width]);

    var y = d3.scaleLinear()
                .domain(y_domain)
                .range([height,0]);
    
    var svg = d3.select(`#svg-${id}`);
    
    svg.selectAll('.axis--x')
        .call(d3.axisBottom(x)) ;

    svg.selectAll('.axis--y')
        .call(d3.axisLeft(y));

    svg.selectAll('rect')
            .data(dataset)
            .enter()            
            .append('rect')
                .attr("x", (d,i) => x(d[0][`${type}`])- 20/2)
                .attr('y', d => y(d.length) )
                .attr("width", 20)
                .attr("height", d => y(0)- y(d.length))
                .attr("fill", "var(--bs-body-color)")
                .attr('stroke','black')
                .attr('transform', `translate(${margin.left},${margin.top})`)
                .append("svg:title")
                    .text((d,i) => `${d.length}`);
}

function change_data(dataset, id,type){

    console.log(dataset);
    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = graph_width - margin.left - margin.right ,
        height = graph_width*0.7 - margin.top - margin.bottom;

    var x_domain = [dataset.slice(0)[0][0][`${type}`] - 1,dataset.slice(-1)[0][0][`${type}`] + 1];
    var y_max = 0
    for (let i=0;i<dataset.length;i++){
        if (y_max < dataset[i].length){
            y_max = dataset[i].length
        }
    }
    var y_domain = [0,y_max+y_max*0.05]
    var x = d3.scaleLinear()
                .domain(x_domain)
                .range([0,width]);

    var y = d3.scaleLinear()
                .domain(y_domain)
                .range([height,0]);
    
    var svg = d3.select(`#svg-${id}`);
    
    svg.selectAll('.axis--x')
        .transition()
        .duration(duration)
        .call(d3.axisBottom(x).ticks(x_domain[1]-x_domain[0])) ;

    svg.selectAll('.axis--y')
    .transition()
    .duration(duration)
        .call(d3.axisLeft(y));

    svg.selectAll('rect')
            .attr('y', d => y(0) )
            .attr("height", d => 0);
            
    svg.selectAll('rect').data(dataset)
            .attr('y', d => y(0) )
            .attr("height", d => 0)
            .transition()
            .duration(duration)
            
                .attr("x", (d,i) => x(d[0][`${type}`])- 20/2)
                .attr('y', d => y(d.length) )
                .attr("width", 20)
                .attr("height", d => y(0)- y(d.length))
                .attr("fill", "var(--bs-body-color)")
                .attr('stroke','black')
                .attr('transform', `translate(${margin.left},${margin.top})`);
}


svg_plot(1);
svg_plot(2);
// add_data(d3.bin().thresholds(6).value((d) => d.stableford_score)(data),1,'stableford_score');
add_data(d3.bin().thresholds(thresholds).value((d) => d.strokes)(data),2,'strokes');

change_data(d3.bin().thresholds(6).value((d) => d.strokes)(d3.filter(data,(d) => d.strokes > 3 )),2,'strokes');
// change_data(d3.bin().thresholds(thresholds).value((d) => d.stableford_score)(data),2,'stableford_score');

// setTimeout(change_data(d3.bin().thresholds(thresholds).value((d) => d.strokes)(data),2,'strokes'),8000);

