import telebot
import pyautogui
from os import system
import cv2
import time
import torch
import sounddevice as sd
from time import sleep

device = torch.device('cpu')
def load_model():
    global model
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='v3_1_ru' )
model = model.to(device)

def speak(text, speaker='random'):
    global model
    simple_rate = 48000
    
    put_accent = True
    put_yoo = True


    language=language

    audio = model.apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=simple_rate,
        put_accent=put_accent,
        put_yo=put_yoo
    )

    print(text)

    sd.play(audio, simple_rate)
    sleep((len(audio) / simple_rate) + 0.3)
    sd.stop()
load_model()
# Инициализация бота
bot = telebot.TeleBot('TOKEN')
bot.send_message(1346243726, 'ПК запущен')

#aidar, baya, xenia, random
speaker = 'random'

@bot.message_handler(commands=['start'])
def func(message):
    bot.send_message(message.chat.id, 'Команды:\n'
                     '/move x y\n'
                     '/off\n'
                     '/restart\n'
                     '/next\n'
                     '/screen\n'
                     '/click\n'
                     '/write\n'
                     '/camera\n'
                     '/stream\n'
                     '/stop\n'
                     '/speak\n'
                     '/set_speaker'
                     )

@bot.message_handler(commands=['move'])
def func(message):
    try:
        coordinates = message.text.split()[1:]
        x, y = map(int, coordinates)
        pyautogui.moveTo(x, y)

        bot.send_message(message.chat.id, f'Перемещение мыши к ({x}, {y}) выполнено.')
    except: bot.send_message(message.chat.id, f'He выполнено.')

@bot.message_handler(commands=['off'])
def func(message):
    bot.send_message(message.chat.id, f'ПК выключается')
    system('shutdown /s /t 0')

@bot.message_handler(commands=['restart'])
def func(message):
    bot.send_message(message.chat.id, f'ПК перезагружается')
    system('shutdown /r /t 0')

@bot.message_handler(commands=['next'])
def func(message):
    bot.send_message(message.chat.id, f'Выполнено')
    pyautogui.hotkey('alt', 'tab')

@bot.message_handler(commands=['screen'])
def func(message):
    screenshot = pyautogui.screenshot()
    bot.send_photo(message.chat.id, screenshot)

@bot.message_handler(commands=['click'])
def func(message):
    bot.send_message(message.chat.id, f'Выполнено')
    pyautogui.click()

@bot.message_handler(commands=['write'])
def func(message):
    try:
        text = ' '.join(message.text.split()[1:])
        pyautogui.write(text)

        bot.send_message(message.chat.id, f'Выполнено')
    except: bot.send_message(message.chat.id, f'He выполнено.')

@bot.message_handler(commands=['camera'])
def func(message):
    try:
        cap = cv2.VideoCapture(0)
        for _ in range(10): cap.read()
        _, frame = cap.read()

        _, encoded_img = cv2.imencode('.jpg', frame)
        frame_bytes = encoded_img.tobytes()

        bot.send_photo(message.chat.id, frame_bytes)
        cap.release()
    except:
        bot.send_message(message.chat.id, f'Камера не подключена')

is_streaming = False

@bot.message_handler(commands=['stream'])
def func(message):
    try:
        global is_streaming

        if not is_streaming:
            is_streaming = True
            try: cap = cv2.VideoCapture(0)
            except: bot.send_message(message.chat.id, f'Камера не подключена'); return
            for _ in range(25): cap.read()
            _, frame = cap.read()
            _, encoded_img = cv2.imencode('.jpg', frame)
            frame_bytes = encoded_img.tobytes()

            image = bot.send_photo(message.chat.id, frame_bytes)
            while is_streaming:
                _, frame = cap.read()
                _, encoded_img = cv2.imencode('.jpg', frame)
                frame_bytes = encoded_img.tobytes()

                bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media=frame_bytes), chat_id=message.chat.id, message_id=image.message_id)
                time.sleep(0.3)

            cap.release()
    except: is_streaming = False

@bot.message_handler(commands=['stop'])
def func(message):
    global is_streaming
    is_streaming = False

@bot.message_handler(commands=['speak'])
def func(message):
    try:
        text = ' '.join(message.text.split()[1:])
        if text!='':
            print(text)
            speak(text, speaker)
            bot.send_message(message.chat.id, f'Выполнено')
        else: bot.send_message(message.chat.id, f'Введите текст')
    except: bot.send_message(message.chat.id, f'Введите текст')


@bot.message_handler(commands=['set_speaker'])
def func(message):
    global speaker
    try:
        text = ' '.join(message.text.split()[1:])
        if text!='':
            speaker=text
            bot.send_message(message.chat.id, f'Выполнено')
        else: bot.send_message(message.chat.id, f'aidar, baya, xenia, random')
    except: bot.send_message(message.chat.id, f'aidar, baya, xenia, random')
    



bot.polling(none_stop=True)
