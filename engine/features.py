from shlex import quote
import subprocess
from playsound import playsound
import eel
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
import os
import pywhatkit as kit
import re
import sqlite3
import webbrowser
from engine.helper import extract_yt_term, remove_words
import pyaudio
import pvporcupine
import time
import struct
from hugchat import hugchat
from engine.prompts import generate_prompt, clean_response


con = sqlite3.connect("jarvis.db")
cursor = con.cursor()


@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
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
    speak("Playing "+search_term+" on youtube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis"], sensitivities=[1.0]) 
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


# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])

        # Validate the mobile number format
        mobile_number_str = str(results[0][0]).strip()
        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str
        
        # Ensure the number is numeric and has the correct length
        if not re.match(r'^\+91\d{10}$', mobile_number_str):
            raise ValueError(f"Invalid phone number format: {mobile_number_str}")
        
        return mobile_number_str, query

    except:
        speak('not exist in contacts')
        return 0, 0


def whatsApp(mobile_no, message, flag, name):

    if flag == 'message':
        target_tab = 15
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 13
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 11
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    
    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)



def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine/cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    
    # Generate the prompt based on the query content
    prompt = generate_prompt(user_input)
    response = chatbot.chat(prompt)
    clean_text = clean_response(response)

    print(clean_text)
    speak(clean_text)
    return clean_text


# android automation
def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(417, 2211)
    #start chat
    tapEvents(917, 2204)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(313, 694)
    # tap on input
    tapEvents(523, 2271)
    #message
    adbInput(message)
    #send
    tapEvents(966, 1385)
    speak("message send successfully to "+name)


def openCamera():
    from engine.helper import goback, keyEvent
    speak("Opening camera")
    
    # Go back to the home screen and clear any open apps
    goback(4)
    time.sleep(1)
    keyEvent(3)
    
    command = 'adb shell am start -a android.media.action.IMAGE_CAPTURE'
    os.system(command)

    
