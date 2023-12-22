from flask import Flask, jsonify, request, Response, render_template
from model import *

import base64

# Init the app
app = Flask(__name__)

# Setup prediction endpoint
@app.route("/api/correct_image_test", methods=["POST"])
async def correct_image_test():

    img = request.files['image']
    image = Image.open(img)
        
    image_array = np.array(image)
    if image.mode != 'RGB':
        image = image.convert('RGB')
        image_array = np.array(image)

    proccesed_img = await correction(image_array)
    result_image = Image.fromarray(proccesed_img)

    img_byte_arr = io.BytesIO()
    result_image.save(img_byte_arr, format=img.mimetype.split('/')[1].upper())
    base64_bytes = base64.b64encode(img_byte_arr.getvalue())
    
    base64_string = base64_bytes.decode('ascii')    

    return jsonify({'base64': base64_string})



@app.route("/", methods=["GET"])
async def index():
    return render_template('index.html')


if __name__ == "__main__":
    # Run the app on local host and port 8989
    app.run(debug=True, host="0.0.0.0", port=8989)