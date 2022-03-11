
function submit_listener() {
    // Should be able to retrieve the
    let sub_btn = document.getElementById("submit_button");
    sub_btn.addEventListener("click", get_locations);
}


function get_locations() {
    console.log('in get_locations');
    let zipcode = document.getElementById('zipbox_input').value;
    console.log(` Here is the host name${window.location.protocol}`);
    console.log(` Here is the host name${window.location.hostname}`);
    let url_string = window.location.protocol + '//' + window.location.hostname + ':5000'
//    let url = new URL(`${window.location.protocsessionStorage.getItem('get_location_url'), );
    let url_string = sessionStorage.getItem('get_location_url');
    console.log(`full fancy url? ${url}`);

    let url = new URL(url_string);
    url.set('zipcode', zipcode);
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




