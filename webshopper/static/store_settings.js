
function submit_listener() {
    // Should be able to retrieve the
    let sub_btn = document.getElementById("submit_button");
    sub_btn.addEventListener("click", get_locations);
}


function get_locations() {
    console.log('in get_locations');
    let zipcode = document.getElementById('zipbox_input').value;
    let url_string = sessionStorage.getItem('get_location_url');
    let url = new URL(url_string);
    url.searchParams.append('zipcode', zipcode);
    // Initializing request and attaching callback function
    let response = fetch(url, {
        method: 'GET',
        credentials: 'include'
    })
    .then (response => response.json())  // Deserializing the json response
    .then  ( data => { // Working with the json object
          console.log(data.results);
//        console.log(`Received response ${response.status} ${response.statusText}`);
//        console.log(`${response.body}`);
//        console.log(`${response.json()}`);
    });
}

function set_location(set_endpoint) {
}




