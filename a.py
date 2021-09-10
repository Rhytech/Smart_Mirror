# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
# from newsapi import NewsApiClient
from PIL import Image, ImageTk
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'in'
weather_api_token = '<TOKEN>' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None # Set this if IP location lookup does not work for you (must be a string)
longitude = None # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18
i=0
timecount=0
repull=0
sleep=0
decrypt=0

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    '01d': "assets/Sun.png",  # clear sky day
    '01n': "assets/Moon.png",  # clear sky night
    '03d': "assets/Cloud.png",  # cloudy day
    '03n': "assets/Cloud.png",  # cloudy night
    '04d': "assets/PartlySunny.png",  # scattered cloudy day
    '04n': "assets/PartlyMoon.png",  # scattered cloudy night
    '02d': "assets/PartlySunny.png",  # partly cloudy day
    '02n': "assets/PartlyMoon.png",  # scattered clouds night
    '09d': "assets/Rain.png",  # rain day
    '09n': "assets/Rain.png",  # rain night
    '13d': "assets/Snow.png",  # snow day
    '13n': "assets/Snow.png",  # snow night
    '50d': "assets/Haze.png",  # fog day
    '50n': "assets/Haze.png",  # fog night
    '11d': "assets/Storm.png",  # thunderstorm day
    '11n': "assets/Storm.png",  # thunderstorm night
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Berlin Sans FB', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Berlin Sans FB', small_text_size), fg="grey", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=('Berlin Sans FB', small_text_size), fg="grey", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
#        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Berlin Sans FB', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Berlin Sans FB', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
#        self.forecastLbl = Label(self, font=('Berlin Sans FB', small_text_size), fg="white", bg="black")
#        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Berlin Sans FB', small_text_size), fg="grey", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    '''
    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e
    '''
    def get_weather(self):
        try:

            location_req_url = "http://ip-api.com/json/"
            r = requests.get(location_req_url)
            location_obj = json.loads(r.text)

            lat = 32.2833
            lon = 75.65

            location2 = "Pathankot, IN" 
            #% (location_obj['city'], location_obj['countryCode'])

            # get weather
            weather_req_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=8d6cc87d46836b3833256cc9748a8963&units=metric'.format(location2)
         
            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}C'
            temperature2 = "%s%s" % (str(int(weather_obj['main']['temp'])), degree_sign)
            currently2 = weather_obj['weather'][0]['main']
            #forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['weather'][0]['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
#            if self.forecast != forecast2:
#                self.forecast = forecast2
#                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News' # 'News' is more internationally generic
        self.newsLbl = Label(self, text=self.title, font=('Berlin Sans FB', medium_text_size), fg="grey", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.get_headlines()
        
    def get_headlines(self):
        try:
            global i
            #i = 0
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
            if news_country_code == None:
                headlines_url = "https://news.google.com/news?ned=us&output=rss"
            else:
                headlines_url = "https://news.google.com/news?ned=%s&output=rss" % news_country_code

            feed = feedparser.parse(headlines_url)
            post=feed.entries[i]
            i+=1
            headline = NewsHeadline(self.headlinesContainer, post.title)
            headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            #print ("Error: %s. Cannot get news." % e)
            post = feed.entries[0]
            headline = NewsHeadline(self.headlinesContainer, post.title)
            headline.pack(side=TOP, anchor=W)
        self.after(6000, self.get_headlines)
                    
class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Berlin Sans FB', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)

class AssistantFrame(Frame):

    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        self.text = "Sleeping... say Hello Mira to wake up."
        self.colour = ["#ffffff", "#eeeeee", "#dddddd", "#eeeeee"]
        self.current = 0

        self.nth_state = 0
        # 0 - say something, 1 - transcript, 2 - response
        # each has 3 frames
        # 0-0.png 0-1.png 0-2.png,  1-0.png 1-1.png 1-2.png,    2-0.png 2-1.png 2-2.png
        self.nth_frame = 0

        photo = self.get_photo()
        self.iconLabel = Label(self, bg='black', image = photo)
        self.iconLabel.image = photo
        self.iconLabel.pack()

        self.textLabel = Label(self, text=self.text, font=('Berlin Sans FB', small_text_size), fg="white", bg="black")
        self.textLabel.pack()

        self.update()

    def get_photo(self):
    	try:
    		image = Image.open("assets/"+str(self.nth_state)+"-"+str(self.nth_frame)+".png")
    	except:
    		image = Image.open("assets/"+str("mira.png"))
    	image = image.resize((50, 50), Image.ANTIALIAS)
    	photo = ImageTk.PhotoImage(image)
    	return photo

    def update(self):

        self.nth_frame = (self.nth_frame+1) % 3
        photo = self.get_photo()
        self.iconLabel.image = photo
        self.iconLabel.config(image = photo)

        self.textLabel.config(fg=self.colour[self.current])
        self.current = (self.current+1) % len(self.colour)
        self.textLabel.after(200, self.update)

    def update_text(self, new_text, new_state):
        
        if globals.active == False:
            new_state = 0
            new_text = "Sleeping... say Hello Mira to wake up."

        self.nth_state = new_state

        self.text = new_text
        self.textLabel.config(text=self.text)

class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Upcoming Events'
        self.calendarLbl = Label(self, text=self.title, font=('Berlin Sans FB', medium_text_size), fg="grey", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.get_events()

    def get_events(self):
        #TODO: implement this method
        # reference https://developers.google.com/google-apps/calendar/quickstart/python
        from calender import quickstart
        ev=": ".join(quickstart.main())

        calendar_event = CalendarEvent(self.calendarEventContainer,ev)
        calendar_event.pack(side=TOP, anchor=E)
    


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        
        image = Image.open("assets/calendar.jpg")
        image = image.resize((30, 30), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)
        
        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)
        
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Berlin Sans FB', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)

class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=10, pady=60)
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=10, pady=60)
        self.calender = Calendar(self.topFrame)
        self.calender.pack(anchor=N, pady=60)      
        # news
        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=10, pady=60)
        # calender

        # Assistant
        self.centreFrame = Frame(self.tk, background='black')
        self.centreFrame.pack(fill = BOTH, expand = YES)
        
        self.assistantFrame = AssistantFrame(self.centreFrame)
        self.assistantFrame.pack(expand = YES, fill = BOTH)

        #Sleep

        image = Image.open("assets/mira.png")
        image = image.resize((100, 100), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)
        
        self.logoLabel = Label(self.tk, bg='black', image=photo)
        self.logoLabel.image = photo
        self.logoLabel.pack(side=BOTTOM, anchor=E)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break" 

    def display_sleep(self, wake):
        if wake == True:
            self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
            self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
            self.centreFrame.pack(fill = BOTH, expand = YES)
            self.logoLabel.pack_forget()
        else:
            self.topFrame.pack_forget()
            self.bottomFrame.pack_forget()
            self.centreFrame.pack_forget()
            self.logoLabel.pack(side=BOTTOM, anchor=E)

import asyncio
def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

@background
def run_assistant():
    path = "assistant-sdk-python-master/google-assistant-sdk/googlesamples/assistant/grpc"
    import sys
    sys.path.insert(1, path)
    import pushtotalk
    pushtotalk.main()

import globals
from threading import Timer

if __name__ == '__main__':
    globals.initialize()
    globals.w = FullscreenWindow()
    globals.active = False
    globals.last_active = None
    globals.w.toggle_fullscreen()     # Make initial fullscreen
    globals.w.display_sleep(False)
    run_assistant()
    globals.w.tk.mainloop()