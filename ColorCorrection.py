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
    # Конвертируем изображения в формат LAB
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    # Вычисляем статистические параметры для каждого канала
    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = await image_stats(source)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = await image_stats(target)

    # Получаем каналы из обрабатываемого изображения
    (l, a, b) = cv2.split(target)

    # Обнуляем среднее
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar
    # Подстраиваем стандартное отклонение под целевое изображение
    l = (lStdTar / lStdSrc) * l
    a = (aStdTar / aStdSrc) * a
    b = (bStdTar / bStdSrc) * b
    # Подстраиваем среднее под целевое изображение
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc
    # Приводим значения к диапазону [0, 255]
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)
    # Объединяем каналы и переводим изображение в RGB формат
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    return transfer


# Функция вычисления параметров изображения
async def image_stats(image):
    # Разделяем каналы изображения
    (l, a, b) = cv2.split(image)
    # Для каждого канала вычисляются среднее и стандартное отклонение
    (lMean, lStd) = (l.mean(), l.std())
    (aMean, aStd) = (a.mean(), a.std())
    (bMean, bStd) = (b.mean(), b.std())
    # return the color statistics
    return (lMean, lStd, aMean, aStd, bMean, bStd)


# Функция для выравнивания контраста каналов
async def individual_channel(image, dist, channel):
    # Выбираем канал для обработки
    im_channel = img_as_ubyte(image[:, :, channel])
    # Находим уникальные значения
    uniq_list = np.unique(im_channel)
    # Вычисляем распределение канала
    freq, bins = cumulative_distribution(im_channel)
    # Интерполяция данных
    new_vals = np.interp(freq,
                         dist.cdf(np.arange(0, 256)),
                         np.arange(0, 256))
    # Выравнивание контрастности
    return new_vals[im_channel-uniq_list[0]].astype(np.uint8)


# Функция для выравнивания контраста изображения
async def change_mean(img, func, mean, std):
    # Распределение для выравнивания
    dist = func(mean, std)
    # Выравнивание контраста каналов
    red = await individual_channel(img, dist, 0)
    green = await individual_channel(img, dist, 1)
    blue = await individual_channel(img, dist, 2)
    # Формирование нового изображения
    out_img = np.dstack([red, green, blue])

    return out_img


# Функция для адаптивного выравнивания контраста
async def CLAHE(img):
    # Конвертация изображения в формат LAB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    # Разбиение по каналам
    b, g, r = cv2.split(img)
    # Инициализация класса метода CLAHE
    clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(10, 10))

    # Применение выравнивания контраста
    b = clahe.apply(b)
    g = clahe.apply(g)
    r = clahe.apply(r)

    # Формирование выходного изображения
    result = cv2.merge((b, g, r))
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

    return result


# Функция для конвертации изображений в RGB
async def convert_to_rgb(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


# Функция для изменения основного изображения
async def change_main_img(source, color):
    # Вычисление статистических параметров
    img_mean = np.mean(source)
    img_var = np.std(source)
    # Проверка на тип изображения
    if color:
        # Выравнивание контраста несбалансированного изображения
        new_img = await change_mean(source, cauchy, img_mean * 0.5, img_var * 0.3)
        new_img = await convert_to_rgb(new_img)
        return new_img
    else:
        # Выравнивание контраста сбалансированного изображения
        source = await CLAHE(source)
        source = await convert_to_rgb(source)
        return source


# Функция изменения цвета изображения
async def color_change(source, target, color):
    # Цветокоррекция изображений
    new_img = await color_transfer(source, target)
    # Вычисление статистических параметров скореектированного изображения
    img_mean = np.mean(new_img)
    img_var = np.std(new_img)
    # Выравнивание контраста
    if color:
        new_img = await change_mean(new_img, cauchy, img_mean * 0.6, img_var * 0.5)
    else:
        new_img = await CLAHE(new_img)
    # Конвертация в RGB
    new_img = await convert_to_rgb(new_img)
    return new_img


# Функция изменения цвета видео
async def video_change(source, video_path, color):
    # Считывание видео
    video = cv2.VideoCapture(video_path)
    # Получение метаданных о видео
    fourcc = int(video.get(cv2.CAP_PROP_FOURCC))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # Перезапись видео
    output_video = cv2.VideoWriter('%s_corrected.mp4' % video_path.split('.')[0], fourcc, 30, (w, h))

    # Цикл для обхода кадров видео
    while True:
        # Получение кадров видео
        ret, frame = video.read()
        if not ret:
            break
        # Цветокоррекция кадров
        new_frame = await color_change(source, frame, color)
        # Конвертация в RGB формат
        new_frame = await convert_to_rgb(new_frame)
        # Перезапись видео
        output_video.write(new_frame)

    # Сохранение видео
    video.release()
    output_video.release()

    return video_path
