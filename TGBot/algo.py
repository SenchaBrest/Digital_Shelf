# print("Hello, world!") имба не контрится

from PIL import Image, ImageDraw, ImageFont

img = Image.open('images/image.jpg')

color = {"odd": [255, 0, 0],
         "already in row": [0, 255, 0],
         "void": [0, 0, 0],
         "column": [255, 0, 255],
         '0': [0, 255, 0],
         '1': [255, 0, 0],
         '2': [0, 0, 255],
         '3': [0, 255, 255]}


def drawBoxPIL(box, pencil, size, color=None, label=None, line_thickness=None):
    line_thickness = line_thickness or max(int(min(size) / 200), 2)
    pencil.rectangle(box, width=line_thickness, outline=tuple(color))  # plot
    if label:
        fontsize = max(round(max(img.size) / 40), 12)
        font = ImageFont.load_default()
        txt_width, txt_height = font.getsize(label)
        pencil.rectangle([box[0], box[1] - txt_height + 4, box[0] + txt_width, box[1]], fill=tuple(color))
        pencil.text((box[0], box[1] - txt_height + 1), label, fill=(255, 255, 255), font=font)


def createImage(mistake):
    pw, ph = img.size
    pencil = ImageDraw.Draw(img)
    drawBoxPIL([mistake.x * pw, mistake.y * ph, (mistake.x + mistake.w) * pw, (mistake.y + mistake.h) * ph],
               pencil, img.size,
               color=color[mistake.tag],
               label=mistake.tag, line_thickness=3)


K = 0.1  # коэффициент точности определения полок (0.5 / max кол-во полок)
PRISE_LEN = 7.1  # реальная длина ценника в см


def clear():
    shelves_h.clear()
    prices_pos.clear()
    products_pos.clear()
    products_length.clear()
    mistakes.clear()
    prices.clear()
    products.clear()
    Product.clear()


class Product:
    tags = {}
    left = 1.
    right = 0.

    def __init__(self, tag, x, y, w, h):
        self.tag = tag
        self.x = x - w / 2
        self.y = y - h / 2
        self.w = w
        self.h = h
        if tag != "mistake":
            Product.left = min(Product.left, self.x)
            Product.right = max(Product.right, self.x + self.w)

            if not self.tags.get(tag):
                self.tags[tag] = 1
            else:
                self.tags[tag] += 1

    def show(self):
        print(f"{self.tag} {self.x} {self.y} {self.w} {self.h}")

    @staticmethod
    def clear():
        Product.tags.clear()
        Product.left = 1.
        Product.right = 0.


class Price:
    tags = {}

    def __init__(self, tag, x, y, w, h):
        self.tag = "Ценники без скидки" if tag == '0' else "Ценники со скидкой"
        self.x = x - w / 2
        self.y = y - h / 2
        self.w = w
        self.h = h
        if not self.tags.get(self.tag):
            self.tags[self.tag] = 1
        else:
            self.tags[self.tag] += 1

    def show(self):
        print(f"{self.tag} {self.x} {self.y} {self.w} {self.h}")


class Mistake:
    def __init__(self, tag, x, y, w, h):
        self.tag = tag
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def show(self):
        print(f"{self.tag} {self.x} {self.y} {self.w} {self.h}")


shelves_h = []
prices_pos = []
products_pos = []
products_length = []
mistakes = []
prices = []  # лист ценников
products = []  # лист продуктов
mask = []


def preparePhoto(labelOfPrices, labelOfProducts):
    file = open(labelOfPrices, 'r')
    for line in file:
        li = line.split(" ")
        temp = Price(li[0], float(li[1]),
                     float(li[2]),
                     float(li[3]),
                     float(li[4]))
        prices.append(temp)
    file.close()

    file = open(labelOfProducts, 'r')
    for line in file:
        li = line.split(" ")
        temp = Product(li[0], float(li[1]),
                       float(li[2]),
                       float(li[3]),
                       float(li[4]))
        products.append(temp)
    file.close()


# число полок
def calcShelvesCount():
    if not prices:
        return 0
    prices.sort(key=lambda obj: obj.y)
    shelves_h.append(prices[0].y)
    for i in range(len(prices) - 1):
        if abs(prices[i].y - prices[i + 1].y) > K:
            shelves_h.append(prices[i + 1].y)
    # print(f"amount of shelves - {len(shelves_h)}")
    # print("calcShelvesCount", shelves_h)

    return len(shelves_h), shelves_h


# заполняем полки ценниками (в индексах!)
def fillShelvesByPrices():
    global prices_pos
    prices_pos = [[] for _ in range(len(shelves_h))]
    prices.sort(key=lambda obj: obj.x)
    for i in range(len(prices)):
        for j in range(len(shelves_h)):
            if abs(shelves_h[j] - prices[i].y) < K:
                prices_pos[len(shelves_h) - 1 - j].append(i)
    # print("fillShelvesByPrices", prices_pos)
    return prices_pos


# заполняем полки продуктами (в индексах!)
def fillShelvesByProducts():
    global products_pos
    products_pos = [[] for _ in range(len(shelves_h))]
    products.sort(key=lambda obj: obj.x)
    temp = [0] + shelves_h
    for i in range(len(products)):
        for j in range(len(temp) - 1):
            if temp[j] < products[i].y < temp[j + 1]:
                if not products_pos[j]:
                    products_pos[j].append([i])
                elif (abs(products[products_pos[j][-1][-1]].x - products[i].x) <
                      products[i].w / 2):
                    products_pos[j][-1].append(i)
                else:

                    products_pos[j].append([i])
                break

    # print("fillShelvesByProducts:", products_pos)
    return products_pos


# длина выкладки
def calcLengthOfLayout():
    global products_length
    products_length = [[] for _ in range(len(shelves_h))]
    for i in range(len(shelves_h)):
        if not products_pos[i]:  # пропускаем пустые полки
            continue
        j = 0
        size = len(products_pos[i]) - 1
        while j < size:
            j += 1

            length = products[products_pos[i][j - 1][0]].w
            amount = 1
            while (products[products_pos[i][j - 1][0]].tag == products[products_pos[i][j][0]].tag and
                   j < size):
                # если продукты друг на друге - пропускаем
                if (abs(products[products_pos[i][j - 1][0]].x - products[products_pos[i][j][0]].x) <
                        products[products_pos[i][j][0]].w / 2):
                    j += 1
                    continue
                length += products[products_pos[i][j - 1][0]].w
                amount += 1
                j += 1
            products_length[i].append([products[products_pos[i][j - 1][0]].tag, length, amount])
        if products[products_pos[i][size - 1][0]].tag == products[products_pos[i][-1][0]].tag:
            products_length[i][len(products_length[i]) - 1][1] += products[products_pos[i][size - 2][0]].w
            products_length[i][len(products_length[i]) - 1][2] += 1
        else:
            products_length[i].append([products[products_pos[i][-1][0]].tag,
                                       products[products_pos[i][-1][0]].w, 1])
    # print("calcLengthOfLayout", products_length)

    for i in range(len(shelves_h)):  # в бота
        # print(f"{i + 1} shelf:")
        for length in products_length[i]:
            # print(f"{' ' * 9}{length[0]} class: {round(length[1] / prices[0].w * PRISE_LEN)} cm")
            length[1] = round(length[1] / prices[0].w * PRISE_LEN)

    return products_length


# количество видов продуктов
def calcTagsCount():
    # for tag in Product.tags:
    #     print(f"Class {tag} - {Product.tags[tag]} products")
    return Product.tags


# количество видов ценников
def calcPricesCount():
    # for tag in Price.tags:
    #     print(f"{tag}: {Price.tags[tag]}")
    return Price.tags


# проверка на пустоту
def findVoids():
    def isMistake(productA, productB):  # B правее чем A
        voidLength = productB.x - (productA.x + productA.w)
        if voidLength >= productB.w / 2:
            mistakes.append(Mistake(
                "void",  # type of mistake
                productA.x + productA.w,  # x
                productA.y,  # y
                voidLength,  # width
                productA.h))  # height

    for i in range(len(shelves_h)):
        if not products_pos[i]:
            continue
        isMistake(Product('mistake', Product.left, products[products_pos[i][0][0]].y +
                          products[products_pos[i][0][0]].h / 2, 0, products[products_pos[i][0][0]].h),
                  products[products_pos[i][0][0]]
                  )
        for j in range(len(products_pos[i]) - 1):
            isMistake(products[products_pos[i][j][0]], products[products_pos[i][j + 1][0]])
        isMistake(products[products_pos[i][-1][0]],
                  Product('mistake', Product.right + products[products_pos[i][-1][0]].w / 2, 0,
                          products[products_pos[i][-1][0]].w, 0)
                  )

    # print(len(mistakes), "mistakes: ")
    # for q in mistakes:
    #     q.show()

    for q in mistakes:
        createImage(q)
    img.save("photo.jpg")

    return "photo.jpg"


# формируем словарь-маску
def createMask():
    for i in range(len(shelves_h)):
        mask.append([])
        temp_tags = []  # встреченные теги
        index = 0
        for j in range(len(products_pos[i])):
            mask[i].append([])
            for cur_pos in products_pos[i][j]:
                if not products[cur_pos].tag in temp_tags:  # если не встречался
                    temp_tags.append(products[cur_pos].tag)
                    mask[i][j].append(index)
                    index += 1
                else:  # если встречался
                    input_index = temp_tags.index(products[cur_pos].tag)
                    mask[i][j].append(input_index)


# поиск ошибок выкладки
def findMistakes():
    createMask()

    # есть ли ошибка в колонке продуктов
    def checkColumnMistake(i, j):
        h = len(mask[i][j])  # количество продуктов друг на друге
        if h != 1:  # если продукты друг на друге
            for k in range(h - 1):
                if mask[i][j][k] != mask[i][j][k + 1]:
                    minY = min(products[products_pos[i][j][c]].y for c in range(h))
                    maxY, hMaxY = max(
                        (products[products_pos[i][j][c]].y, products[products_pos[i][j][c]].h) for c in range(h))
                    mistakes.append(Mistake(
                        "column",  # type of mistake
                        products[products_pos[i][j][-1]].x,  # x
                        minY,  # y
                        products[products_pos[i][j][0]].w,  # width
                        maxY + hMaxY - minY  # height
                    ))
                    break

    for i in range(len(mask)):
        if not mask[i]:
            continue
        checkColumnMistake(i, 0)  # проверяем первый
        for j in range(1, len(mask[i]) - 1):
            checkColumnMistake(i, j)
            if mask[i][j][0] > mask[i][j + 1][0]:  # ошибка в ряду в [j] или [j + 1]
                if (mask[i][j - 1][0] == mask[i][j + 1][0] and  # ==> ошибка в [j]
                        len([item for item in mask[i] if item[0] == mask[i][j - 1][0]])):
                    mistakes.append(Mistake(
                        "odd",  # type of mistake
                        products[products_pos[i][j][0]].x,  # x
                        products[products_pos[i][j][0]].y,  # y
                        products[products_pos[i][j][0]].w,  # width
                        products[products_pos[i][j][0]].h  # height
                    ))
                else:
                    ml = 1
                    saveX = products[products_pos[i][j + 1][0]].x
                    while (j < len(mask[i]) - 2 and
                           mask[i][j + 1][0] == mask[i][j + 2][0]):
                        j += 1
                        ml += 1
                    mistakes.append(Mistake(
                        "already in row",  # type of mistake
                        saveX,  # x
                        products[products_pos[i][j + 1][0]].y,  # y
                        products[products_pos[i][j + 1][0]].w * ml,  # width
                        products[products_pos[i][j + 1][0]].h  # height
                    ))
        checkColumnMistake(i, -1)  # проверяем последний

    for mistake in mistakes:
        createImage(mistake)
    img.save("errors.jpg")


# проверка на нахождение друг в друге
def isInEachOther(productA, productB):
    minArea = min(productA.w * productA.h, productB.w * productB.h)
    width = min(productA.x + productA.w, productB.x + productB.w) - max(productA.x, productB.x)
    height = min(productA.y + productA.h, productB.y + productB.h) - max(productA.y, productB.y)
    intersection = width * height
    if intersection > 2 * minArea:
        pass


preparePhoto(labelOfPrices='labels/prices.txt', labelOfProducts='labels/products.txt')

# for q in products:
#     createImage(q)
# img.save("temp.jpg")

calcShelvesCount()

fillShelvesByPrices()
fillShelvesByProducts()

calcLengthOfLayout()
calcTagsCount()
calcPricesCount()

findVoids()
findMistakes()
