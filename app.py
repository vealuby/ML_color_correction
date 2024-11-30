from flask import Flask, jsonify, request, render_template, send_file, after_this_request
import os
from ColorCorrection import *
from random import randint

import base64

app = Flask(__name__)

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

@app.route("/api/correct_video", methods=["POST"])
async def correct_video():

    video_file = request.files['video']
    etalon_file = request.files['etalon']


    temp_filename = 'temp/temp%d.mp4' % randint(0, 5000)
    video_file.save(temp_filename)
    
    etalon = Image.open(etalon_file)
    etalon_array = np.array(etalon)

    video_path = await video_change(cv2.cvtColor(etalon_array, cv2.COLOR_RGB2BGR), temp_filename, False)
    # video_path = temp_filename
    return jsonify({'link': '%s_corrected.mp4' % video_path.split('.')[0] })


@app.route("/", methods=["GET"])
async def index():
    return render_template('index.html')

@app.route("/video", methods=["GET"])
async def video_index():
    return render_template('video_index.html')

@app.route('/temp/<filename>/')
async def download(filename):

    return_data = io.BytesIO()
    try:
        with open('temp/%s' % filename, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)
    except:
        return render_template('video_index.html')

    try:
        os.remove('temp/%s' % filename)
        os.remove('temp/%s' % filename.replace('_corrected', ''))
    except Exception as e:
        print(e)

    return send_file(return_data, mimetype='video/mp4',
                     download_name='processed_video.mp4', as_attachment=True)


if __name__ == "__main__":
    # Run the app on local host and port 8989
    app.run(debug=True, host="0.0.0.0", port=8989)