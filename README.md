# Цифровая полка

### Наш продукт 
Цифровая полка должна стать помощником мерчендайзеров при анализе стеллажей магазина и\
структурировании полученной информации.

### Содержание <a name="desc"></a> 
* [Почему?](#why)
* [Основные функции](#func)
* [Схема распознования](#diagram)
* [Пример работы](#example)
* [Установка приложения](#download)

### Почему? <a name="why"></a> 
1. Работы человека без приложения занимает много времени
2. Скучный, рутинный подсчет может выполнить приложение
3. Пока наше приложение работает, человек получает результат



### Основные функции <a name="func"></a> 
- [X]	Определение количества ценников акционной и не акционной продукции
- [X]	Определение количества продуктов
- [X]	Определение количества полок на фотографии
- [X]	Определение длины выкладки продукции
- [X]	Определение вида продукта
- [ ]	Определение ошибки выкладки продуктов
- [ ]	Определение неполных полок 
- [ ]	Определение цен продукции
- [ ] Помощь в исправлении ошибок выкладки работникам магазина
- [ ]	Робот, занимающийся сбором информации о содержимом полок магазина автономно



### Схема распознования <a name="diagram"></a>

```mermaid
flowchart TB
  A(получаем изображение) --> B(нейросеть определяет\n расположение и вид ценников)
  B --> C(нейросеть определяет\n расположение объектов)
  C --> D(отсеивание ошибочных данных\n расположения объектов)
  D --> E(определение типов объектов)
  E --> F(работа алгоритмов)
  F --> G(отправка результатов)
```



### Пример работы <a name="example"></a>

### Установка приложения <a name="download"></a>
По умолчанию наш проект работает на архитектуре yolov5, поэтому следуя нижепреведенным инструкциям вы будете использровать именно ее.

```bash
git clone https://github.com/SenchaBrest/Digital_Shelf.git
```

```bash
pip install -r requirements.txt
```
Для скачивания весов пройдите по ссылке: [weights](https://github.com/SenchaBrest/Digital_Shelf/releases/tag/weights-yolov5).

#
Если вы хотите обучить самостоятельно, возьмите архивы фотографий [здесь](https://github.com/SenchaBrest/Digital_Shelf/releases/tag/Datasets).

#
Если вы хотите использовать программу на архитектуре yolov7, вам потребуется самостоятельно [склонировать](https://github.com/WongKinYiu/yolov7).
После этого вы можете скачать наш проект в файле zip и распаковать его в склонированном репозитории.
Для yolov7 веса находятся [здесь](https://github.com/SenchaBrest/Digital_Shelf/releases/tag/weights-yolov7).

#
[назад к содержанию](#desc)




