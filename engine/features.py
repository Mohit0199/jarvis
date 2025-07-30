from shlex import quote
import subprocess
from playsound import playsound
import eel
from engine.command import speak
from engine.config import ASSISTANT_NAME
import os
import pywhatkit as kit
import re
import sqlite3
import webbrowser
from engine.helper import extract_yt_term, remove_words
import pvporcupine
import time
from engine.prompts import generate_prompt, clean_response
import ollama
import pvporcupine
from pvrecorder import PvRecorder
import pyautogui as autogui
import time
from dotenv import load_dotenv
import pyautogui

load_dotenv()

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
    if search_term is None:
        speak("Sorry, I couldn't find the song name in your query.")
        return
    speak("Playing "+search_term+" on youtube")
    kit.playonyt(search_term)


def hotword():
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        raise ValueError("PICOVOICE_ACCESS_KEY environment variable is not set.")
    
    porcupine = None
    recorder = None
    
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis"],
            sensitivities=[0.5]
        )
        
        recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
        recorder.start()
        
        print("🎙️ Listening for 'Jarvis'...")
        
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("✅ Hotword detected!")
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except KeyboardInterrupt:
        print("Stopped by user.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if recorder is not None:
            recorder.stop()
            recorder.delete()
        if porcupine is not None:
            porcupine.delete()



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

    # Create the prompt using your existing function
    prompt = generate_prompt(user_input)

    # Use Ollama library to chat with local model
    response = ollama.chat(
        model='qwen2.5:latest',   # change this if using another model (e.g. mistral, gemma)
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and clean response
    clean_text = clean_response(response['message']['content'])

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

    
