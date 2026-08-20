# main.py
# SAM ka main loop. Yeh file run karo: python main.py

from config import WAKE_WORD, USER_NAME, ASSISTANT_NAME
from listener import listen, listen_for_wake_word
from speaker import speak
from brain import handle_command


def main():
    print(f"=== {ASSISTANT_NAME} chal raha hai ===")
    try:
        speak(f"Assalam o Alaikum {USER_NAME}, main {ASSISTANT_NAME} hoon. '{WAKE_WORD}' bol kar mujhe bulao.")
    except Exception as exc:
        print(f"Startup speech error: {exc}")

    while True:
        try:
            print(f"\n(Sun raha hoon... '{WAKE_WORD}' bolo)")
            heard_wake = listen_for_wake_word(WAKE_WORD)

            if heard_wake:
                speak("Ji, boliye.")
                command = listen()

                if command is None:
                    speak("Kuch sunayi nahi diya, dobara koshish karo.")
                    continue

                response, should_exit = handle_command(command)
                speak(response)

                if should_exit:
                    break

        except KeyboardInterrupt:
            speak("SAM band ho raha hai. Allah Hafiz!")
            break
        except Exception as exc:
            print(f"Error: {exc}")
            try:
                speak("Kuch masla ho gaya, dobara koshish karta hoon.")
            except Exception:
                pass
            continue


if __name__ == "__main__":
    main()