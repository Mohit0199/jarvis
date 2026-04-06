import speech_recognition as sr
import eel
import time
import re
import traceback
import os
import sys
import tempfile
import pygame

# ─── CRITICAL: Use _thread (real OS threads) instead of threading ───
# gevent.monkey.patch_all() in main.py converts threading.Thread into
# cooperative gevent greenlets. That means our TTS fetcher's subprocess.run()
# blocks the ENTIRE event loop, starving the audio player of CPU time.
# _thread creates REAL preemptive OS threads that gevent cannot touch.
import _thread
import queue
import subprocess

tts_queue = queue.Queue()
play_queue = queue.Queue()
stop_speaking_flag = False
first_audio_playing = False  # Sync flag: set True when first voice clip starts playing
fetcher_busy = False         # True while fetcher is downloading an MP3

# Resolve edge-tts path once at startup (absolute path, avoids CWD issues)
EDGE_TTS_EXE = os.path.join(os.path.dirname(sys.executable), "edge-tts.exe")
if not os.path.exists(EDGE_TTS_EXE):
    # Fallback: might be in venv/Scripts
    EDGE_TTS_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "venv", "Scripts", "edge-tts.exe")
    EDGE_TTS_EXE = os.path.normpath(EDGE_TTS_EXE)

print(f"🔧 Edge-TTS binary: {EDGE_TTS_EXE} (exists: {os.path.exists(EDGE_TTS_EXE)})")

try:
    pygame.mixer.init()
    print("🎵 Pygame mixer initialized OK")
except Exception as e:
    print(f"⚠️ Pygame mixer init failed: {e}")

@eel.expose
def stop_speak():
    global stop_speaking_flag
    stop_speaking_flag = True
    print("🛑 Stop requested!")
    
    # Purge BOTH queues safely
    with tts_queue.mutex:
        tts_queue.queue.clear()
        
    with play_queue.mutex:
        for f in list(play_queue.queue):
            try: os.remove(f)
            except: pass
        play_queue.queue.clear()
        
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"Stop error: {e}")

def _tts_fetcher_fn():
    """REAL OS thread: pulls text from tts_queue, downloads MP3 via edge-tts subprocess, pushes to play_queue."""
    global stop_speaking_flag
    
    while True:
        try:
            text = tts_queue.get(timeout=1)
        except queue.Empty:
            continue
        
        if text is None:
            break
            
        if stop_speaking_flag:
            continue
            
        try:
            global fetcher_busy
            fetcher_busy = True
            temp_file = os.path.join(tempfile.gettempdir(), f"jarvis_voice_{int(time.time() * 1000)}.mp3")
            print(f"🔊 Fetching voice for: {text[:40]}...")
            
            result = subprocess.run([
                EDGE_TTS_EXE,
                "--text", text,
                "--voice", "en-GB-RyanNeural",
                "--rate", "+15%",
                "--write-media", temp_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=15)
            
            if result.returncode != 0:
                print(f"❌ edge-tts failed (code {result.returncode}): {result.stderr.decode(errors='ignore')[:200]}")
                continue
                
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                print(f"❌ MP3 file missing or empty: {temp_file}")
                continue
            
            if stop_speaking_flag:
                try: os.remove(temp_file) 
                except: pass
                continue
            
            print(f"✅ MP3 ready, pushing to play queue: {os.path.basename(temp_file)}")
            play_queue.put(temp_file)
            
        except Exception as e:
            print(f"❌ TTS FetchError: {e}")
            traceback.print_exc()
        finally:
            fetcher_busy = False

def _audio_player_fn():
    """REAL OS thread: pulls MP3 files from play_queue and plays them sequentially via pygame."""
    global stop_speaking_flag
    
    print("🎧 Audio player thread started!")
    
    while True:
        try:
            temp_file = play_queue.get(timeout=1)
        except queue.Empty:
            continue

        if temp_file is None:
            break
            
        if stop_speaking_flag:
            try: os.remove(temp_file) 
            except: pass
            continue
            
        try:
            print(f"▶️ Playing: {os.path.basename(temp_file)}")
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Signal to chatBot() that voice has started — it can now flush buffered text
            global first_audio_playing
            first_audio_playing = True
            
            while pygame.mixer.music.get_busy():
                if stop_speaking_flag:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.05)
                
            try:
                pygame.mixer.music.unload()
                os.remove(temp_file)
            except:
                pass
            
            print(f"⏹️ Finished playing clip")
                        
        except Exception as e:
            print(f"❌ Audio PlayError: {e}")
            traceback.print_exc()

# Start BOTH workers as REAL OS threads (bypasses gevent monkey-patching!)
_thread.start_new_thread(_tts_fetcher_fn, ())
_thread.start_new_thread(_audio_player_fn, ())

def speak(text):
    global stop_speaking_flag
    stop_speaking_flag = False
    
    text = str(text).strip()
    if not text:
        return

    try:
        eel.ShowStopBtn()
    except:
        pass
        
    tts_queue.put(text)

def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.ShowUserQuery('listening....')
        r.pause_threshold = 0.8
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=15, phrase_time_limit=10)

    try:
        # Try Google STT first (fast, accurate, free, needs internet)
        print('recognizing with Google...')
        eel.ShowUserQuery('recognizing....')
        query = r.recognize_google(audio, language='en-US')
        print(f"user said: {query}")
        eel.ShowUserQuery(query)
        
    except Exception as google_error:
        try:
            # Fallback to Whisper (offline, slower but reliable)
            print(f'Google failed ({google_error}), trying Whisper...')
            eel.ShowUserQuery('recognizing (offline)....')
            query = r.recognize_whisper(audio, model="small", language="english")
            print(f"user said: {query}")
            eel.ShowUserQuery(query)
        except Exception as e:
            print(f"Recognition error: {e}")
            return ""
    
    return query.lower()


@eel.expose
def allCommands(message=1):
    print(f"📡 [BACKEND] allCommands triggered from frontend with message: {message}")
    import threading

    def _process_command():
        print("⚡ [BACKEND] _process_command greenlet spawned!")
        try:
            if message == 1:
                query = takecommand()
                print(query)
                eel.senderText(query)
            else:
                query = message
                print(f"💬 [BACKEND] user query received: {query}")
                eel.senderText(query)
                eel.ShowUserQuery(query)

            # Force Gevent to flush the WebSocket so the frontend updates instantly!
            # Otherwise the heavy `ollama.chat` completely freezes the event loop.
            eel.sleep(0.5)

            if "open" in query:
                from engine.features import openCommand
                openCommand(query)

            elif ("on youtube" in query) or ("from youtube" in query) or ("play" in query):
                from engine.features import PlayYoutube
                PlayYoutube(query)

            elif "send message" in query or "phone call" in query or "video call" in query:
                from engine.features import findContact, whatsApp, makeCall, sendMessage
                contact_no, name = findContact(query)
                if(contact_no != 0):
                    speak("Which mode you want to use whatsapp or mobile")
                    preferance = takecommand()
                    print(preferance)

                    if "mobile" in preferance:
                        if "send message" in query or "send sms" in query: 
                            speak("what message to send")
                            msg = takecommand()
                            sendMessage(msg, contact_no, name)
                        elif "phone call" in query:
                            makeCall(name, contact_no)
                        else:
                            speak("please try again")

                    elif "whatsapp" in preferance:
                        msg_type = ""
                        if "send message" in query:
                            msg_type = 'message'
                            speak("what message to send")
                            query = takecommand()
                                            
                        elif "phone call" in query:
                            msg_type = 'call'
                        else:
                            msg_type = 'video call'
                                            
                        whatsApp(contact_no, query, msg_type, name)

            elif "open camera" in query:
                from engine.features import openCamera
                openCamera()

            else:
                from engine.features import chatBot
                chatBot(query)

        except Exception as e:
            print(f"Error in allCommands: {e}")
            speak("Sorry Something went wrong")
        finally:
            # Safely wait for ALL audio processing to complete before hiding UI.
            # Must check: tts_queue (pending text), fetcher_busy (downloading MP3),
            # play_queue (ready MP3s), and pygame busy (currently playing)
            for _ in range(600):  # Max 60 second timeout
                if stop_speaking_flag:
                    break
                    
                fetching = fetcher_busy
                queued = not tts_queue.empty() or not play_queue.empty()
                try:
                    playing = pygame.mixer.music.get_busy()
                except:
                    playing = False
                
                if not fetching and not queued and not playing:
                    break
                eel.sleep(0.1)
                    
            eel.ShowHood()

    # Start as a greenlet so Eel websocket calls work safely without dropping frames
    eel.spawn(_process_command)







