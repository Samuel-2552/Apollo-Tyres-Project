function validate_frame(address) {
    let val = 'address_' + address;
    let inp = document.getElementById(val);
    let inputData = inp.value;

    sendData1(inputData, val,address); // Pass the input data and the ID of the input element

    // Prevent the default form submission behavior
    return false;
}
function check_ping(){
    event.preventDefault();
    let plc_ip = document.getElementById('plc_ip');
    send_data_plc(plc_ip.value);
}
function send_data_plc(plcip){
    $.ajax({
        url: '/pinging',
        type: 'POST',
        data: { 'data_1': plcip },
        success: function(response) {
            // Create a paragraph element for displaying the result
            let ch = document.getElementById('res_5');
            // Change the paragraph content based on the response value
            if (response.trim() === '0') {
                ch.style.color = "red";
                ch.innerHTML = "Failed!";
            } else {
            ch.style.color = "green";
                ch.innerHTML = "Success";
                tested+=1;
            }
            // Append the paragraph element below the corresponding input element

        },
        error: function(error) {
            console.log(error);
        }
    });
}

let tested = 0;
function sendData1(inputData, inputId,address_ret) {
    $.ajax({
        url: '/testing',
        type: 'POST',
        data: { 'data': inputData },
        success: function(response) {
            // Create a paragraph element for displaying the result
            let ch = document.getElementById("res_"+address_ret);

            // Change the paragraph content based on the response value
            if (response.trim() === '0') {
                ch.style.color = "red";
                ch.innerHTML = "Failed!";
            } else {
            ch.style.color = "green";
                ch.innerHTML = "Success";
                tested+=1;
            }

            // Append the paragraph element below the corresponding input element
            let inp = document.getElementById(inputId);
            inp.insertAdjacentElement('afterend', ch);
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function testing(){
  if(tested >= 4){
    var addresses = [];
        for (var i = 1; i <= 4; i++) {
            var address = document.getElementById("address_" + i).value;
            addresses.push(address);
        }

        var plc_ip = document.getElementById("plc_ip").value;
        var plc_port = document.getElementById("plc_port").value;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/live_feed", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText);
                alert(01);
                return window.location.href = '/live_feed_page';
            }
        };
        var data = JSON.stringify({ addresses: addresses, plc_ip: plc_ip, plc_port: plc_port });
        xhr.send(data);

         //// Prevent form submission

        }


  else{
    alert("Some cameras not found!");
  }

}

