
function submit_listener() {
    // Should be able to retrieve the
    let sub_btn = document.getElementById("submit_button");
    sub_btn.addEventListener("click", get_locations);

    console.log(`Also checking the storage thing: ${url}`);
}


function get_locations() {
    console.log('in get_locations');
    let zipcode = document.getElementById('zipbox_input').value;
    let url = sessionStorage.getItem('get_location_url');

    // Initializing request and attaching callback function
    let response = fetch(url, {
        method: 'GET',
        credentials: 'include'
    }).then( response => {
        console.log(`Received response ${response.status} ${response.statusText}`);
    });
}

function set_location(set_endpoint) {
}




