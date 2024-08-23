

// const value = JSON.parse(document.getElementById('player').textContent)
// const data = await d3.json(`/api/scores?golf_round__holiday=${value.holiday_id}&golf_round__id=${value.round_id}`);

const holes = [...Array(18).keys()].map(x => x+1);
console.log(holes)

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
}