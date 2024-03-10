from typing import List, Optional, Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from pydub import AudioSegment # voice conversion
import itertools
import os # PATH
import cv2 # face detection from OpenCV
#import subprocess

_counter = itertools.count() # counter for the voice messages

def main(args: Optional[List[str]] = None) -> int:
    from pip._internal.utils.entrypoints import _wrapper
    return _wrapper(args)

TOKEN: Final = '7053023228:AAGp6AeX6iYNdfOuGV6b3pazV_HdxevSAMk'
BOT_USERNAME: Final = '@MitWavBot'
PATH2UID: Final = 'C://Users/ra_bd/Desktop/'

# Commands and help-functions
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply-text('Hi! I am a MitBot!')

def check_folder_exists(PATH: str):
    if not os.path.exists(PATH):
        os.makedirs(PATH)

#Responses
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.voice.file_unique_id
    uid = update.message.chat.id
    print(f'New voice message is detected, User {uid}')
    new_file = await update.message.voice.get_file()
    check_folder_exists(PATH2UID+f'{uid}')
    order = next(_counter)
    # Voice conversion
    await new_file.download_to_drive(PATH2UID + f'Temporal/{uid}' + '.ogg')
    audio = AudioSegment.from_file(PATH2UID + f'Temporal/{uid}' + '.ogg',
            format="ogg", frame_rate=44100)
    audio = audio.set_frame_rate(16000)
    audio.export(PATH2UID + f'{uid}/{uid}' + '_' + str(order)
                 +".wav", format="wav")
    os.remove(PATH2UID + f'Temporal/{uid}' + '.ogg')


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = (update.message.photo[-1].file_unique_id)
    new_file = await update.message.effective_attachment[-1].get_file()
    uid = update.message.chat.id
    print(f'New image is detected, User {uid}')

    # Temp file, face detection
    file = await (new_file.download_to_drive(PATH2UID + f'Temporal/{file_id}' + '.jpg'))

    # Face detection using OpenCV
    img = cv2.imread(PATH2UID + f'Temporal/{file_id}' + '.jpg')
    img.shape
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_image.shape
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    face = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    if len(face) > 0:
        print('Some faces are detected. Saving the file..')
        check_folder_exists(PATH2UID + f'{uid}')
        file = await (new_file.download_to_drive(PATH2UID
                      + f'{uid}/{file_id}' + '.jpg'))
    os.remove(PATH2UID + f'Temporal/{file_id}' + '.jpg')


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')

if __name__ == '__main__':

    print('Starting bot..')
    app = Application.builder().token(TOKEN).build()

    # Command
    app.add_handler(CommandHandler('start', start_command))

    # Messages
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling..')
    app.run_polling(poll_interval=3)