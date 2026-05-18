# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)


from compileall import compile_path
import google.generativeai as genai
import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3

from backend.helper import extract_yt_term, remove_words
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()
# Gemini AI Setup
genai.configure(api_key="AIzaSyDIwdcpf6zRr9RBb04HG-a4Wq-4kIa-JFY")

model = genai.GenerativeModel("gemini-pro")

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = r"C:\Users\Asus\Documents\Jarvis-2025-master\frontend\assets\audio\start_sound.mp3"  
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query.lower()
    
    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):

    if flag == 'message':

        speak("Sending message to " + name)

        kit.sendwhatmsg_instantly(
            Phone,
            message,
            wait_time=15,
            tab_close=True
        )

    elif flag == 'call':

        speak("Opening WhatsApp call")
        webbrowser.open(f"https://wa.me/{Phone}")

    else:

        speak("Opening WhatsApp video call")
        webbrowser.open(f"https://wa.me/{Phone}")

def chatBot(query):

    query = query.lower()

    try:

        if "hello" in query:
            response = "Hello Vikas, how can I help you"

        elif "how are you" in query:
            response = "I am fine sir"

        elif "your name" in query:
            response = "I am Jarvis"

        elif "youtube" in query:
            response = "Opening YouTube"
            webbrowser.open("https://youtube.com")

        elif "google" in query:
            response = "Opening Google"
            webbrowser.open("https://google.com")

        elif "whatsapp" in query:
            response = "Opening WhatsApp"
            webbrowser.open("https://web.whatsapp.com")

        else:
            ai_response = model.generate_content(query)
            response = ai_response.text

        print(response)
        speak(response)
        return response

    except Exception as e:
        print("Gemini Error:", e)
        speak("Sorry Vikas, AI is not working properly")

