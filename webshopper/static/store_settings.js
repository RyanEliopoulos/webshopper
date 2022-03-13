
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
            // @TODO response parsing here? Not sure
          console.log(`data.results: ${data.results}`);
          update_ui_locations(data.results);
          // So we have the store locations. Remove old html elements
          // and replace with a list of locations to choose from

    });
}


function update_ui_locations(locations) {
    // Called by get_locations after receiving location data from our API
    // locations = list of JSON objects
    // keys 'address', 'locationId', 'chain'

    // Remove existing buttons/elements
    list_cleanup();
    // update with a list of elements..how do we record selection?
    let main_div = document.getElementById('main_div');  // To attach the new list divs onto
    locations.foreach(element => {
        // Updating new div with store details
        let tmp_div = document.createElement("div");
        let chain_node = document.createTextNode(element.chain);
        tmp_div.appendChild(chain_node);
        let br = document.createElement("br");
        tmp_div.appendChild(br);
        let address_node = document.createTextNode(element.address);
        tmp_div.appendChild(address_node);
        // Adding this div to the main div
        main_div.appendChild(tmp_div);
    });
}

function list_cleanup() {
    // Finds and deletes all list item containers
    let elements = document.getElementsByClassName('location_item');
    console.log(`the desired length value: ${elements.length}`);
    if (typeof(elements) === 'undefined') {
        console.log('Yep, it\'s undefined');
        return;
    }

    // elements.foreach(element => {
    //     element.remove();
    // });
}


function set_location(set_endpoint) {
}




