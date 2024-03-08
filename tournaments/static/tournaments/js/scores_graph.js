const value = JSON.parse(document.getElementById('hello-data').textContent);


const data = await d3.json(`/api/scores?golf_round__holiday=${value.holiday_id}&golf_round__id=${value.round_id}`);
const data2 = await d3.json(`/api/scores`);

console.log(data);
console.log(`/api/scores?golf_round__holiday=${value.holiday_id}&golf_round__id=${value.round_id}`)

