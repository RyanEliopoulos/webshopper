
function submit_listener() {
    // Should be able to retrieve the
    let sub_btn = document.getElementById("submit_button");
    sub_btn.addEventListener("click", get_locations);
//    sub_btn.onclick = get_locations;

//    sub_btn.addEventListener("Mouse", (event) => {
//        // Input validation would go here
//        let zipcode = document.getElementById("zipbox_input").value;
//        console.log(`Here is the zipbox value: ${zipcode}`);
//    });

    let url = sessionStorage.getItem('get_location_url');
    console.log(`Also checking the storage thing: ${url}`);
}


function get_locations() {
    console.log('in get_locations');
    let zipcode = document.getElementById('zipbox_input').value;
    console.log(`Here is the zipbox value: ${zipcode}`);
}

function set_location(set_endpoint) {
}




