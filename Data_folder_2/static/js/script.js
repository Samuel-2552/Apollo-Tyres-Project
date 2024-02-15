function validate_frame(address) {
    let val = 'address_' + address;
    let inp = document.getElementById(val);
    let inputData = inp.value;

    sendData1(inputData, val,address); // Pass the input data and the ID of the input element

    // Prevent the default form submission behavior
    return false;
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
    window.location.href='/live_feed';
  }
  else{
    alert("Some cameras not found!");
  }

}

