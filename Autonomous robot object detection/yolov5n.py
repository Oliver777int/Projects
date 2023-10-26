import numpy as np
import cv2
import os

# Set True to show bounding box on screen.
SHOW_BBOX = False

# Constants.
INPUT_WIDTH = 96
INPUT_HEIGHT = 96
SCORE_THRESHOLD = 0.45
NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.3
 
# Text parameters.
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 1
 
# Colors.
BLACK  = (0,0,0)
BLUE   = (255,178,50)
YELLOW = (0,255,255)
WHITE = (255,255,255)
height = 480
width = 640

# Yolov5n network
modelWeights = "saved_models/yolo96.onnx"
net = cv2.dnn.readNetFromONNX(modelWeights)
maxGroundSteering = 38 * np.pi/180

def draw_label(im, label, x, y):
    text_size = cv2.getTextSize(label, FONT_FACE, FONT_SCALE, THICKNESS)
    dim, baseline = text_size[0], text_size[1]
    cv2.rectangle(im, (x,y), (x + dim[0], y + dim[1] + baseline), (0,0,0), cv2.FILLED)

    # Display text inside the rectangle.
    cv2.putText(im, label, (x, y + dim[1]), FONT_FACE, FONT_SCALE, YELLOW, THICKNESS, cv2.LINE_AA)

def pre_process(input_image, net):
      # Create a 4D blob from a frame.
      blob = cv2.dnn.blobFromImage(input_image, 1/255,  (INPUT_WIDTH, INPUT_HEIGHT), [0,0,0], 1, crop=False)
 
      # Sets the input to the network.
      net.setInput(blob)
 
      # Run the forward pass to get output of the output layers.
      outputs = net.forward(net.getUnconnectedOutLayersNames())
      return outputs

def post_process(input_image, outputs, base_speed, max_steering):
      class_ids = []
      confidences = []
      boxes = []
      # Rows.
      rows = outputs[0].shape[1]
      image_height, image_width = input_image.shape[:2]
      # Resizing factor.
      x_factor = image_width / INPUT_WIDTH
      y_factor =  image_height / INPUT_HEIGHT
      # Iterate through detections.
      for r in range(rows):
            row = outputs[0][0][r]
            confidence = row[4]
            # Discard bad detections and continue.
            if confidence >= CONFIDENCE_THRESHOLD:
                  classes_scores = row[5:]
                  # Get the index of max class score.
                  class_id = np.argmax(classes_scores)
                  #  Continue if the class score is above threshold.
                  if (classes_scores[class_id] > SCORE_THRESHOLD):
                        confidences.append(confidence)
                        class_ids.append(class_id)
                        cx, cy, w, h = row[0], row[1], row[2], row[3]
                        left = int((cx - w/2) * x_factor)
                        top = int((cy - h/2) * y_factor)
                        width = int(w * x_factor)
                        height = int(h * y_factor)
                        box = np.array([left, top, width, height])
                        boxes.append(box)

# Perform non maximum suppression to eliminate redundant, overlapping boxes with lower confidences.
      indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
      groundSteering, pedalPosition, zero_detections = 0, 0, True
      for i in indices:
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]

            # Move towards highest confidence prediction.
            if confidences[i] == max(confidences) and (top+height/2) > 180 and (top+height/2) < 360:
                visualize(input_image, left, top, width, height, confidences[i])
                zero_detections = False
                groundSteering, pedalPosition = move(left+width/2, top+height/2, height, base_speed, max_steering)
                cv2.rectangle(input_image, (int(left+width/2), int(top+height/2)), (int(left+width/2), int(top+height/2)), WHITE, 6*THICKNESS)
      return groundSteering, pedalPosition, zero_detections

def visualize(input_image, left, top, width, height, confidence):
    # Draw bounding box.
    cv2.rectangle(input_image, (left, top), (left + width, top + height), BLUE, 3*THICKNESS)

    # Class label.
    label = "{}:{:.2f}".format('Kiwicar', confidence)                          
    draw_label(input_image, label, left, top)

    # Show inference time
    t, _ = net.getPerfProfile()
    label2 = "Bounding box size: " + str(int(height))
    label = 'Inference time: %.2f ms' % (t * 1000.0 /  cv2.getTickFrequency())
    cv2.putText(input_image, label, (20, 40), FONT_FACE, FONT_SCALE,  (0, 0, 255), THICKNESS, cv2.LINE_AA)

def move(cx, cy, kiwi_h, base_speed, max_steering):
    x0 = int(width/2)
    y0 = int(height)
    pedalPosition = 0
    groundSteering = 0
    xRange = (cx - x0)/x0
    groundSteering = - xRange * max_steering

    if kiwi_h < 100:
        pedalPosition = base_speed
    
    return groundSteering, pedalPosition
    
