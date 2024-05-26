var holiday = '60';
var player = '1';
var round_number = '1';
var data = await d3.json(`/api/scores?golf_round__holiday=${holiday}&player=${player}&golf_round__round_number=${round_number}`);

var font_size = 1;

function line_plot(data,id) {
    const div_width = document.getElementById(`chart-${id}`).offsetWidth;

    var margin = { top: div_width/10, right: div_width/10, bottom: div_width/10, left: div_width/10 },
        width = div_width - margin.left - margin.right,
        height = div_width*2/3 - margin.top - margin.bottom;

    var svg = d3.select(`#chart-${id}`).append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
    .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
        .attr('stroke-width',"2px")
        ;

    console.log(data.length,)
    
    var x = d3.scaleLinear()
                .domain([0,data.length])
                .range([0,width])
    var y = d3.scaleLinear()
                .domain([data.slice(-1),0])
                .range([0,height])
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(${0},${height})`)
        .call(d3.axisBottom(x))
        .attr('font-size',`${font_size}em`);
        
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(${0},${0})`)
        .call(d3.axisLeft(y))
        .attr('font-size',`${font_size}em`);
    
    var line = d3.line()
                .x((d,i) => x(i))
                .y((d) => y(d));

    svg.append('path')
        .attr('d',line(data))
        .attr('fill','none')
        .attr('stroke',"var(--bs-body-color)")
        .attr('stroke-width',"2px")

}

line_plot(d3.cumsum(data,(d,i) => d.strokes - d.hole.par),1);
line_plot(d3.cumsum(data,(d,i) => d.stableford_score),2);
line_plot(d3.cumsum(data,(d,i) => d.strokes),3);