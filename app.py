import os
from flask import Flask, render_template, request, jsonify, redirect
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import json
from moviepy.editor import *

app = Flask(__name__)

languages = {"afrikaans": "af", "albanian": "sq", "amharic": "am", "arabic": "ar", "armenian": "hy", "azerbaijani": "az",
             "basque": "eu", "belarusian": "be", "bengali": "bn", "bosnian": "bs", "bulgarian": "bg",
             "catalan": "ca", "cebuano": "ceb", "chichewa": "ny", "chinese (simplified)": "zh-cn", "chinese (traditional)": "zh-tw",
             "corsican": "co", "croatian": "hr", "czech": "cs", "danish": "da", "dutch": "nl",
             "english": "en", "esperanto": "eo", "estonian": "et", "filipino": "tl", "finnish": "fi",
             "french": "fr", "frisian": "fy", "galician": "gl", "georgian": "ka", "german": "de",
             "greek": "el", "gujarati": "gu", "haitian creole": "ht", "hausa": "ha", "hawaiian": "haw",
             "hebrew": "he", "hindi": "hi", "hmong": "hmn", "hungarian": "hu", "icelandic": "is",
             "igbo": "ig", "indonesian": "id", "irish": "ga", "italian": "it", "japanese": "ja",
             "javanese": "jw", "kannada": "kn", "kazakh": "kk", "khmer": "km", "korean": "ko",
             "kurdish (kurmanji)": "ku", "kyrgyz": "ky", "lao": "lo", "latin": "la", "latvian": "lv",
             "lithuanian": "lt", "luxembourgish": "lb", "macedonian": "mk", "malagasy": "mg", "malay": "ms",
             "malayalam": "ml", "maltese": "mt", "maori": "mi", "marathi": "mr", "mongolian": "mn",
             "myanmar (burmese)": "my", "nepali": "ne", "norwegian": "no", "odia": "or", "pashto": "ps",
             "persian": "fa", "polish": "pl", "portuguese": "pt", "punjabi": "pa", "romanian": "ro",
             "russian": "ru", "samoan": "sm", "scots gaelic": "gd", "serbian": "sr", "sesotho": "st",
             "shona": "sn", "sindhi": "sd", "sinhala": "si", "slovak": "sk", "slovenian": "sl",
             "somali": "so", "spanish": "es", "sundanese": "su", "swahili": "sw", "swedish": "sv",
             "tajik": "tg", "tamil": "ta", "telugu": "te", "thai": "th", "turkish": "tr",
             "ukrainian": "uk", "urdu": "ur", "uyghur": "ug", "uzbek": "uz", "vietnamese": "vi",
             "welsh": "cy", "xhosa": "xh", "yiddish": "yi", "yoruba": "yo", "zulu": "zu"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text_translate', methods=['GET', 'POST'])
def translate_text():
    text = request.form.get('user_text')
    target = request.form.get('target_language')
    translated_text = text_translator(text, target)
    data = {'text': translated_text}
    encoded_unicode = json.dumps(data, ensure_ascii=False)
    return encoded_unicode

@app.route('/audio_translate', methods=['GET', 'POST'])
def audio_transcript():
    target = request.form.get('target_language')
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    target = languages[target].lower()
    if file:
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(file)
        with audio_file as source:
            data = recognizer.record(source)
        transcript = recognizer.recognize_google(data, key=None)
    translated_text = text_translator(transcript, target)
    audio_translator(translated_text, target)
    data = {'text': translated_text}
    encoded_unicode = json.dumps(data, ensure_ascii=False)
    return encoded_unicode

@app.route('/video_translate', methods=['GET', 'POST'])
def translate_video():
    target = request.form.get('target_language')
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    target = languages[target].lower()
    file.save(r'static/audio_from_video/original.mp4')
    videoclip = VideoFileClip(r'static/audio_from_video/original.mp4')
    videoclip.audio.write_audiofile(r"static/audio_from_video/audio.wav", codec='pcm_s16le')
    translated_text = video_translator(r'static/audio_from_video/audio.wav', target, videoclip)
    return {'text': 'success'}

def video_translator(file, target, videoclip):
    r = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = r.record(source)
    transcript = r.recognize_google(audio, key=None)
    translated_text = text_translator(transcript, target)
    translated_audio = gTTS(text=translated_text, lang=target, slow=False)
    translated_audio.save(r'static/audio_from_video/translated_audio.wav')
    audioclip = AudioFileClip(r'static/audio_from_video/translated_audio.wav')
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(r"static/audio_from_video/translated_video.mp4")
    return translated_text

def audio_translator(text, target):
    speak = gTTS(text=text, lang=target, slow=False)
    speak.save(r"static/translated_audio/captured_voice.mp3")

def text_translator(text, target):
    translator = Translator()
    translation = translator.translate(text, dest=target)
    return translation.text

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
