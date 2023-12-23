from flask import Flask, jsonify, request, Response, render_template
from XmaxHack import *

import base64

# Init the app
app = Flask(__name__)

# Setup prediction endpoint
@app.route("/api/correct_image", methods=["POST"])
async def correct_image():

    img_file = request.files['image']
    etalon_file = request.files['etalon']
    
    etalon = Image.open(etalon_file)
    etalon_array = np.array(etalon)
    image = Image.open(img_file)
    image_array = np.array(image)

    img_gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(img_gray, (5, 5))  
    if cv2.mean(blur)[0] > 63:  
        color = False
    else:
        color = True

    new_img = await color_change(cv2.cvtColor(etalon_array, cv2.COLOR_RGB2BGR), cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR), color)

    result_image = Image.fromarray(new_img)

    img_byte_arr = io.BytesIO()
    result_image.save(img_byte_arr, format=img_file.mimetype.split('/')[1].upper())
    base64_bytes = base64.b64encode(img_byte_arr.getvalue())
    base64_string = base64_bytes.decode('ascii')    

    return jsonify({'base64': base64_string})

@app.route("/api/correct_etalon", methods=["POST"])
async def correct_etalon():

    etalon_file = request.files['etalon']
    
    etalon = Image.open(etalon_file)
    etalon_array = np.array(etalon)

    img_gray = cv2.cvtColor(etalon_array, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(img_gray, (5, 5))  
    if cv2.mean(blur)[0] > 63:  
        color = False
    else:
        color = True

    new_img = await change_main_img(cv2.cvtColor(etalon_array, cv2.COLOR_RGB2BGR), color)

    result_image = Image.fromarray(new_img)

    img_byte_arr = io.BytesIO()
    result_image.save(img_byte_arr, format=etalon_file.mimetype.split('/')[1].upper())
    base64_bytes = base64.b64encode(img_byte_arr.getvalue())
    base64_string = base64_bytes.decode('ascii')    

    return jsonify({'base64': base64_string})



@app.route("/", methods=["GET"])
async def index():
    return render_template('index.html')


if __name__ == "__main__":
    # Run the app on local host and port 8989
    app.run(debug=True, host="0.0.0.0", port=8989)