// const value = JSON.parse(document.getElementById('player-1').textContent) |
//  JSON.parse(document.getElementById('player-2').textContent)|
//  JSON.parse(document.getElementById('player-3').textContent)|
//  JSON.parse(document.getElementById('player-4').textContent);

const value = JSON.parse(document.getElementById('player').textContent)
const start = 0;
const end = 18;
const holes = [...Array(18).keys()].map(x => x+1);


const data = await d3.json(`/api/scores?golf_round__holiday=${value.holiday_id}&golf_round__id=${value.round_id}`);

function plot(dataset,name,div_id) {

    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = document.getElementById(`${div_id}`).offsetWidth - margin.left - margin.right ,
        height = 300 - margin.top - margin.bottom,
        bar_width = width/25;
    
    var svg = d3.select(`div.${div_id}`).append('svg')
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
        .call(d3.axisBottom(x).tickValues(holes)) ;

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

                .attr("fill", "var(--bs-body-color)")
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
                    .attr("fill", "var(--bs-body-color)")
                    .attr('stroke','grey')
                    .append("svg:title")
                        .text(d => `${d.strokes} shots`);

}

function plot_stable(dataset,name,div_id) {

    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = document.getElementById(`${div_id}`).offsetWidth - margin.left - margin.right ,
        height = 300 - margin.top - margin.bottom,
        bar_width = width/25;
    
    var svg = d3.select(`div.${div_id}`).append('svg')
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
        .call(d3.axisBottom(x).tickValues(holes)) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(5));
    
    svg.append('text')
        .attr('class','y-label')
        .attr("text-anchor", "start")
        .attr("x", 0)
        .attr("y", -10)
        .text(`${name} Points`);

    svg.selectAll('bar')
            .data(dataset.map(d => d.stableford_score > 0 ? d : {strokes:0,hole:{par:0}}))
            .enter()
            .append('rect')
                .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                .attr('y', d => y(d.stableford_score) )
                .attr("width", bar_width)
                .attr("height", d => y(0)- y(d.stableford_score))

                .attr("fill", "var(--bs-body-color)")
                .attr('stroke','grey')
                .append("svg:title")
                    .text(d => `${d.stableford_score} points`);

    svg.selectAll('bar')
                .data(dataset
                        .map(d => d.stableford_score < 0 ? d : {strokes:0,hole:{par:0}})
                        .map(d => d.strokes > 0 ? d : {hole:{par:0}}))
                .enter()
                .append('rect')
                    .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                    .attr('y', d => y(0) )
                    .attr("width", bar_width)
                    .attr("height", d => y(0)- y(-d.strokes))
                    .attr("fill", "var(--bs-body-color)")
                    .attr('stroke','grey')
                    .append("svg:title")
                        .text(d => `${d.strokes} points`);

}

function plot_stable_bird(dataset,name,div_id) {

    var margin = { top: 50, right: 50, bottom: 100, left: 50 },
        width = document.getElementById(`${div_id}`).offsetWidth - margin.left - margin.right ,
        height = 300 - margin.top - margin.bottom,
        bar_width = width/25;
    
    var svg = d3.select(`div.${div_id}`).append('svg')
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
        .call(d3.axisBottom(x).tickValues(holes)) ;

    svg.append('g')
        .attr('class','axis')
        .attr('transform',`translate(${0},${0})`)
        .call(d3.axisLeft(y).ticks(5));
    
    svg.append('text')
        .attr('class','y-label')
        .attr("text-anchor", "start")
        .attr("x", 0)
        .attr("y", -10)
        .text(`${name} Stableford Par`);

    svg.selectAll('bar')
            .data(dataset.map(d => 2 - d.stableford_score > 0 ? d : {strokes:0,hole:{par:0}}))
            .enter()
            .append('rect')
                .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                .attr('y', d => y(2 - d.stableford_score) )
                .attr("width", bar_width)
                .attr("height", d => y(0)- y(2-d.stableford_score))

                .attr("fill", "var(--bs-body-color)")
                .attr('stroke','grey')
                .append("svg:title")
                    .text(d => `${d.stableford_score} points`);
    // negative to par
    svg.selectAll('bar')
                .data(dataset
                        .map(d => 2 - d.stableford_score < 0 ? d : {stableford_score:0,hole:{par:0}})
                        .map(d => d.stableford_score > 0 ? d : {hole:{par:0}})) 
                .enter()
                .append('rect')
                    .attr("x", d => x(d.hole.hole_number) - bar_width/2)
                    .attr('y', d =>   y(0))
                    .attr("width", bar_width)
                    .attr("height", d => -y(d.stableford_score - 2)+y(0))
                    .attr("fill", "var(--bs-body-color)")
                    .attr('stroke','grey')
                    .append("svg:title")
                        .text(d => `${d.strokes} points`);

}


for (let i=0;i<4;i++) {
    plot(data.slice(start+(18*i),end+(18*i)),data.slice(start+(18*i),end+(18*i))[0]['player']['first_name'],`player-${i+1}`);
    plot_stable(data.slice(start+(18*i),end+(18*i)),data.slice(start+(18*i),end+(18*i))[0]['player']['first_name'],`player-${i+1}`);
    plot_stable_bird(data.slice(start+(18*i),end+(18*i)),data.slice(start+(18*i),end+(18*i))[0]['player']['first_name'],`player-${i+1}`);
}
