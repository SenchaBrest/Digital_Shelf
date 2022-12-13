import random
import os
import pandas as pd
import time
from PIL import Image, ImageDraw, ImageFont
from sift import get_kp, get_matrix_of_angels, get_kontrol_angel, create_object_to_detect, match_objects

t = time.time()
photo = "valid-objects/20.jpg"
directory = "merge"

labels = "detect_res/objects/labels/20.txt"


def plot_one_box_PIL(box, pencil, size, color=None, label=None, line_thickness=None):
    line_thickness = line_thickness or max(int(min(size) / 200), 2)
    pencil.rectangle(box, width=line_thickness, outline=tuple(color))
    if label:
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
    color = [random.randint(0, 255) for _ in range(3)]
    for filename in os.listdir(path):
        path = f"{directory}/{dirname}/{filename}"
        Image.open(path).resize((224, 224)).save(path)
        _, kp2, des2 = create_object_to_detect(path)
        print(path)
        #examples.append([dirname, color, get_kp(path)])
        examples.append([dirname, color, (kp2, des2)])


products = df.to_numpy()
for i, elem in enumerate(products):
    x_l = (elem[1] - elem[3] / 2) * photoWidth
    y_l = (elem[2] - elem[4] / 2) * photoHeight
    x_r = (elem[1] + elem[3] / 2) * photoWidth
    y_r = (elem[2] + elem[4] / 2) * photoHeight
    img.crop((x_l, y_l, x_r, y_r)).resize((224, 224)).save(f"crops/{i}.jpg")

    _, kp1, des1 = create_object_to_detect(f"crops/{i}.jpg")

    koefs = []
    for j in range(len(examples)):
        kp2 = examples[j][2][0]
        des2 = examples[j][2][1]
        koefs.append([get_kontrol_angel(get_matrix_of_angels(kp1, kp2, match_objects(des1, des2))), j])
    koefs = sorted(koefs)
    print(koefs[0][0])
    name = examples[koefs[0][1]][0]
    color = examples[koefs[0][1]][1]

    with open(f"results.txt", "a") as f:
        f.write(f"{name} {x_l / photoWidth} {y_l / photoHeight} {x_r / photoWidth} {y_r / photoHeight}\n")

    plot_one_box_PIL([x_l, y_l, x_r, y_r], pencil, img.size, color=color,
                     label=f"{str(name).replace('.jpg', '')}", line_thickness=3)

img.show()
print(time.time() - t)