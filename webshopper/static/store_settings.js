
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
        console.log(data.results);
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
    console.log(typeof(locations));
    console.log(locations);
    locations.forEach(element => {
        // Updating new div with store details
        let tmp_div = document.createElement("div");
        tmp_div.classList.add('location_item');
        let chain_node = document.createTextNode(element.chain);
        chain_node.classList.add('location_item');
        tmp_div.appendChild(chain_node);
        let br = document.createElement("br");
        br.classList.add('location_item');

        tmp_div.appendChild(br);
        let addressLine = document.createTextNode(element.address.addressLine1);
        addressLine.classList.add('location_item');
        tmp_div.appendChild(addressLine);
        let city_node = document.createTextNode(element.address.city);
        city_node.classList.add('location_item');
        tmp_div.appendChild(city_node);
        let state_node = document.createTextNode(element.address.state);
        state_node.classList.add('location_item');
        tmp_div.appendChild(state_node);
        let zip_node = document.createTextNode(element.address.zipCode);
        zip_node.classList.add('location_item');
        tmp_div.appendChild(zip_node);
        // Adding this div to the main div
        main_div.appendChild(tmp_div);
    });
}

function list_cleanup() {
    // Finds and deletes all list item containers
    let elements = document.getElementsByClassName('location_item');
    if (elements.length === 0) return;
    Array.prototype.forEach.call(elements, element => {
        console.log('worked baby');
        console.log(element);
        element.remove();
    })
    // console.log(elements);
    // elements.forEach(element => {
    //     element.remove();
    // });
}


function set_location(set_endpoint) {
}




