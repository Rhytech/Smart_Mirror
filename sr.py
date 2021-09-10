import pyttsx3 
import speech_recognition as sr 
from time import time, sleep
import globals
from auth import verify_user

def takeCommand(): 

	r = sr.Recognizer() 
	with sr.Microphone() as source: 
		print('Listening') 
		r.pause_threshold = 0.7
		audio = r.listen(source) 
		try: 
			print("Recognizing") 
			Query = r.recognize_google(audio, language='en-in') 
			print("the command is printed=", Query) 
		except Exception as e: 
			print(e) 
			print("Say that again sir") 
			return "None"
		return Query 

def speak(audio): 
      
    engine = pyttsx3.init() 
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id) 
    globals.w.assistantFrame.update_text("Responding...", 2)
    engine.say(audio)         
    engine.runAndWait() 

def wake_up():
    if(globals.active == True):
        print("Already active.")
        return
    globals.active = True
    globals.w.display_sleep(True)
    speak("Hello. I'm Meera, the smart mirror.")
    globals.w.assistantFrame.update_text("Say something...", 0)

def mira_sleep():
    if(globals.active == False):
        print("Already sleeping.")
        return
    speak("Going to sleep.")
    globals.w.assistantFrame.update_text("Sleeping... say Hello Mira to wake up.", 0)
    globals.active = False
    globals.w.display_sleep(False)

def mira_call(query):
    return ("mira" in query or "meera" in query or "mirror" in query or "mera" in query)

def mark_conv():
    globals.last_active = time()

from threading import Timer

def allow_next():
    while(globals.active == False):
        query = takeCommand().lower()
        if (("hi" in query or "hai" in query or "hello" in query or "wake" in query or "up" in query) and mira_call(query)):
            if verify_user() == True:
                wake_up()
                mark_conv()
                Timer(1, check_sleep).start()
            else:
                speak("Unauthorized User!")
    return

def check_sleep():
    if globals.active == False:
        return
    if globals.last_active and (time() - globals.last_active)>30:
        mira_sleep()
    else:
        Timer(1, check_sleep).start()