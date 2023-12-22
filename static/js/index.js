const input_file = document.querySelector("#photo");
const original = document.querySelector(".original");
const result = document.querySelector(".result");

async function get_result(image_file, mime_type){
    await fetch('/api/correct_image_test', {
    method: 'POST',
    body: image_file // This is your file object
  })
      .then(response => response.json())
      .then(data => {
        result.src = `data:${mime_type};base64,${data.base64}`;
      })
    .catch(err => console.log(err))
  
  }

input_file.addEventListener("change", (event) => {

    image_file = event.target.files[0];
    reader = new FileReader();
    formData = new FormData();
    formData.append('image', image_file);

    reader.onload = function(e) {
        mime_type = image_file['type'];
        get_result(formData, mime_type);

        imageUrl = e.target.result;
        original.src = imageUrl;
        
      };

    reader.readAsDataURL(image_file);

});