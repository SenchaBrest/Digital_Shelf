import cv2
import numpy as np
import pickle
import os


def set_kp(kp, des, path):
    to_save = []
    for pt in kp:
        to_save.append((pt.pt,
                        pt.size,
                        pt.angle,
                        pt.response,
                        pt.octave,
                        pt.class_id))
    to_save.append(des)

    file = open(path, 'wb')
    pickle.dump(to_save, file)
    file.close()


def get_kp(path):
    file = open(path, 'rb')
    data = pickle.load(file)
    file.close()

    kp = []
    for pt in data:
        try:
            kp.append(cv2.KeyPoint(x=pt[0][0], y=pt[0][1],
                                   size=pt[1], angle=pt[2],
                                   response=pt[3],
                                   octave=pt[4],
                                   class_id=pt[5]))
        except:
            pass
    des = data[-1]

    return kp, des


def calc_angle(x1, y1, x2, y2):
    return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi


def vector_from_coordenates(coord):
    return np.array([coord[2] - coord[0], coord[3] - coord[1]])


def vector_multiplication_of_vectors(kp1, kp2, matches):
    coord = []
    for i in range(50 if len(matches) > 50 else len(matches)):
        coord.append([int(kp1[matches[i].queryIdx].pt[0]),
                      int(kp1[matches[i].queryIdx].pt[1]),
                      int(kp2[matches[i].trainIdx].pt[0]) + 224,
                      int(kp2[matches[i].trainIdx].pt[1])])
    coord = np.array(coord)

    vs = []
    for i in range(0, len(coord) - 1, 2):
        vs.append(np.sqrt((coord[i][2] - coord[i][0]) ** 2 + (coord[i][3] - coord[i][1]) ** 2) *
                  np.sqrt((coord[i + 1][2] - coord[i + 1][0]) ** 2 + (coord[i + 1][3] - coord[i + 1][1]) ** 2) *
                  np.sin(np.arctan2(coord[i][3] - coord[i][1], coord[i][2] - coord[i][0]) -
                         np.arctan2(coord[i + 1][3] - coord[i + 1][1], coord[i + 1][2] - coord[i + 1][0])))
    vs = np.array(vs)
    return np.sqrt(np.mean(vs ** 2))


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


def create_files_of_db(list_of_paths):
    for path in list_of_paths:
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(img, None)
        set_kp(kp, des, path.replace(".jpg", ".pkl"))


def create_object_to_detect(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    kp, des = sift.detectAndCompute(img, None)
    return img, kp, des


def match_objects(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches


def show(img1, kp1, img2, kp2, matches):
    matched_img = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], img2, flags=2)
    cv2.imshow("img", matched_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# img1, kp1, des1 = create_object_to_detect("products/3/34.jpg")
# img2, kp2, des2 = create_object_to_detect("products/3/23.jpg")

# show(img1, kp1, img2, kp2, match_objects(des1, des2))

def main():
    directory = "products_pkl"

    paths = []
    for dirname in os.listdir(directory):
        path = f"{directory}/{dirname}"
        for filename in os.listdir(path):
            paths.append(f"{directory}/{dirname}/{filename}")

    create_files_of_db(paths)


if __name__ == "__main__":
    main()
