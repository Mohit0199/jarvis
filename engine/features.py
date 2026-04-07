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


def wait_for_speech():
    """Block until all queued voice clips have finished playing."""
    import engine.command
    while not engine.command.tts_queue.empty() or engine.command.fetcher_busy or not engine.command.play_queue.empty():
        if engine.command.stop_speaking_flag:
            return
        eel.sleep(0.1)
    try:
        while pygame.mixer.music.get_busy():
            if engine.command.stop_speaking_flag:
                return
            eel.sleep(0.1)
    except:
        pass


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
                wait_for_speech()
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    wait_for_speech()
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    wait_for_speech()
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
    speak("Playing "+search_term)
    wait_for_speech()
    kit.playonyt(search_term)


def hotword():
    import openwakeword
    from openwakeword.model import Model
    import pyaudio
    import numpy as np

    # Download models on first run
    openwakeword.utils.download_models()

    # Load the 'hey jarvis' wake word model with ONNX
    oww_model = Model(
        wakeword_models=["hey_jarvis_v0.1"],
        inference_framework="onnx"
    )

    print("Loaded wake word models:", list(oww_model.models.keys()))

    # Setup microphone stream
    audio = pyaudio.PyAudio()
    CHUNK = 1280  # openwakeword expects 80ms of 16kHz audio = 1280 samples
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("⏳ Warming up wake word engine...")

    # Warmup: feed ~3 seconds of audio to fill the model's internal buffer
    warmup_frames = int(3 * RATE / CHUNK)  # 3 seconds worth
    for _ in range(warmup_frames):
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        oww_model.predict(audio_array)
    oww_model.reset()

    print("🎙️ Listening for 'Hey Jarvis'... (Ready!)")

    THRESHOLD = 0.5       # Raised from 0.08 — prevents false triggers on background noise
    COOLDOWN_SEC = 3      # Minimum seconds between valid detections
    last_detected = 0

    try:
        while True:
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            prediction = oww_model.predict(audio_array)

            for model_name, score in prediction.items():
                now = time.time()
                if score > THRESHOLD and (now - last_detected) > COOLDOWN_SEC:
                    print(f"✅ Wake word detected! ({model_name}: {score:.2f})")
                    last_detected = now
                    oww_model.reset()
                    autogui.keyDown("win")
                    autogui.press("j")
                    time.sleep(2)
                    autogui.keyUp("win")

    except KeyboardInterrupt:
        print("Stopped by user.")

    except Exception as e:
        print(f"Error in hotword: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()



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




# ─── Conversation Memory ───
# Persists across all chatBot() calls for the lifetime of the session.
# Stores dicts: {"role": "user"/"assistant", "content": "..."}
conversation_history = []


def clear_memory():
    """Wipes Jarvis's conversation history. Call this on 'forget' / 'reset' commands."""
    global conversation_history
    conversation_history = []
    print("🧹 Conversation history cleared.")


def chatBot(query):
    global conversation_history

    # Tell UI to initialize a new streaming text bubble + show thinking animation
    try:
        eel.receiverTextStreamInit()
        eel.ShowThinkingAnimation()
        eel.sleep(0.5)
    except Exception as e:
        print("Eel stream init failed", e)

    # Build messages: system prompt + history + current query
    messages = generate_prompt(query, conversation_history)
    print(f"🧠 Memory: {len(conversation_history)//2} exchanges in context")

    # Use Ollama library to stream chat with local model
    response_stream = ollama.chat(
        model='qwen2.5:latest',
        messages=messages,
        stream=True
    )

    import engine.command
    # Reset the sync flag so we wait for the first clip to start playing
    engine.command.first_audio_playing = False
    
    sentence_buffer = ""
    full_text = ""
    first_chunk_sent = False
    ui_buffer = []        # Buffer tokens until voice starts
    voice_started = False # Flipped True once first audio clip begins playing

    for chunk in response_stream:
        # Check if user hit the stop button to abort LLM generation halfway!
        if engine.command.stop_speaking_flag:
            break
            
        token = chunk['message'].get('content', '')
        if not token:
            continue
        
        sentence_buffer += token
        full_text += token
        
        # ─── UI TEXT SYNC ───
        # Buffer tokens silently until the first voice clip starts playing.
        # Then flush all buffered tokens at once so text + voice start together.
        if not voice_started:
            ui_buffer.append(token)
            
            # Check if audio player has started the first clip
            if engine.command.first_audio_playing:
                voice_started = True
                print("🔄 Voice started! Flushing buffered text to UI...")
                try:
                    eel.HideThinkingAnimation()
                    for buffered_token in ui_buffer:
                        formatted = buffered_token.replace('\n', '<br>')
                        eel.receiverTextStreamChunk(formatted)
                    eel.sleep(0.02)
                except:
                    pass
                ui_buffer = []
        else:
            # Voice is already playing — stream tokens to UI in real-time
            try:
                formatted_token = token.replace('\n', '<br>')
                eel.receiverTextStreamChunk(formatted_token)
                eel.sleep(0.02)
            except:
                pass
        
        # ─── TTS DISPATCH ───
        # FIRST CHUNK: dispatch ASAP (3+ words on ANY punctuation)
        # LATER CHUNKS: sentence-ending (.?!) always; clause punct (,;:) needs 8+ words
        should_dispatch = False
        word_count = len(sentence_buffer.split())
        
        if not first_chunk_sent:
            if any(p in token for p in ['.', '?', '!', ',', ';', ':']) and word_count >= 3:
                should_dispatch = True
        else:
            if any(p in token for p in ['.', '?', '!']):
                should_dispatch = True
            elif any(p in token for p in [',', ';', ':']) and word_count >= 8:
                should_dispatch = True
        
        if should_dispatch:
            clean_sentence = clean_response(sentence_buffer).strip()
            if clean_sentence:
                print(f"🗣️ TTS chunk ({len(clean_sentence.split())} words): {clean_sentence[:60]}...")
                speak(clean_sentence)
                first_chunk_sent = True
            sentence_buffer = ""

    # Flush any remaining text in buffer
    if sentence_buffer.strip():
        clean_sentence = clean_response(sentence_buffer).strip()
        if clean_sentence:
            print(f"🗣️ TTS final chunk: {clean_sentence[:60]}...")
            speak(clean_sentence)
    
    # If voice never started (e.g. very short response), flush UI buffer anyway
    if ui_buffer:
        try:
            eel.HideThinkingAnimation()
            for buffered_token in ui_buffer:
                formatted = buffered_token.replace('\n', '<br>')
                eel.receiverTextStreamChunk(formatted)
            eel.sleep(0.02)
        except:
            pass
    
    # ─── Save to Memory ───
    # Only save if we got a meaningful response and weren't interrupted
    final_response = clean_response(full_text)
    if final_response and not engine.command.stop_speaking_flag:
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": final_response})
        # Cap memory at 10 exchanges (20 messages)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        print(f"💾 Memory updated: {len(conversation_history)//2} exchanges stored")

    return final_response




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

    
