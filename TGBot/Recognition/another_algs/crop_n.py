import random
import os
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
import tensorflow_hub as hub
from scipy.spatial import distance


model_path = "efficientnet_lite0_feature-vector_2"
metric = 'cosine'

# correlation
# cosine
# yule
# dice

IMAGE_SHAPE = (224, 224)
layer = hub.KerasLayer(model_path)
model = tf.keras.Sequential([layer])


def extract(file):
    file = Image.open(file).convert('L').resize(IMAGE_SHAPE)

    file = np.stack((file,) * 3, axis=-1)
    file = np.array(file) / 255.0

    embedding = model.predict(file[np.newaxis, ...])
    vgg16_feature_np = np.array(embedding)
    flattened_feature = vgg16_feature_np.flatten()

    return flattened_feature


def compare(obj1, obj2):
    return distance.cdist([obj1], [obj2], metric)


photo = "photos/1.jpg"
directory = "products_photo"

labels = f"detect_res/objects/labels/1.txt"


def plot_one_box_PIL(box, pencil, size, color=None, label=None, line_thickness=None):
    line_thickness = line_thickness or max(int(min(size) / 200), 2)
    pencil.rectangle(box, width=line_thickness, outline=tuple(color))  # plot
    if label:
        fontsize = max(round(max(img.size) / 40), 12)
        font = ImageFont.load_default()
        txt_width, txt_height = font.getsize(label)
        pencil.rectangle([box[0], box[1] - txt_height + 4, box[0] + txt_width, box[1]], fill=tuple(color))
        pencil.text((box[0], box[1] - txt_height + 1), label, fill=(255, 255, 255), font=font)


df = pd.read_csv(f"{labels}", delimiter=' ',
                 names=['class', 'x', 'y', 'w', 'h'])


img = Image.open(f'{photo}')
photoWidth, photoHeight = img.size
pencil = ImageDraw.Draw(img)

examples = []
for dirname in os.listdir(directory):
    path = f"{directory}/{dirname}"
    examples.append([dirname, [random.randint(0, 255) for _ in range(3)], []])
    for filename in os.listdir(path):

        path = f"{directory}/{dirname}/{filename}"
        a = Image.open(path)
        resized = a.resize((224, 224))
        resized.save(f"{path}")
        examples[-1][2].append(extract(path))


products = df.to_numpy()
for i, elem in enumerate(products):
    x_left = (elem[1]-elem[3]/2) * photoWidth
    y_left = (elem[2]-elem[4]/2) * photoHeight
    x_right = (elem[1]+elem[3]/2) * photoWidth
    y_right = (elem[2]+elem[4]/2) * photoHeight

    img.crop((x_left, y_left, x_right, y_right)).resize((224, 224)).save(f"crops/{i}.jpg")

    crop_photo = extract(f"crops/{i}.jpg")

    min = 1
    for example in enumerate(examples):
        print(example)
        koefs = []
        for i in range(4):
            koefs.append(compare(crop_photo, example[1][2][0]))
        koef = np.mean(koefs)
        if koef < min:
            min = koef
            name = example[1][0]
            color = example[1][1]
    if min < 0.3:
        with open(f"results.txt", "a") as f:
            f.write(f"{name} {x_left / photoWidth} {y_left / photoHeight} {x_right / photoWidth} {y_right / photoHeight}\n")

        plot_one_box_PIL([x_left, y_left, x_right, y_right], pencil, img.size, color=color, \
                         label=f"{str(name).replace('.jpg', '')}", line_thickness=3)

img.show()