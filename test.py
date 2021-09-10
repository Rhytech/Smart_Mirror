from threading import Timer

def sl(a):
    print("hello")

Timer(1, sl, 'a').start()