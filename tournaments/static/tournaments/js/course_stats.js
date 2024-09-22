

async function full_plot(id) {
    var course = document.getElementById('course_select').value;
    var round = document.getElementById('round_select').value;
    var player = document.getElementById('player_select').value;
    var holiday = document.getElementById('holiday_select').value;
    var dataset = await d3.json(`/api/scores?hole__course=${course}&player=${player}&golf_round__round_number=${round}&golf_round__holiday=${holiday}`);
    var data = d3.group(dataset, (d) => d.hole.hole_number);
    var stable_data = d3.map(data,d => [d[0],d3.mean(d[1],i => i.stableford_score)]);
    var strokes_data = d3.map(data,d => [d[0],d3.mean(d[1],i => i.strokes - i.hole.par)]);
    var all_data = d3.map(dataset, d => d.stableford_score);
    // all_data = all_data.sort(d3.descending,d => d.hole.hole_number)
    var all_par_data = d3.map(dataset, d => d.strokes - d.hole.par);
    var all_shots_data = d3.map(dataset, d => d.strokes);
    
    

    sub_plot(stable_data,1)
    sub_plot(strokes_data,2)
    all_plot(all_data,3)
    all_plot(all_par_data,4)
    all_plot(all_data.sort(d3.descending),5)
    all_plot(all_par_data.sort(d3.descending),6)
    all_plot(all_shots_data.sort(d3.descending),7)

}

var colour = '#0FA3B1';

function sub_plot(data,id){
    const holes = [...Array(18).keys()].map(x => x+1);
    var margin = { top: 40, right: 40, bottom: 40, left: 40 },
        width = document.getElementById(`chart-${id}`).offsetWidth - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;
    var bar_width = width/20;


    try {d3.select(`#svg-${id}`).remove();}
    catch{}
    var svg = d3.select(`#chart-${id}`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .attr('id', `svg-${id}`)
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    var max_y = Math.ceil(d3.max(data,d=>d[1]))
    var x = d3.scaleLinear()
        .domain([0,19])
        .range([0,width]);

    var y = d3.scaleLinear()
        .domain([0,max_y])
        .range([height,0]);
    
    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${height})`)
        .call(d3.axisBottom(x)) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(max_y));

    var tooltip = d3.select(`#chart-${id}`)
        .append('div')
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        .style("position", "absolute");

    var mouseover = function (mouse,d){
        d3.select(this)
            .attr('fill',colour)
            tooltip.style("opacity", 1);
    };

    var mousemove = function (mouse,d){
        tooltip.html( Math.round(d[1]*100)/100)
        .style("left", `${mouse["layerX"] + 20}px`)
        .style("top", `${mouse["layerY"] - 20}px`);
        };
    
    var mouseout = function(mouse,d){
        d3.select(this)
            .attr("fill", "var(--bs-body-color)")
            tooltip.style("opacity", 0);
    };

    svg.selectAll('bar')
        .data(data)
        .enter()
        .append('rect')
            .attr("x", d => x(d[0]) -bar_width/2)
            .attr('y', d => d[1] >0 ? y(d[1]):y(0) )
            .attr("width", bar_width)
            .attr("height", d => d[1] >0 ? y(0)- y(d[1]) : y(d[1])-y(0))
            .attr("fill", "var(--bs-body-color)")
            .attr('stroke','grey')
            .on("mouseover",mouseover)
            .on("mousemove",mousemove)
            .on('mouseout',mouseout)
}

function all_plot(data,id){
    const holes = [...Array(18).keys()].map(x => x+1);
    var margin = { top: 40, right: 40, bottom: 40, left: 40 },
        width = document.getElementById(`chart-${id}`).offsetWidth - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;
    


    try {d3.select(`#svg-${id}`).remove();}
    catch{}
    var svg = d3.select(`#chart-${id}`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .attr('id', `svg-${id}`)
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    var max_y = d3.max(data);
    var min_y = d3.min(data);

    var bar_width = width/(data.length);


    var x = d3.scaleLinear()
        .domain([0,data.length])
        .range([0,width]);

    var y = d3.scaleLinear()
        .domain([min_y<=0?min_y:0,max_y])
        .range([height,0]);
    
    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${height*(max_y/(-min_y+max_y))})`)
        .call(d3.axisBottom(x)) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(max_y+Math.abs(min_y)));

    var tooltip = d3.select(`#chart-${id}`)
                .append('div')
                .style("opacity", 0)
                .attr("class", "tooltip")
                .style("background-color", "white")
                .style("border", "solid")
                .style("border-width", "2px")
                .style("border-radius", "5px")
                .style("padding", "5px")
                .style("position", "absolute");

    var mouseover = function (mouse,d){
        d3.select(this)
            .attr('fill',colour)
            .attr('stroke-width',1)
            tooltip.style("opacity", 1);
    };

    var mousemove = function (mouse,d){
        tooltip.html( d)
        .style("left", `${mouse["layerX"] + 20}px`)
        .style("top", `${mouse["layerY"] - 20}px`);
        };
    
    var mouseout = function(mouse,d){
        d3.select(this)
            .attr("fill", "var(--bs-body-color)")
            .attr('stroke-width',0.01);
            tooltip.style("opacity", 0);
    };
    
    svg.selectAll('bar')
        .data(data)
        .enter()
        .append('rect')
            .attr("x", (d,i) =>  x(i+1) -bar_width/2)
            .attr('y', d => d >= 0 ? y(d) : y(0))
            .attr("width", bar_width)
            .attr("height", d => d >= 0 ? y(0)- y(d): y(d)-y(0))
            .attr("fill", "var(--bs-body-color)")
            .attr('stroke','grey')
            .attr('stroke-width',0.01)
            .on("mouseover",mouseover)
            .on("mousemove",mousemove)
            .on('mouseout',mouseout)
            
            ;

      
}




document.getElementById('course_select').addEventListener('change', full_plot);
document.getElementById('round_select').addEventListener('change', full_plot);
document.getElementById('player_select').addEventListener('change', full_plot);
document.getElementById('holiday_select').addEventListener('change', full_plot);
