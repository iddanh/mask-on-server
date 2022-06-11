import base64
import sys
import cv2
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
from imutils import paths
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from tensorflow.keras.utils import img_to_array

from keras.applications.mobilenet_v2 import preprocess_input
import tensorflow as tf
from keras.models import load_model


class VideoTransformer():

    def detect_and_predict_mask(self, frame1, net, model):
        # grab the dimensions of the frame and then construct a blob
        (h, w) = frame1.shape[:2]
        blob = cv2.dnn.blobFromImage(frame1, 1.0, (300, 300), (104.0, 177.0, 123.0))

        net.setInput(blob)
        detections = net.forward()

        # initialize our list of faces, their corresponding locations and list of predictions
        faces = []
        locations = []
        predictions = []

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.6:
                # we need the X,Y coordinates
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype('int')

                # ensure the bounding boxes fall within the dimensions of the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                # extract the face ROI, convert it from BGR to RGB channel, resize it to 224,224 and preprocess it
                face = frame1[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (128, 128))
                face = img_to_array(face)
                face = preprocess_input(face)

                faces.append(face)
                locations.append((startX, startY, endX, endY))

        # only make a predictions if atleast one face was detected
        if len(faces) >= 1:
            faces = np.array(faces, dtype='float32')
            predictions = model(faces)

        return (locations, predictions)

    def transform(self, frame):
        # img = frame.to_ndarray(format="bgr24")
        prototxtPath = 'config/deploy.prototxt.txt'
        weightsPath = 'config/res10_300x300_weights.caffemodel'
        net = cv2.dnn.readNet(weightsPath, prototxtPath)
        model = load_model(r'config/model/model-c.h5')
        (locs, preds) = self.detect_and_predict_mask(frame, net, model)
        for (box, pred) in zip(locs, preds):
            (startX, startY, endX, endY) = box
            (mask, withoutMask, no_face, half) = pred
            max_pred = max(pred)

            # if no_face == max_pred:
            #     continue

            if mask == max_pred:
                label = "MASK-ON"
                color = (117, 182, 70)
            elif withoutMask == max_pred or no_face == max_pred:
                label = "MASK-OFF"
                color = (97, 95, 232)
            else:
                label = "MASK-HALF"
                color = (110, 191, 249)

            # label = 'Mask' if mask > withoutMask else 'No Mask'
            # color = (0, 255, 0) if label == 'Mask' else (0, 0, 210)
            # # include the probability in the label
            # label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
            frame = cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            frame = cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
        return frame


def main():
    my_video_transformer = VideoTransformer()
    while (True):
        try:
            # print("p:")
            # fileName = input()
            # frame = cv2.imread(fileName)

            data = input()

            img = base64.b64decode(data)
            npimg = np.fromstring(img, dtype=np.uint8)
            frame = cv2.imdecode(npimg, 1)

            tagged_frame = my_video_transformer.transform(frame)

            _, im_arr = cv2.imencode('.jpg', tagged_frame)
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            print(im_b64)

            # cv2.imwrite('tagged.jpg', tagged_frame)
        except:
            print(sys.exc_info()[0])


# Start process
if __name__ == '__main__':
    main()
