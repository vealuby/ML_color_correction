const input_file_photos = document.querySelector("#photo");
const input_file_etalon = document.querySelector("#etalon");
const orig_container = document.querySelectorAll('.img__container')[1]
const result_container = document.querySelectorAll('.img__container')[2]
const etalon_img = document.querySelector(".etalon");

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function get_result(form_data, mime_type, i){
    await fetch('/api/correct_image', {
    method: 'POST',
    body: form_data // This is your file object
  })
      .then(response => response.json())
      .then(data => {

        var res = document.createElement("img");
        res.className = 'result';
        res.src = `data:${mime_type};base64,${data.base64}`;

        // while (result_container.children.length < i){
        //   sleep(0.5 * 1000);
        // }

        result_container.appendChild(res);

      })
    .catch(err => console.log(err))
  
  }

  async function change_etalon(form_data, mime_type){
    await fetch('/api/correct_etalon', {
    method: 'POST',
    body: form_data // This is your file object
  })
      .then(response => response.json())
      .then(data => {

        etalon_img.src = `data:${mime_type};base64,${data.base64}`;

      })
    .catch(err => console.log(err))
  
  }

input_file_photos.addEventListener("change", (event) => {

    let photos = event.target.files;

    if (etalon_img.src == ''){
      var etalon_reader = new FileReader();

      etalon = photos[Math.floor(Math.random() * photos.length)];

      etalon_reader.onload = function(e) {

        imageUrl = e.target.result;
        etalon_img.src = imageUrl;
        
      };

      etalon_reader.readAsDataURL(etalon);
    } 

    for (i = 0; i <= photos.length; i++) {
      

      if (i != photos.length){

        let reader = new FileReader();
        mime_type = photos[i]['type'];

        reader.onload = (function(etalon, file, mimeType, i) {
          return function(e) {
              let individualFormData = new FormData();
              individualFormData.append('etalon', etalon);
              individualFormData.append('image', file);
              get_result(individualFormData, mimeType, i);

              var orig = document.createElement("img");
              orig.className = 'result';
              orig.src = e.target.result;
              orig_container.appendChild(orig);

          };

        })(etalon, photos[i], mime_type, i);
        
        reader.readAsDataURL(photos[i]);

      }else{

        let reader = new FileReader();
        mime_type = etalon['type'];

        reader.onload = (function(etalon, mimeType) {
          return function(e) {
              let individualFormData = new FormData();
              individualFormData.append('etalon', etalon);
              change_etalon(individualFormData, mimeType);
          };


        })(etalon, mime_type);
        
        reader.readAsDataURL(etalon);

      }

    }

});

let etalon;
input_file_etalon.addEventListener("change", (event) => {

  let image_file = event.target.files[0];
  etalon = event.target.files[0];

  reader = new FileReader();
  reader.onload = function(e) {

      imageUrl = e.target.result;
      etalon_img.src = imageUrl;
      
    };

  reader.readAsDataURL(image_file);

});