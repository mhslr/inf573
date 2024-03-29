import numpy as np
import matplotlib.pyplot as plt
import cv2
import glob

import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
import webbrowser

from cv_util import timed, cap
from np_util import quant
from filters import bg_diff
from features import detect_faces, body_width

# bg = timed('background')

def save_image(k,im):
    L = glob.glob('../data/*png')
    n = 0 if len(L) == 0 else int(L[0][-5])
    print(n)
    if k == ord('s'):           # create a new picture
        n += 1
        cv2.imwrite("../Data/Test" + str(n) + ".png",im)
    if k == ord('o'):           # overwrite
        cv2.imwrite("../Data/Test" + str(n) + ".png",im)

def save_video():
    L = glob.glob('../data/*png')
    n = 0 if len(L) == 0 else int(L[0][-5])
    print(n)
    n += 1
    name = "../Data/Test" + str(n) + ".avi"
    frame_width = 640
    frame_height = 480
    out = cv2.VideoWriter(name,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))
    while cv2.waitKey(1) != ord('v'):
        _, frame = cap.read()
        out.write(frame)
        cv2.imshow('recording', frame)
    cap.release()
    out.release()

# save_video()

def remove_background(frame,bg,threshold=.1):
    # m1,m2 = bg_diff(frame, bg,threshold)
    faces = detect_faces(frame)
    # print(faces)
    C = (0,0)
    for (x,y,w,h) in faces:
        y -= int(h*.3)
        h = int(h*1.3)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        # m2[y:y+h,x:x+w] = 0
        C = (x+int(w/2),y+int(h/2))         # center of the head
    # cv2.circle(frame,C,3,(0,255,0),-1)
    # return m1,m2,frame, C


def main():
    bg = timed('background')

    vis = meshcat.Visualizer(zmq_url="tcp://127.0.0.1:6000")
    # open: http://127.0.0.1:7000/static/

    vis["robot"].delete()

    vis["robot"].set_object(g.Box([0.15, 0.35, 0.4]))
    vis["robot"]["head"].set_object(g.Box([0.2, 0.2, 0.2]))
    vis["robot"]["arm_l"].set_object(g.Box([0.1, 0.1, 0.3]))
    vis["robot"]["arm_r"].set_object(g.Box([0.1, 0.1, 0.3]))
    vis["robot"]["head"].set_transform(tf.translation_matrix([0, 0, 0.32]))
    vis["robot"]["arm_l"].set_transform(tf.translation_matrix([0, .25, 0]))
    vis["robot"]["arm_r"].set_transform(tf.translation_matrix([0, -.25, 0]))
    while True:
        ret, frame = cap.read()

        m1,m2,frame,C = remove_background(frame,bg)

        if (C[0] != 0):
            C = np.array(C)
            C = C - np.array([303.87548638, 182.57587549])
            C = C / 200
            print("is moving")
            vis["robot"].set_transform(tf.translation_matrix([0,C[0],-C[1]]))

        body_width(m2)
        cv2.imshow('cam', frame)
        # cv2.imshow('mask', m2)

        k = cv2.waitKey(1)
        if k == ord('h'):
            # print(quant(m1))
            plt.figure(1)
            plt.hist(m1.ravel(), bins=50)
            plt.figure(2)
            plt.plot(m2.sum(axis=0))
            plt.figure(3)
            plt.plot(m2.sum(axis=1))
            plt.show()
        if k == ord('b'):
            bg = timed('background')
        if k == ord('q'):
            break
        if k == ord('s') or k == ord('o'):
            save_image(k,frame)

# main()
# run: meshcat-server
# run in another terminal: python -c 'import main; main.main()'
