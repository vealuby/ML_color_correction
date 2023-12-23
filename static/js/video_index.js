const input_file_etalon = document.querySelector("#etalon");
const etalon_img = document.querySelector(".etalon");

const input_file_video = document.querySelector("#video");
const a_download = document.querySelector("#download");

async function process_video(form_data, mime_type){
    await fetch('/api/correct_video', {
    method: 'POST',
    body: form_data // This is your file object
  })
      .then(response => response.json())
      .then(data => {

        a_download.href = data.link;
        a_download.innerHTML = 'Скачать';

      })
    .catch(err => console.log(err))
  
}

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

input_file_video.addEventListener("change", (event) => {

  let video = event.target.files[0];

  if (etalon_img.src == ''){
    return;
  }   
    
  let reader = new FileReader();
  mime_type = video['type'];

  reader.onload = (function(etalon, file, mimeType) {
    return function(e) {
        let individualFormData = new FormData();
        individualFormData.append('etalon', etalon);
        individualFormData.append('video', file);
        process_video(individualFormData, mimeType);
    };

  })(etalon, video, mime_type);
  reader.readAsDataURL(video);
  
});