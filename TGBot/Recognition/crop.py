import random
import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def crop(photo, labels, directory = "Recognition/merge"):
    def calc_angle(x1, y1, x2, y2):
        return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi


    def get_matrix_of_angels(kp1, kp2, matches):
        angles = []
        for i in range(50 if len(matches) > 50 else len(matches)):
            angles.append(calc_angle(int(kp1[matches[i].queryIdx].pt[0]),
                                     int(kp1[matches[i].queryIdx].pt[1]),
                                     int(kp2[matches[i].trainIdx].pt[0]) + 224,
                                     int(kp2[matches[i].trainIdx].pt[1])))
        return np.array(angles)

    def get_kontrol_angel(angles):
        return np.mean((angles - np.mean(angles)) ** 2)

    def match_objects(des1, des2):
        bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        return matches

    def create_object_to_detect(path):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(img, None)
        return img, kp, des


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
        color = [random.randint(10, 255) for _ in range(3)]
        for filename in os.listdir(path):
            path = f"{directory}/{dirname}/{filename}"
            Image.open(path).resize((224, 224)).save(path)
            _, kp2, des2 = create_object_to_detect(path)
            examples.append([dirname, color, (kp2, des2)])

    data = []
    products = df.to_numpy()
    for i, elem in enumerate(products):
        x_l = (elem[1] - elem[3] / 2) * photoWidth
        y_l = (elem[2] - elem[4] / 2) * photoHeight
        x_r = (elem[1] + elem[3] / 2) * photoWidth
        y_r = (elem[2] + elem[4] / 2) * photoHeight
        img.crop((x_l, y_l, x_r, y_r)).resize((224, 224)).save(f"Recognition/crops/{i}.jpg")

        _, kp1, des1 = create_object_to_detect(f"Recognition/crops/{i}.jpg")

        koefs = []
        for j in range(len(examples)):
            kp2 = examples[j][2][0]
            des2 = examples[j][2][1]
            koefs.append([get_kontrol_angel(get_matrix_of_angels(kp1, kp2, match_objects(des1, des2))), j])
        koefs = sorted(koefs)
        print(koefs[0][0])
        name = examples[koefs[0][1]][0]
        color = examples[koefs[0][1]][1]

        data.append(f"{name} {elem[1]} {elem[2]} {elem[3]} {elem[4]}\n")

        plot_one_box_PIL([x_l, y_l, x_r, y_r], pencil, img.size, color=color,
                         label=f"{str(name).replace('.jpg', '')}", line_thickness=3)

    with open(f"res_rec_obj.txt", "w") as f:
        for dt in data:
            f.write(dt)

    img.save("res_rec_obj.jpg")
    return "res_rec_obj.jpg"