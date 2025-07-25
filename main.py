import cv2
import time
import HandTrackingModule as htm
import MyDict as md
from math import atan, pi
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc


def findAngle(Cm, Vm):                                                  # This function finds angles
    angle = abs((Vm - Cm)/(1 + Cm * Vm))                                # between    the fingers used to 
    ret = atan(angle)                                                   # control the volume and
    val = (ret * 180)/pi                                                # brightness
    return int(val)

# Angle Range 0 - 180
# Volume Range -65 - 0

def setVolume(angle):                                                   # This function controls
    vol = float(md.ReturnVol(angle))  
    volume.SetMasterVolumeLevel(vol, None)


def setBrightness(angle):                                               # This function controls
    brightness = float(md.ReturnBtns(angle))                   # Brightness of the system)   
    sbc.set_brightness(brightness, display=0)


###########################################
wCam , hCam = 640, 480                                                 # set resolution from here
###########################################


cap = cv2.VideoCapture(0)                                               # Initialize camera capture
cap.set(3,wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(maxHands=1, detectionCon=0.7)               # Object for class in HandTrackingModule


devices = AudioUtilities.GetSpeakers()                                  # Initialization for accessing 
interface = devices.Activate(                                           # system volume
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


angle = float()
Vctrl = [0,1,0,0,0]
Bctrl = [0,1,1,0,0]
getCtrl = [0,0,0,0,0]
initiator = 0
while True:                                                             # Main initialized with loop 
    success, img = cap.read()                                           # Reads image i.e. ongoing video
    img = detector.findHands(img, draw=False)                           # Find hand in image
    lmlist = detector.findPosition(img, draw=False)                     # Save position of Hand Landmark
    if len(lmlist) != 0:


        x1, y1 = lmlist[4][1], lmlist[4][2]                             # Coordinates of Thumb
        x2, y2 = lmlist[8][1], lmlist[8][2]                             # Coordinates of Index finger
        x3, y3 = lmlist[12][1], lmlist[12][2]                           # Coordinates of Middle finger
        cx, cy = (x1+x3)//2, (y1+y3)//2                                 # Coordinates of Intersection

        # This code fragment checks the rotation of fingers and accordingly gives angle      
                                                                    
        Cm = 0                                                          
        if (x2 > cx) & (y1 < cy):                                      # Anti-clockwise rotation
            if (y2 >= cy) & (y3 > cy):                                  # Minimum angle boundry
                angle = 0
            elif ((x2 - cx) != 0):                                      # Angle between 0 - 90
                Vm = (y2 - cy)/(x2 - cx)
                angle = findAngle(Cm, Vm)

        elif (x2 < cx) & (y1 > cy):                                    # Clockwise rotation
            if (y3 < cy) & (y2 >= cy):                                  # Maximum angle boundry
                angle = 180
            elif ((x2 - cx) != 0):                                      # Angle between 90 - 180
                Vm = (y2 - cy)/(x2 - cx)
                angle = findAngle(Cm, Vm)
                angle = 180 - angle
        else: 
            if (y1 == cy == y3) & (y2 < cy):               # To eradicate undefined slope
                angle = 90
        
        if initiator == 0:
            getCtrl = detector.fingersUp(lmlist)

        else:
            cv2.circle(img, (x1, y1), 5, (0, 0, 0), cv2.FILLED)             # Highlighting tip of Thumb
            cv2.circle(img, (x2, y2), 5, (0, 0, 0), cv2.FILLED)             # Highlighting tip of Index finger
            cv2.circle(img, (x3, y3), 5, (0, 0, 0), cv2.FILLED)             # Highlighting tip of Middle finger
            cv2.circle(img, (cx, cy), 5, (0, 0, 0), cv2.FILLED)             # Highlighting Intersection
            cv2.line(img, (x1,y1), (x3, y3), (0, 140, 255), 1)              # Line joining Thumb & Middle finger
            cv2.line(img, (x2,y2), (cx, cy), (0, 140, 255), 1)              # Line joining Index finger & Intersection
            

        if getCtrl == Vctrl:
            cv2.rectangle(img, (20, 50), (wCam - 20, hCam - 20), (0, 0, 0), 3)
            cv2.putText(img, f'Volume', (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (128, 0, 0), 1)
            setVolume(angle)
            initiator = 1
            if detector.fingersUp(lmlist) == [1,1,1,1,1]:
                initiator = 0

        if getCtrl == Bctrl:
            cv2.rectangle(img, (20, 50), (wCam - 20, hCam - 20), (0, 0, 0), 3)
            cv2.putText(img, f'Brightness', (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (128, 0, 0), 1)
            setBrightness(angle)
            initiator = 1
            if detector.fingersUp(lmlist) == [1,1,1,1,1]:
                initiator = 0


    cTime = time.time()
    fps = 1/(cTime-pTime)                                               # FPS calculator and Display 
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (20, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (128, 0, 0), 1)

    cv2.imshow("image", img)                                            # Output
    cv2.waitKey(1)
    if getCtrl == [0,1,1,1,0]:
        exit(1)
