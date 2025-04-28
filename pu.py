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




























































































