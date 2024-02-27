const value = JSON.parse(document.getElementById('hello-data').textContent);

console.log(value);

var weatherdataset = await d3.json(`https://api.open-meteo.com/v1/forecast?latitude=${value.lat}&longitude=${value.long}&current=temperature_2m,weather_code`);

console.log(weatherdataset);
console.log(weatherdataset.latitude);
