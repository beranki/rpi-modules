from time import time
import cv2
import numpy as np
from imutils.video import VideoStream
import socket
import asyncio
import sys
import pickle
import struct
import datetime
import base64
import time
import keyboard
import select

class Camera:


    def __init__(self, num_streams=0):

        self.streams = []
        self.current = None
        self.ctr = 0


        #capture = cv2.VideoCapture(0)
        #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 315)

        if (num_streams > 0): self.current = 0

        for stream in range(abs(num_streams)):
            print(stream)
            self.streams.append(VideoStream(src=stream).start())
            #print(stream)
            #img = cv2.imread(f"video-streaming-opt/stream_test/cam_{self.current+1}a.png")
            #img = self.streams[stream].read()
            #resize_frame = cv2.resize(img, dsize=(480, 315), interpolation=cv2.INTER_AREA)
            #self.streams.append(resize_frame)

    def camera_stream(self, idx_stream):
        self.current = (idx_stream-1) % len(self.streams) 
        #img = cv2.imread(f"video-streaming-opt/stream_test/cam_{self.current+1}{chr(97+self.ctr)}.png")
        #print(f"video-streaming-opt/stream_test/cam_{self.current+1}{chr(97+self.ctr)}.png")
        img = self.streams[self.current].read()
        #print(self.streams)
        #print(img)
        if (img is not None):
            resize_frame = cv2.resize(img, dsize=(480, 315), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)
            self.ctr = (self.ctr + 1) % 2
            return gray


class Client:
    def __init__(self, ip: str, port: int, cam: Camera):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.cam = cam
        self.conn_sock()

    def conn_sock(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            if (len(self.cam.streams) > 0): 
                self.sendImages()

        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(u'Connect fail %d times. exit program'%(self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server'%(self.connectCount))
            self.conn_sock()

    def sock_text(self, readySock):
        ACK_TEXT = 'text_received'

        encodedMessage = readySock.recv(1024)

        if not encodedMessage:
            print('error: encodedMessage was received as None')
            return None

        message = encodedMessage.decode('utf-8')
        encodedAckText = bytes(ACK_TEXT, 'utf-8')
        readySock.sendall(encodedAckText)

        return message

    def sendImages(self):
        cnt = 0
        current = 1
        
        try:
            
            while (True):
                if (self.cam.camera_stream(current) is not None):
                    frame = self.cam.camera_stream(current)

                    now = time.localtime()
                    stime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                    data = np.array(imgencode)
                    stringData = base64.b64encode(data)
                    length = str(len(stringData))
                    self.sock.sendall(length.encode('utf-8').ljust(64))
                    self.sock.send(stringData)
                    self.sock.send(stime.encode('utf-8').ljust(64))
                    print(u'send images %d'%(cnt))
                    cnt+=1

                    socks = [self.sock]
                    readySocks, _, _ = select.select(socks, [], [], 5)
                    for readySock in readySocks:
                        message = str(self.sock_text(readySock))
                        print('received: ' + message)
                        
                        current = eval(message)
                    time.sleep(0.095)

                else:
                    print("no established cam stream")
            
        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.conn_sock()
            self.sendImages()

def main():
    client = Client('localhost', 8080, Camera(2))

if __name__ == "__main__":
    main()