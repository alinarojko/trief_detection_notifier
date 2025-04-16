import cv2
import time
from emailing import send_email
from datetime import datetime
import glob
import os
from threading import Thread

# Command to run camera of the laptop
video = cv2.VideoCapture(0)

# Define frame for the first video frame
first_frame = None
status_list = []
count = 1

def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)

# Start loop to cellect video from camera while "Q! letter is not pressed
while True:
    status = 0
#   time.sleep(1)
    check, frame = video.read()

    # creating grey video
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # creating blur vidoe
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)
#    cv2.imshow("My video", gray_frame_gau)  this line display the created video

    # Checking if first frami is already exist , if not - assig blur and crey video to the first
    if first_frame is None:
         first_frame = gray_frame_gau


    # comparing the current video and the grey-blur
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
#    cv2.imshow("My video", delta_frame)
    key = cv2.waitKey(1)


    #  Update our video to be black-white to have only the object in white and environment - black
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
#    cv2.imshow("My video", thresh_frame)


    # To find a contours of the object on the black background, using the last frame
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # To add contoutrs  to the object , bigger that 5000 pixels,  not to show the fake objects
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(target=send_email, args=(image_with_object, ))
        email_thread.daemon = True

        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()
        clean_thread.start()

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

video.release()

