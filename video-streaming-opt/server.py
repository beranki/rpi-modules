from time import time
import cv2
import numpy as np
from imutils.video import VideoStream
import socket
import asyncio
import sys
import pickle
import struct
import base64
import datetime
import threading
import time
import keyboard
import msvcrt

class Server:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.open_sock()
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()

    def close_sock(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def open_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

    def send_text(self, message, sock):
        ACK_TEXT = 'text_received'
        
        encodedMessage = bytes(message, 'utf-8')

        sock.sendall(encodedMessage)

        encodedAckText = sock.recv(1024)
        ackText = encodedAckText.decode('utf-8')

        if ackText == ACK_TEXT:
            print('server acknowledged reception of text')
        else:
            print('error: server has sent back ' + ackText)

    def receiveImages(self):
        rec_kp = "1"
        
        try:
            while True:
                length = self.recvall(self.conn, 64)
                length1 = length.decode('utf-8')
                stringData = self.recvall(self.conn, int(length1))
                stime = self.recvall(self.conn, 64)
                print('send time: ' + stime.decode('utf-8'))
                now = time.localtime()
                print('receive time: ' + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                data = np.frombuffer(base64.b64decode(stringData), np.uint8)
                decimg = cv2.imdecode(data, 1)
                
                if (msvcrt.kbhit()): 
                    rec_kp = (msvcrt.getch()).decode('utf-8') if rec_kp.isnumeric() else rec_kp
                
                self.send_text(rec_kp, self.conn)

                cv2.imshow("image", decimg)

                if cv2.waitKey(1) & 0xFF == ord('s'): 
                    break
                    
                time.sleep(0.1)
                
        except Exception as e:
            print(e)
            self.close_sock()
            self.open_sock()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()
        
        cv2.destroyAllWindows()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def main():
    server = Server('localhost', 8080)

if __name__ == "__main__":
    main()