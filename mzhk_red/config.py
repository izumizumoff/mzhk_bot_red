# config data for mzhk_bot
import json
import requests
import vk_api
import random

with open('vk_token.json', 'r') as token:
    VK_TOKEN = json.load(token)["token"]

def device_turn(command):
    session = vk_api.VkApi(token=VK_TOKEN)
    session.method('messages.send', {'user_id': 000000000, 'message': command, 'random_id': random.randint(0,1024)})


def random_face():
    img = 'https://thispersondoesnotexist.com/image'
    p = requests.get(img)
    with open('random_face.jpg', 'wb') as pic:
        pic.write(p.content)

with open('token.json', 'r') as token:
    API_TOKEN = json.load(token)["token"]

ADMIN_ID = 000000000

CLIP_ID = 'BAACAgIAAxkBAAIXiGFPf0AO3R5UuVlsWDtZKj-3zZXMAAITDQACaKqBSuLh1dSQ3LESIQQ'


with open('authors', 'r', encoding='UTF-8') as file:
    AUTHORS = file.read()

with open('start', 'r', encoding='UTF-8') as file:
    START_MESSAGE = file.readlines()

with open('id_play', 'r', encoding='UTF-8') as file:
    ID_PLAY = file.read()

with open('intro.json', 'r', encoding='UTF-8') as file:
    INTRO_MESSSAGE = json.load(file)

with open('inside.json', 'r', encoding='UTF-8') as file:
    INSIDE_MESSSAGE = json.load(file)

with open('kitchen', 'r') as file:
    KITCHEN_MESSAGE = file.read()

with open('kitchen_photo', 'r') as file:
    KITCHEN_PHOTO = file.read()

with open('big_room', 'r') as file:
    BIGROOM_MESSAGE = file.read()

with open('bigroom_final', 'r') as file:
    BIGROOM_FINAL_MESSAGE = file.read()

with open('kabinet.json', 'r') as file:
    KABINET_MESSAGE = json.load(file)

with open('part_3.json', 'r', encoding='UTF-8') as file:
    PART3_MESSSAGE = json.load(file)

with open('final.json', 'r', encoding='UTF-8') as file:
    FINAL_MESSSAGE = json.load(file)

with open('anekdot', 'r') as file:
    ANEKDOT_MESSAGE = file.read()