
function submit_listener() {
    // Should be able to retrieve the
    let sub_btn = document.getElementById("submit_button");
    sub_btn.addEventListener("click", get_locations);
}


function get_locations(event) {
    console.log(`event.currentTarget: ${event.currentTarget}`);  // Element triggering the event

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
    for (let i = 0; i < locations.length; i++) {
        build_list_item(locations[i], i);
    }
    // locations.forEach(element => {
    //     // Updating new div with store details
    //     build_list_item(element);
    // });

    // Alternating colors for readability
    let location_items = document.getElementsByClassName('location_item');
    for (let i = 0; i < location_items.length; i++) {
        if (i % 2 === 0) {
            location_items[i].style.backgroundColor = 'lightblue';
        }
    }
}


function build_list_item(element, element_id) {
    /* helper function for update_ui_locations
        Constructs an inner div containing a particular store's data
        element: Single store result back from Kroger locations API
        element_id: Order the element came in. For client-side state tracking
     */

    let main_div = document.getElementById('main_div');  // To attach the new list divs onto

    let store_div = document.createElement("div");  // Going to store successive divs, each with a piece of store data
    store_div.classList.add('location_item');
    store_div.id = element_id;
    // building store chain details
    let chain_div = document.createElement("div");
    store_div.appendChild(chain_div);
    chain_div.classList.add('chain_div');
    let chain_node = document.createTextNode(element.chain);
    chain_div.appendChild(chain_node);
    // Building  address divs
    // Address Line
    let addr_div = document.createElement("div");
    addr_div.classList.add('addr_div');
    store_div.appendChild(addr_div);
    let addrline_node = document.createTextNode(element.address.addressLine1);
    addr_div.appendChild(addrline_node);
    // City
    let addrcity_div = document.createElement("div");
    addrcity_div.classList.add('addrcity_div');
    store_div.appendChild(addrcity_div);
    let addr_city_node = document.createTextNode(element.address.city);
    addrcity_div.appendChild(addr_city_node);
    // State
    let addr_state_div = document.createElement("div");
    addr_state_div.classList.add('addr_state_div');
    store_div.appendChild(addr_state_div);
    let addr_state_node = document.createTextNode(element.address.state);
    addr_state_div.appendChild(addr_state_node);
    // Zipcode
    let addr_zipcode_div = document.createElement("div");
    addr_zipcode_div.classList.add('addr_zipcode_div');
    store_div.appendChild(addr_zipcode_div);
    let addr_zipcode = document.createTextNode(element.address.zipCode);
    addr_zipcode_div.appendChild(addr_zipcode);

    // Adding  these to the primary div holder
    main_div.appendChild(store_div);

    // Adding the onclick
    store_div.addEventListener("click", event => {
        // Need to highlight new selection and unhighlight old selection, if applicable
        let selected_id = sessionStorage.getItem('selected_item'); // id of the item div
        if (selected_id != null) {
            let item_div = document.getElementById(selected_id);
            if (selected_id % 2 === 0) {
                item_div.style.backgroundColor = 'lightblue';
            }
            else {
                item_div.style.backgroundColor = 'white';
            }
        }
        // Updating state of the new selected item div and saving to storage
        event.currentTarget.style.backgroundColor = 'yellow';
        sessionStorage.setItem('selected_item', event.currentTarget.id);
        console.log(`setting selected item to id ${event.currentTarget.id}`);
    });
}

function list_cleanup() {
    // Finds and deletes all list item containers
    let elements = document.getElementsByClassName('location_item');
    console.log(`length of the location_itme array: ${elements.length}`);
    if (elements.length === 0) return;
    for (let i = 0; i < elements.length; ) {
        let element = elements[i];
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
        element.remove();
    }
}


function set_location(set_endpoint) {
}




