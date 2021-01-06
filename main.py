	# main.py

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import DataBase

from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2



class CreateAccountWindow(Screen):
    namee = kivy.properties.ObjectProperty(None)
    email = kivy.properties.ObjectProperty(None)
    password = kivy.properties.ObjectProperty(None)
    qrcode=kivy.properties.ObjectProperty(None)

    def submit(self):
        if self.namee.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password != "":
                db.add_user(self.email.text, self.password.text, self.namee.text)

                self.reset()

                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""
        self.qrcode.text=""

    def addQRCode(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
	        help="path to output CSV file containing barcodes")
        args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(2.0)


        while self.qrcode.text=="":
	# grab the frame from the threaded video stream and resize it to
	# have a maximum width of 400 pixels
	        frame = vs.read()
        	frame = imutils.resize(frame, width=400)

	# find the barcodes in the frame and decode each of the barcodes
        	barcodes = pyzbar.decode(frame)

        	# loop over the detected barcodes
	        for barcode in barcodes:
		# extract the bounding box location of the barcode and draw
		# the bounding box surrounding the barcode on the image
		        (x, y, w, h) = barcode.rect
		        cv2.cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

		# the barcode data is a bytes object so if we want to draw it
		# on our output image we need to convert it to a string first
		        barcodeData = barcode.data.decode("utf-8")
	        	barcodeType = barcode.type

		# draw the barcode data and barcode type on the image
	        	text = "{} ({})".format(barcodeData, barcodeType)
	        	cv2.cv2.putText(frame, text, (x, y - 10),
		        	cv2.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                

		# if the barcode text is currently not in our CSV file, write
		# the timestamp + barcode to disk and update the set
	        	print("NICE:"+barcodeData)
	        	self.qrcode.text=barcodeData
	        	
	        	
	# show the output frame
	        cv2.cv2.imshow("Barcode Scanner", frame)
	        key = cv2.cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	        if key == ord("q"):
	        	break
            

# close the output CSV file do a bit of cleanup

        print("[INFO] cleaning up...")
        
        vs.stop()

        

class LoginWindow(Screen):
    email = kivy.properties.ObjectProperty(None)
    password = kivy.properties.ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.email.text, self.password.text):
            MainWindow.current = self.email.text
            self.reset()
            sm.current = "main"
        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""

    



class MainWindow(Screen):
    n = kivy.properties.ObjectProperty(None)
    created = kivy.properties.ObjectProperty(None)
    email = kivy.properties.ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        password, name, created = db.get_user(self.current)
        self.n.text = "Account Name: " + name
        self.email.text = "Email: " + self.current
        self.created.text = "Created On: " + created


class WindowManager(ScreenManager):
    pass


def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()


kv = Builder.load_file("my.kv")

sm = WindowManager()
db = DataBase("users.txt")

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"),MainWindow(name="main")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
