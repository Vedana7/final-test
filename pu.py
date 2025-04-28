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
           rect = json.load(f)
   except:
       pass
   
   API_TOKEN = ''
   
   bot = telebot.TeleBot(API_TOKEN)
   
   # rect : [ [[x, y], color, photofile, name, type, height, desiases, mest, comment, beholder_name, phonenumber], ]
   
   state = {} # {id: state}  # 1-photo 2-name 3-type 4-height 5-болезни 6-местоположение 7-видовые особенности 8-имя наблюдателя 9-телефон 10-цвет
   tree_data = {} # {id: []}
   
   kw = {
       "fill": True,
       "weight": 5
   }
   colors_states = {1:'red', 2:'orange', 3:'green'}
   
   def create_treecard(tree):
       img = Image.open("tree0.png")
       draw = ImageDraw.Draw(img)
       font = ImageFont.truetype("arial.ttf", 100)
       draw.text((1400, 650), tree[3], (0,0,0), font=font)
       draw.text((1400, 920), tree[4], (0,0,0), font=font)
       draw.text((1500, 1200), tree[5], (0,0,0), font=font)
       draw.text((1350, 1450), tree[7], (0,0,0), font=font)
       draw.text((1000, 1730), tree[6], (0,0,0), font=font)
       draw.text((1250, 2000), tree[8], (0,0,0), font=font)
       draw.text((1500, 2400), tree[9], (0,0,0), font=font)
       draw.text((1000, 2620), tree[10], (0,0,0), font=font)
   
       treephoto = Image.open(tree[2])
       treephoto = treephoto.resize((535, int(treephoto.size[1] * float(535 / float(treephoto.size[0])))), Image.Resampling.LANCZOS)
       img.paste(treephoto, (504, 568))


img.save('card.png')
    return 'card.png'

def create_table(rect):
    with open('table.csv', 'w', encoding='utf8') as f:
        print('Координаты;Фотография;Имя;Вид;Высота;Болезни;Адрес;Видовые особенности;Имя наблюдаеля;Телефон', file=f)
        for i in rect:
            print(f'{i[0][0]}, {i[0][1]};{i[2]};{i[3]};{i[4]};{i[5]};{i[6]};{i[7]};{i[8]};{i[9]};{i[10]}', file=f)
    read_file = pd.read_csv('table.csv', delimiter=';')
    read_file.to_excel('table.xlsx', index=None, header=True)

def create_map(rectangles):
    m = folium.Map(location=[54.371258, 86.117834], zoom_start=7, tiles='OpenStreetMap')

    for rectangle in rectangles:
        folium.Marker(rectangle[0], icon=folium.Icon(rectangle[1])).add_to(m)
    
    img_data = m._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    width, height = img.size
    left = 60
    top = 0
    right = width
    bottom = height - 20
    im1 = img.crop((left, top, right, bottom))
    im1.save('image.png')
    return 


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '''Привет!
Команды:
map - показать карту
add - добавить дерево
table - показать таблицу с данными всех деревьев
''')

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "Отправьте геолокацию дерева")
    

@bot.message_handler(commands=['map'])
def send_map(message):
    create_map(rect)
    with open('image.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands=['table'])
def send_table(message):
    create_table(rect)
    with open("table.xlsx","rb") as f:
        bot.send_document(message.chat.id,f)

@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        tree_data[str(message.chat.id)] = [[message.location.latitude, message.location.longitude], '']
        state[str(message.chat.id)] = 1
        bot.send_message(message.chat.id, "Отправьте фотографию дерева (не как файл)")



























































































