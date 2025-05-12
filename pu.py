import telebot
import folium
import io
from PIL import Image
import selenium
import json
import pandas as pd
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from check_swear import SwearingCheck

rect = []

try:
    with open('data.json', encoding='utf8') as f:
        rect = json.load(f)  # загружаем данные из файла data.json
except:
    pass

API_TOKEN = ''

bot = telebot.TeleBot(API_TOKEN)

# rect : [ [[x, y], color, photofile, name, type, height, desiases, mest, comment, beholder_name, phonenumber], ]

state = {}  # словарь для хранения состояния пользователя {id: state}  # 1-photo 2-name 3-type 4-height 5-болезни 6-местоположение 7-видовые особенности 8-имя наблюдателя 9-телефон 10-цвет
tree_data = {}  # словарь для хранения данных о деревьях {id: []}

kw = {
    "fill": True,
    "weight": 5
}
colors_states = {1: 'red', 2: 'orange', 3: 'green'}

def create_treecard(tree):
    img = Image.open("tree0.png")  # открываем изображение для карточки дерева
    draw = ImageDraw.Draw(img)  # создаем объект для рисования на изображении
    font = ImageFont.truetype("arial.ttf", 100)  # загружаем шрифт для текста
    draw.text((1400, 650), tree[3], (0, 0, 0), font=font)  # добавляем имя дерева
    draw.text((1400, 920), tree[4], (0, 0, 0), font=font)  # добавляем вид дерева
    draw.text((1500, 1200), tree[5], (0, 0, 0), font=font)  # добавляем высоту дерева
    draw.text((1350, 1450), tree[7], (0, 0, 0), font=font)  # добавляем болезни дерева
    draw.text((1000, 1730), tree[6], (0, 0, 0), font=font)  # добавляем местоположение дерева
    draw.text((1250, 2000), tree[8], (0, 0, 0), font=font)  # добавляем видовые особенности
    draw.text((1500, 2400), tree[9], (0, 0, 0), font=font)  # добавляем имя наблюдателя
    draw.text((1000, 2620), tree[10], (0, 0, 0), font=font)  # добавляем телефон наблюдателя

    treephoto = Image.open(tree[2])  # открываем фотографию дерева
    treephoto = treephoto.resize((535, int(treephoto.size[1] * float(535 / float(treephoto.size[0])))), Image.Resampling.LANCZOS)  # изменяем размер фотографии
    img.paste(treephoto, (504, 568))  # вставляем фотографию на карточку

    img.save('card.png')  # сохраняем карточку дерева
    return 'card.png'

def create_table(rect):
    with open('table.csv', 'w', encoding='utf8') as f:
        print('координаты;фотография;имя;вид;высота;болезни;адрес;видовые особенности;имя наблюдателя;телефон', file=f)  # записываем заголовки в файл
        for i in rect:
            print(f'{i[0][0]}, {i[0][1]};{i[2]};{i[3]};{i[4]};{i[5]};{i[6]};{i[7]};{i[8]};{i[9]};{i[10]}', file=f)  # записываем данные о деревьях
    read_file = pd.read_csv('table.csv', delimiter=';')  # читаем данные из CSV файла
    read_file.to_excel('table.xlsx', index=None, header=True)  # сохраняем данные в Excel файл

def create_map(rectangles):
    m = folium.Map(location=[54.371258, 86.117834], zoom_start=7, tiles='OpenStreetMap')  # создаем карту


    for rectangle in rectangles:
    folium.Marker(rectangle[0], icon=folium.Icon(rectangle[1])).add_to(m)  # добавляем маркеры на карту

img_data = m._to_png(5)  # получаем изображение карты в формате PNG
img = Image.open(io.BytesIO(img_data))  # открываем изображение карты
width, height = img.size  # получаем размеры изображения
left = 60
top = 0
right = width
bottom = height - 20
im1 = img.crop((left, top, right, bottom))  # обрезаем изображение
im1.save('image.png')  # сохраняем обрезанное изображение
return

# команды
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '''привет!
команды:
map - показать карту
add - добавить дерево
table - показать таблицу с данными всех деревьев
problem - сообщить о проблеме
''')

@bot.message_handler(commands=['problem'])
def report_problem(message):
    bot.send_message(message.chat.id, "опишите вашу проблему")  # запрашиваем описание проблемы
    state[str(message.chat.id)] = 'problem_description'  # устанавливаем состояние

@bot.message_handler(func=lambda message: state.get(str(message.chat.id)) == 'problem_description')
def get_problem_description(message):
    tree_data[str(message.chat.id)] = [message.text]  # сохраняем описание проблемы
    bot.send_message(message.chat.id, "пожалуйста, введите ваш email для обратной связи.")  # запрашиваем email
    state[str(message.chat.id)] = 'problem_email'  # устанавливаем состояние

@bot.message_handler(func=lambda message: state.get(str(message.chat.id)) == 'problem_email')
def get_problem_email(message):
    if "@" in message.text and "." in message.text:  # проверяем формат email
        tree_data[str(message.chat.id)].append(message.text)  # сохраняем email
        bot.send_message(message.chat.id, "спасибо! мы рассмотрим вашу проблему и свяжемся с вами по email")  # подтверждаем получение

        state.pop(str(message.chat.id))  # очищаем состояние
        tree_data.pop(str(message.chat.id))  # очищаем данные о дереве
    else:
        bot.send_message(message.chat.id, "неверный формат email. пожалуйста, введите корректный email")  # сообщаем об ошибке

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "отправьте геолокацию дерева")  # запрашиваем геолокацию

@bot.message_handler(commands=['map'])
def send_map(message):
    create_map(rect)  # создаем карту
    with open('image.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)  # отправляем карту пользователю

@bot.message_handler(commands=['table'])
def send_table(message):
    create_table(rect)  # создаем таблицу
    with open("table.xlsx", "rb") as f:
        bot.send_document(message.chat.id, f)  # отправляем таблицу пользователю

@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:  # проверяем, что получена геолокация
        tree_data[str(message.chat.id)] = [[message.location.latitude, message.location.longitude], '']  # сохраняем координаты
        state[str(message.chat.id)] = 1  # устанавливаем состояние
        bot.send_message(message.chat.id, "отправьте фотографию дерева (не как файл)")  # запрашиваем фотографию

@bot.message_handler(content_types=['photo'])
def photo(message):
    if state[str(message.chat.id)] == 1:  # проверяем состояние
        fileID = message.photo[-1].file_id  # получаем ID фотографии
        file_info = bot.get_file(fileID)  # получаем информацию о файле
        downloaded_file = bot.download_file(file_info.file_path)  # загружаем файл
        with open(str(fileID) + ".jpg", 'wb') as new_file:
            new_file.write(downloaded_file)  # сохраняем файл
        tree_data[str(message.chat.id)].append(str(fileID) + ".jpg")  # добавляем путь к фотографии в данные
        state[str(message.chat.id)] = 2  # устанавливаем следующее состояние
        bot.send_message(message.chat.id, "отправьте имя дерева")  # запрашиваем имя дерева

@bot.message_handler(content_types=['text'])
def text(message):
    sch = SwearingCheck()  # создаем объект для проверки ненормативной лексики
    if sch.predict(message.text) == [1]:  # проверяем, есть ли ненормативная лексика
        bot.send_message(message.chat.id, "недопустимые выражения в сообщении")  # уведомляем пользователя
    else:
        if state[str(message.chat.id)] == 2:  # если состояние 2
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем имя дерева
            state[str(message.chat.id)] = 3  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте вид дерева")  # запрашиваем вид дерева
        elif state[str(message.chat.id)] == 3:  # если состояние 3
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем вид дерева
            state[str(message.chat.id)] = 4  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте примерную высоту дерева")  # запрашиваем высоту
        elif state[str(message.chat.id)] == 4:  # если состояние 4
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем высоту дерева
            state[str(message.chat.id)] = 5  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте болезни дерева")  # запрашиваем болезни
        elif state[str(message.chat.id)] == 5:  # если состояние 5
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем болезни
            state[str(message.chat.id)] = 6  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте местоположение дерева")  # запрашиваем местоположение
        elif state[str(message.chat.id)] == 6:  # если состояние 6
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем местоположение
            state[str(message.chat.id)] = 7  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте видовые особенности дерева")  # запрашиваем видовые особенности
        elif state[str(message.chat.id)] == 7:  # если состояние 7
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем видовые особенности
            state[str(message.chat.id)] = 8  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте ваше имя")  # запрашиваем имя
        elif state[str(message.chat.id)] == 8:  # если состояние 8
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем имя
            state[str(message.chat.id)] = 9  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "отправьте ваш телефон")  # запрашиваем телефон
        elif state[str(message.chat.id)] == 9:  # если состояние 9
            tree_data[str(message.chat.id)].append(message.text)  # сохраняем телефон
            state[str(message.chat.id)] = 10  # переходим к следующему состоянию
            bot.send_message(message.chat.id, "оцените состояние дерева от 1 до 3")  # запрашиваем оценку состояния
        elif state[str(message.chat.id)] == 10:  # если состояние 10
            tree_data[str(message.chat.id)][1] = colors_states[int(message.text)]  # сохраняем цвет состояния дерева
            rect.append(tree_data[str(message.chat.id)])  # добавляем данные о дереве в список
            with open('data.json', 'w', encoding='utf8') as f:
                json.dump(rect, f, ensure_ascii=False)  # сохраняем данные в файл
            bot.send_message(message.chat.id, "добавляю дерево")  # уведомляем пользователя

            create_treecard(rect[-1])  # создаем карточку дерева
            with open('card.png', 'rb') as card:
                bot.send_photo(message.chat.id, card)  # отправляем карточку пользователю

bot.infinity_polling()  # запускаем бесконечный опрос для получения сообщений
