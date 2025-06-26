import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import pyperclip as pc
import os

r = sr.Recognizer()

def reply(text):
    print("App:", text)  

def record_audio():
    """Capture voice input from the user."""
    with sr.Microphone() as source:
        r.pause_threshold = 1.0
        r.energy_threshold = 500
        reply("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            return r.recognize_google(audio).lower()
        except sr.UnknownValueError:
            reply("Sorry, I didn't catch that. Could you repeat?")
            return ""
        except sr.RequestError:
            reply("Network error. Please check your internet connection.")
            return ""
        except Exception as e:
            reply(f"An error occurred: {e}")
            return ""

class LanguageTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title('Language Translator')
        self.root.geometry('1060x660')
        self.root.resizable(False, False)

        self.language_codes = {
            'English': 'en',
            'Tamil': 'ta',
            'Kannada': 'kn',
            'Telugu': 'te',
            'hindi': 'hi',
            'Malayalam': 'ml',
        }

        self.setup_ui()

    def setup_ui(self):
        try:
            bg_img = Image.open('translator.jpeg')
            self.bg_image = ImageTk.PhotoImage(bg_img)
            bg_label = tk.Label(self.root, image=self.bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

        languages = sorted(self.language_codes.keys())

        self.from_lang_var = tk.StringVar()
        self.from_lang_combo = ttk.Combobox(
            self.root, width=20, textvariable=self.from_lang_var,
            state='readonly', font=('Corbel', 14), values=['Auto Detect'] + languages
        )
        self.from_lang_combo.place(x=50, y=140)
        self.from_lang_combo.current(0)

        self.to_lang_var = tk.StringVar()
        self.to_lang_combo = ttk.Combobox(
            self.root, width=20, textvariable=self.to_lang_var,
            state='readonly', font=('Corbel', 14), values=languages
        )
        self.to_lang_combo.place(x=600, y=140)
        self.to_lang_combo.current(languages.index('Tamil'))

        self.input_text = tk.Text(self.root, width=45, height=13, font=('Calibri', 14), wrap=tk.WORD)
        self.input_text.place(x=20, y=200)

        self.output_text = tk.Text(self.root, width=45, height=13, font=('Calibri', 14), wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.place(x=550, y=200)

        self.create_buttons()

    def create_buttons(self):
        tk.Button(self.root, text="Translate", font=('Corbel', 14, 'bold'), command=self.translate,
                  bg="#4CAF50", fg="white", padx=10).place(x=40, y=565)

        tk.Button(self.root, text="Clear", font=('Corbel', 14, 'bold'), command=self.clear_text,
                  bg="#f44336", fg="white", padx=10).place(x=270, y=565)

        tk.Button(self.root, text="Copy", font=('Corbel', 14, 'bold'), command=self.copy_text,
                  bg="#2196F3", fg="white", padx=10).place(x=485, y=565)

        tk.Button(self.root, text="Speak", font=('Corbel', 14, 'bold'), command=self.text_to_speech,
                  bg="#FF9800", fg="white", padx=10).place(x=650, y=565)

        tk.Button(self.root, text="Voice Input", font=('Corbel', 14, 'bold'), command=self.voice_input,
                  bg="#9C27B0", fg="white", padx=10).place(x=850, y=565)

    def translate(self):
        text = self.input_text.get("1.0", tk.END).strip()
        target_lang = self.to_lang_var.get()
        if not text or not target_lang:
            messagebox.showwarning("Warning", "Enter text and select target language.")
            return

        try:
            translated = GoogleTranslator(
                source='auto',
                target=self.language_codes[target_lang]
            ).translate(text)

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Translation Error", str(e))

    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

    def copy_text(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            pc.copy(text)
            messagebox.showinfo("Copied", "Text copied to clipboard.")

    def text_to_speech(self):
        text = self.output_text.get("1.0", tk.END).strip()
        target_lang = self.to_lang_var.get()
        if not text or not target_lang:
            messagebox.showwarning("Warning", "No text or language selected.")
            return

        try:
            tts = gTTS(text=text, lang=self.language_codes[target_lang])
            tts.save("translated_audio.mp3")
            playsound("translated_audio.mp3")
            os.remove("translated_audio.mp3")
        except Exception as e:
            messagebox.showerror("Speech Error", str(e))

    def voice_input(self):
        spoken_text = record_audio()
        if spoken_text:
            print("User said:", spoken_text)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, spoken_text)

            # Detect language and set dropdown
            try:
                detected_lang_code = GoogleTranslator(source='auto', target='en').detect(spoken_text)
                matched_lang = next((lang for lang, code in self.language_codes.items() if code == detected_lang_code), None)
                self.from_lang_combo.set(matched_lang if matched_lang else "Auto Detect")
            except:
                self.from_lang_combo.set("Auto Detect")

            self.translate()
            self.text_to_speech()

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslator(root)
    root.mainloop()
