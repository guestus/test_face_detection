import telepot
from telepot.loop import MessageLoop
import cv2
import os

class BaseNotificator:
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def sendMessage(self, text):
        self._sendMsg_(text)
    def sendImage(self, img):
        self._sendImg_(img)
    def _sendMsg_(self, text):
        pass
    def _sendImg_(self, img):
        pass
        
class TelegrammNotificator(BaseNotificator):
    def __init__(self, **kwargs):
        super(TelegrammNotificator, self).__init__(**kwargs)
        self.bot = telepot.Bot(self.auth)
    def _sendMsg_(self, text):
        self.bot.sendMessage(self.chatid, text)
    def _sendImg_(self, img):
        cv2.imwrite(f"file-temp.jpg",img)
        try:
            self.bot.sendPhoto(self.chatid,open(f"file-temp.jpg",'rb'))
        finally:
            os.remove(f"file-temp.jpg")

