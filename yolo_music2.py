import cv2
import numpy as np
import argparse
import threading
import pygame
from send_mail import send_email
from pygame import mixer

# Initialize pygame mixer
pygame.mixer.init()

parser = argparse.ArgumentParser()
parser.add_argument('--play_video', help="True/False", default=False)
parser.add_argument('--video_path', help="Path of video file", default="videos/fire1.mp4")
args = parser.parse_args()

# Global variable to define anomaly threshold
anomaly_threshold = 5000  # Adjust according to your requirements
anomaly_detected = False
anomaly_sound_played = False

sender_email = "sowrabha02@gmail.com"
app_password = "pdfi nqtg wuqz lkga"
recipient_email = "sowrabhaa.bharadwaj@gmail.com"
subject = "ANOMALY IS DETECTED IN VIDEO"
body = "ANOMALY IS BEING FOUND BE AWARE!!!!!!!!!!!!!!!"

# Load the song you want to play
mixer.music.load('song1.mp3')

def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    classes = []
    with open("obj.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layers_names = net.getLayerNames()
    output_layers = [layers_names[i - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    return net, classes, colors, output_layers

def detect_objects(img, net, output_layers):
    blob = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    return blob, outputs

def get_box_dimensions(outputs, height, width):
    boxes = []
    confs = []
    class_ids = []
    for output in outputs:
        for detect in output:
            scores = detect[5:]
            class_id = np.argmax(scores)
            conf = scores[class_id]
            if conf > 0.3:
                center_x = int(detect[0] * width)
                center_y = int(detect[1] * height)
                w = int(detect[2] * width)
                h = int(detect[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confs.append(float(conf))
                class_ids.append(class_id)
    return boxes, confs, class_ids

def draw_labels(boxes, confs, colors, class_ids, classes, img):
    global anomaly_detected, anomaly_sound_played

    indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN

    # Use a dictionary to store colors assigned to classes
    class_colors = {}
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])

            # Assign color dynamically based on class label
            if label not in class_colors:
                class_colors[label] = colors[len(class_colors) % len(colors)]
            color = class_colors[label]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 1, color, 1)

            # Anomaly detection logic
            if label in ["Gun", "Fire", "Rifle"]:
                if w * h > anomaly_threshold and not anomaly_detected:
                    # Print anomaly detection message
                    print("Anomaly detected: {} with bounding box size {}x{}".format(label, w, h))
                    cv2.imwrite("anomaly_detected.jpg", img)
                    send_email(sender_email, app_password, recipient_email, subject, body, "anomaly_detected.jpg")
                    anomaly_detected = True

                    # Play the sound only once when anomaly is detected
                    if not anomaly_sound_played:
                        threading.Thread(target=play_sound).start()
                        anomaly_sound_played = True

                    cv2.putText(img, "Anomaly Detected", (x, y - 20), font, 1, (0, 0, 255), 2)

    img = cv2.resize(img, (800, 600))
    cv2.imshow("Image", img)

def play_sound():
    mixer.music.play()

def start_video(video_path):
    model, classes, colors, output_layers = load_yolo()
    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, channels = frame.shape
        blob, outputs = detect_objects(frame, model, output_layers)
        boxes, confs, class_ids = get_box_dimensions(outputs, height, width)
        draw_labels(boxes, confs, colors, class_ids, classes, frame)

        key = cv2.waitKey(1)
        if key == 27 or cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_play = args.play_video
    if video_play:
        video_path = args.video_path
        print('Opening ' + video_path + " .... ")
        start_video(video_path)
