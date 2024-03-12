const value = JSON.parse(document.getElementById('hello-data').textContent);


const data = await d3.json(`/api/scores?golf_round__holiday=${value.holiday_id}&golf_round__id=${value.round_id}`);
console.log(data);

const player_1 = data.slice(0,18);

function plot(dataset,name) {
    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = window.innerWidth*(1-5/7) - margin.left - margin.right ,
        height = 300 - margin.top - margin.bottom,
        bar_width = width/25;
    
    var svg = d3.select('div.chart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    var x = d3.scaleLinear()
                .domain([0,19])
                .range([0,width]);

    var y = d3.scaleLinear()
                .domain([0,5])
                .range([height,0]);
    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${height})`)
        .call(d3.axisBottom(x).tickValues([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(5));
    
    svg.append('text')
        .attr('class','y-label')
        .attr("text-anchor", "start")
        .attr("x", 0)
        .attr("y", -10)
        .text(`${name} to Par`);

    svg.selectAll('bar')
            .data(dataset.map(d => d.strokes-d.hole.par > 0 ? d : {strokes:0,hole:{par:0}}))
            .enter()
            .append('rect')
                .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                .attr('y', d => y(d.strokes-d.hole.par) )
                .attr("width", bar_width)
                .attr("height", d => y(0)- y(d.strokes-d.hole.par))

                .attr("fill", "#69b3a2CC")
                .attr('stroke','grey')
                .append("svg:title")
                    .text(d => `${d.strokes} shots`);

    svg.selectAll('bar')
                .data(dataset
                        .map(d => d.strokes-d.hole.par < 0 ? d : {strokes:0,hole:{par:0}})
                        .map(d => d.strokes > 0 ? d : {hole:{par:0}}))
                .enter()
                .append('rect')
                    .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                    .attr('y', d => y(0) )
                    .attr("width", bar_width)
                    .attr("height", d => y(0)- y(-d.strokes+d.hole.par))
                    .attr("fill", "#69b3a2CC")
                    .attr('stroke','grey')
                    .append("svg:title")
                        .text(d => `${d.strokes} shots`);

}
plot(data.slice(0,18),data.slice(0,18)[0]['player']['first_name']);
plot(data.slice(18,36),data.slice(18,36)[0]['player']['first_name']);
plot(data.slice(36,54),data.slice(36,54)[0]['player']['first_name']);
plot(data.slice(54,72),data.slice(54,72)[0]['player']['first_name']);