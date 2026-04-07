const OPENFOODFACTS_API_ENDPOINT = 'https://world.openfoodfacts.net'

fetch(`${OPENFOODFACTS_API_ENDPOINT}/api/v2/product/3274080005003.json`, {
  method: "GET",
  headers: { Authorization: "Basic " + btoa("off:off") },
})
  .then((response) => response.json())
  .then((json) => console.log(json));