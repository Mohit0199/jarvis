import pvporcupine
from pvrecorder import PvRecorder

def test_jarvis_wake_word():
    access_key = "V1klDBIz8OaqJ0Vu4is2VWsUjE8LARXlxKGRfqVm0PluyaF+Jdhb9g=="  # Get it from https://console.picovoice.ai/

    porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=["jarvis"],
        sensitivities=[0.7]
    )

    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

    try:
        recorder.start()
        print("🎙️ Listening... Say 'Jarvis'")

        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:
                print("✅ Hotword 'Jarvis' detected!")
                break

    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()
        print("🛑 Cleaned up.")

if __name__ == "__main__":
    test_jarvis_wake_word()
