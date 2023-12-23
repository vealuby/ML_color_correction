const input_file_photos = document.querySelector("#photo");
const input_file_etalon = document.querySelector("#etalon");
const result_container = document.querySelectorAll('.img__container')[1]
const original = document.querySelector(".original");
const result = document.querySelector(".result");

async function get_result(etalon, image_file, mime_type){
    await fetch('/api/correct_image_test', {
    method: 'POST',
    body: image_file // This is your file object
  })
      .then(response => response.json())
      .then(data => {

        var res = document.createElement("img");
        res.className = 'result';
        res.src = `data:${mime_type};base64,${data.base64}`;
        result_container.appendChild(res);

      })
    .catch(err => console.log(err))
  
  }

input_file_photos.addEventListener("change", (event) => {

    let photos = event.target.files;

    if (original.src == ''){
      etalon = photos[Math.floor(Math.random() * photos.length)]
    } 

    for (i = 0; i < photos.length; i++) {
      
      let reader = new FileReader();
      mime_type = photos[i]['type'];

      reader.onload = (function(etalon, file, mimeType) {
        return function(e) {
            let individualFormData = new FormData();
            individualFormData.append('image', file);
            get_result(etalon, individualFormData, mimeType);
        };

    })(etalon, photos[i], mime_type);
      
      reader.readAsDataURL(photos[i]);

    }

});

let etalon;
input_file_etalon.addEventListener("change", (event) => {

  let image_file = event.target.files[0];
  etalon = event.target.files[0];

  reader = new FileReader();
  reader.onload = function(e) {

      imageUrl = e.target.result;
      original.src = imageUrl;
      
    };

  reader.readAsDataURL(image_file);

});