import cv2 
import pickle

width,height=107,48

try:
    with open('parkingSlotPosition','rb') as f:
        posList=pickle.load(f)
except:
    posList=[]



def mouseClick(events, x, y, flags, params):
# Adding ROI values to posList
    if events == cv2.EVENT_LBUTTONDOWN: 
        posList.append((x, y))
# Removing unwanted ROI from poslist
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate (posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1< y < y1 + height:
                posList.pop(i)
# Saving the posList values to parkingSlotPosition file 
    with open('parkingSlotPosition', 'wb') as f: pickle.dump(posList, f)



while True:
    img = cv2.imread('carParkImg.png')
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 255, 255), 2)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


