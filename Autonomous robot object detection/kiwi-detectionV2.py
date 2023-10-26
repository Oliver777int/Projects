# sysv_ipc is needed to access the shared memory where the camera image is present.
import sysv_ipc
# numpy and cv2 are needed to access, modify, or display the pixels
import numpy
import cv2
# OD4Session is needed to send and receive messages
import OD4Session
import opendlv_standard_message_set_v0_9_10_pb2
from kiwicar import Kiwicar
from yolov5n import *
MAX_STILL_STANDING_FRAMES = 5
MAX_REVERSE_TIME = 2.5

# This dictionary contains all distance values to be filled by function onDistance(...).
distances = { "front": 0.0, "left": 0.0, "right": 0.0, "rear": 0.0 }


# This callback is triggered whenever there is a new distance reading coming in.
def onDistance(msg, senderStamp, timeStamps):
    if senderStamp == 0:
        distances["front"] = msg.distance
    if senderStamp == 1:
        distances["left"] = msg.distance
    if senderStamp == 2:
        distances["rear"] = msg.distance
    if senderStamp == 3:
        distances["right"] = msg.distance


# Create a session to send and receive messages from a running OD4Session;
# Replay mode: CID = 253
# Live mode: CID = 112
# TODO: Change to CID 112 when this program is used on Kiwi.
session = OD4Session.OD4Session(cid=140)
# Register a handler for a message; the following example is listening
# for messageID 1039 which represents opendlv.proxy.DistanceReading.
# Cf. here: https://github.com/chalmers-revere/opendlv.standard-message-set/blob/master/opendlv.odvd#L113-L115
messageIDDistanceReading = 1039
session.registerMessageCallback(messageIDDistanceReading, onDistance, opendlv_standard_message_set_v0_9_10_pb2.opendlv_proxy_DistanceReading)
# Connect to the network session.
session.connect()

################################################################################
# The following lines connect to the camera frame that resides in shared memory.
# This name must match with the name used in the h264-decoder-viewer.yml file.
name = "/tmp/img.bgr"
# Obtain the keys for the shared memory and semaphores.
keySharedMemory = sysv_ipc.ftok(name, 1, True)
keySemMutex = sysv_ipc.ftok(name, 2, True)
keySemCondition = sysv_ipc.ftok(name, 3, True)
# Instantiate the SharedMemory and Semaphore objects.
shm = sysv_ipc.SharedMemory(keySharedMemory)
mutex = sysv_ipc.Semaphore(keySemCondition)
cond = sysv_ipc.Semaphore(keySemCondition)

kiwi = Kiwicar(MAX_STILL_STANDING_FRAMES, MAX_REVERSE_TIME, 0.095)
################################################################################
# Main loop to process the next image frame coming in.
while True:
    groundSteeringRequest = opendlv_standard_message_set_v0_9_10_pb2.opendlv_proxy_GroundSteeringRequest()
    pedalPositionRequest = opendlv_standard_message_set_v0_9_10_pb2.opendlv_proxy_PedalPositionRequest()

    # Wait for next notification.
    cond.Z()
    print ("Received new frame.")

    # Lock access to shared memory.
    mutex.acquire()
    # Attach to shared memory.
    shm.attach()
    # Read shared memory into own buffer.
    buf = shm.read()
    # Detach to shared memory.
    shm.detach()
    # Unlock access to shared memory.
    mutex.release()

    # Turn buf into img array (1280 * 720 * 4 bytes (ARGB)) to be used with OpenCV.
    img = numpy.frombuffer(buf, numpy.uint8).reshape(480, 640, 3)
    if kiwi.terminate:
        kiwi.append_data()
        print("Terminating Run . . .")
        break

    kiwi.move(img, distances["front"], distances["rear"])
    cv2.imshow("image", img)
    cv2.waitKey(2)

    groundSteering, pedalPosition = kiwi.get_state()

    groundSteeringRequest.groundSteering = groundSteering
    pedalPositionRequest.position = pedalPosition

    session.send(1090, groundSteeringRequest.SerializeToString())
    session.send(1086, pedalPositionRequest.SerializeToString())

