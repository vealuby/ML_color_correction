import cv2
import numpy as np
import io
import matplotlib.pyplot as plt
from PIL import Image
from skimage.io import imread, imshow
from skimage import img_as_ubyte
from skimage.color import rgb2gray
from skimage.exposure import histogram, cumulative_distribution
from scipy.stats import cauchy, logistic
import asyncio

# Подстраивает изображения друг под друга
async def color_transfer(source, target):
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")
    # print(np.std(source),np.std(target))

    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = await image_stats(source)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = await image_stats(target)
    # subtract the means from the target image
    (l, a, b) = cv2.split(target)
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar
    # scale by the standard deviations
    # print((lStdTar ,lStdSrc), aStdTar / aStdSrc, bStdTar / bStdSrc)
    l = (lStdTar / lStdSrc) * l
    a = (aStdTar / aStdSrc) * a
    b = (bStdTar / bStdSrc) * b
    # add in the source mean
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc
    # clip the pixel intensities to [0, 255] if they fall outside
    # this range
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)
    # merge the channels together and convert back to the RGB color
    # space, being sure to utilize the 8-bit unsigned integer data
    # type
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    # return the color transferred image
    return transfer


# Вычисление параметров изображения
async def image_stats(image):
    # compute the mean and standard deviation of each channel
    (l, a, b) = cv2.split(image)
    (lMean, lStd) = (l.mean(), l.std())
    (aMean, aStd) = (a.mean(), a.std())
    (bMean, bStd) = (b.mean(), b.std())
    # return the color statistics
    return (lMean, lStd, aMean, aStd, bMean, bStd)


# Изменение каналов в зависимости от распределения
async def individual_channel(image, dist, channel):
    im_channel = img_as_ubyte(image[:,:,channel])
    uniq_list = np.unique(im_channel)
    freq, bins = cumulative_distribution(im_channel)
    new_vals = np.interp(freq, dist.cdf(np.arange(0,256)),
                               np.arange(0,256))
    # print(new_vals.shape)
    return new_vals[im_channel-uniq_list[0]].astype(np.uint8)

# Изменение изображения на основе его распределения
async def change_mean(img,func,mean,std):
    dist = func(mean, std)

    red = await individual_channel(img, dist, 0)
    green = await individual_channel(img, dist, 1)
    blue = await individual_channel(img, dist, 2)

    out_img = np.dstack([red, green, blue])

    return out_img



async def CLAHE(img):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
    b,g,r = cv2.split(img)
    clahe = cv2.createCLAHE(clipLimit = 0.8, tileGridSize=(10, 10))
    max_val = np.max(np.unique(b))
    b_glare = np.where(b < max_val * 0.6, 0, 10)
    #b -= b_glare
    # print(b_glare.shape,np.)
    b = clahe.apply(b)
    g = clahe.apply(g)
    r = clahe.apply(r)

    result = cv2.merge((b,g,r))
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    # print(b.shape,np.unique(b))
    return result

async def convert_to_rgb(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


async def change_main_img(source,color):
    img_mean = np.mean(source)
    img_var = np.std(source)
    if color:
        new_img = await change_mean(source, cauchy, img_mean * 0.5, img_var * 0.3)
        new_img = await convert_to_rgb(new_img)
        return new_img
    else:
        source = await CLAHE(source)
        source = await convert_to_rgb(source)
        return source

async def color_change(source, target, color):
    new_img = await color_transfer(source, target)
    img_mean = np.mean(new_img)
    img_var = np.std(new_img)
    if color:
        new_img = await change_mean(new_img, cauchy, img_mean * 0.6, img_var * 0.5)
    else:
        new_img = await CLAHE(new_img)
    new_img = await convert_to_rgb(new_img)
    return new_img

async def video_change(source, video_path, color):

    video = cv2.VideoCapture(video_path)
    format_video = 'mp4'

    fourcc = int(video.get(cv2.CAP_PROP_FOURCC))
    fps = video.get(cv2.CAP_PROP_FPS)
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_video = cv2.VideoWriter('%s_corrected.mp4' % video_path.split('.')[0], fourcc, 30, (w, h))

    while True:
        ret, frame = video.read()
        if not ret:
            break

        new_frame = await color_change(source, frame, color)
        # center = (int(w / 2), int(h / 2))
        # rotation_matrix = cv2.getRotationMatrix2D(center, 180, 1)
        # rotated = cv2.warpAffine(new_frame, rotation_matrix, (w, h))
        new_frame = await convert_to_rgb(new_frame)
        output_video.write(new_frame)

    video.release()
    output_video.release()

    return video_path
