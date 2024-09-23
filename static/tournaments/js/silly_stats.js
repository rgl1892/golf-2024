var data = await d3.json(`/api/scores`);

function plot(data) {
    var margin = { top: 50, right: 50, bottom: 50, left: 50 },
        width = 960 - margin.left - margin.right,
        height = 640 - margin.top - margin.bottom;
    
    var svg = d3.select('#chart-1').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    
    
}

plot(data);