import dlib
import cv2

import sys
import numpy as np

import time
from datetime import datetime

# activate python environment, go to folder where this file is located, then run python file_name.py in terminal
sys.path = ['', 'C:\\Users\\User\\Anaconda3\\envs\\hci-env\\python36.zip', 'C:\\Users\\User\\Anaconda3\\envs\\hci-env\\DLLs', 'C:\\Users\\User\\Anaconda3\\envs\\hci-env\\lib', 'C:\\Users\\User\\Anaconda3\\envs\\hci-env', 'C:\\Users\\User\\Anaconda3\\envs\\hci-env\\lib\\site-packages']

def initialize():
    """
    Initializing the dlib functions used throughtout the program
    These detect the face, and predict the location of the facial landmarks

    Parameters
    ----------
    
    Returns
    ----------
    detector : detector object (dlib)
        A frontal face detector object produced by the dlib
    predictor: predictor object (dlib)
        An object to predict facial landmark points using dlib

    """
    detector = dlib.get_frontal_face_detector()
    # download the predictor file at: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    return detector, predictor


def rect_to_bb(rect):
    """
    Take a rect object predicted by dlib and return the x,y corner coordinates
    and the width and height of the rectangle in (x, y, w, h) tuple format.

    Parameters
    ----------
    rect : rect object (dlib)
        rect object generated by dlib frontal face detector

    Returns
    ----------
    (x,y,w,h) : tuple
        tuple with corner, height and wight of bounding box

    """
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    return (x, y, w, h)


def shape_to_np(shape, dtype="int"):
    """
    Take a shape object (that is generated by dlib predictor) and convert that
    into an array containing (x,y) tuples for the coordinates of the facial
    landmark points

    Parameters
    ----------
    shape : shape object (dlib)
        shape object generated by dlib predictor

    Returns
    ----------
    coords : array
        array containing (x,y) tuples for the coordinates of the facial landmark
        points
    """
    coords = np.zeros((68, 2), dtype=dtype)
    # [(0,0),(0,0),(0,0)....68 times]
    # Shape object has 68 landmark points. We extract a landmark point by calculating
    # shape.part(<landmark_number>)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # coords now looks something like [(12,15),(24,78)....68 times]
    return coords


def detect_action_units(shape_coords, rect):
    """
    Detects the presence of action units

    Parameters
    ----------
    shape : array[array]
        contains (x,y) coordinates of 68 facial landmark points
    rect : rect object (dlib)
        rect object generated by dlib frontal face detector

    Returns
    ----------
    au_array : array
        Array identifying action units, 1 indicating presence, 0 otherwise
        Refer array position under Main codes at:
        https://en.wikipedia.org/wiki/Facial_Action_Coding_System
    """

    # Potential idea can be to normalize the landmark points wrt a particular
    # landmark point (for eg. point 27, located between the eyes that has a
    # relatively fixed position)
    au_array = [0]*29
    (x, y, w, h) = rect_to_bb(rect)

    # Indentifying Action Unit 12: Lip Corner Puller
    left_lip_corner_x, left_lip_corner_y = shape_coords[48]
    right_lip_corner_x, right_lip_corner_y = shape_coords[54]

    # distance between the corners = right_lip_corner_x - left_lip_corner_x

#    print((right_lip_corner_x - left_lip_corner_x)/w)

    # 0.32 comes from calculating the neutral difference between the lip corners
    # which can be calculated using: (right_lip_corner_x - left_lip_corner_x)/w
    smile_param = 0.09 # can be adjusted for different faces
    if (((right_lip_corner_x - left_lip_corner_x)/w)>0.32+smile_param):
        au_array[12] = 1

    # FILL IN CODE FOR INDENTIFYING DIFFERENT ACTION UNITS
    
    # Question 2: 
    
    ### Action unit 5: upper eye lid raiser (could user outter and inner, using 
    #       only outter landmark )
    
    ### I have asian eyes, so my eye parameters may be smaller
    #out = outisde of the eye, in = inner of the eye (towards center)
    top_out_left_eye_x, top_out_left_eye_y = shape_coords[37] 
    top_in_left_eye_x, top_in_left_eye_y = shape_coords[38]
    
    # right eye anchor points
    top_out_right_eye_x, top_out_right_eye_y = shape_coords[44] 
    top_in_right_eye_x, top_in_right_eye_y = shape_coords[43]
    
    
    ###bottom of the eye to measure against
    bottom_out_left_eye_x, bottom_out_left_eye_y = shape_coords[41]
    bottom_in_left_eye_x, bottom_in_left_eye_y = shape_coords[40]
    # right eye
    bottom_out_right_eye_x, bottom_out_right_eye_y = shape_coords[46]
    bottom_in_right_eye_x, bottom_in_right_eye_y = shape_coords[47]
#    print("eye", abs((top_out_left_eye_y - bottom_out_left_eye_y)/h))
    upper_eye_param = 0.02
    # .006 is neutral
    if (abs((top_out_left_eye_y - bottom_out_left_eye_y)/h) > .037 + upper_eye_param):
      au_array[5] = 1
    
    ### Action unit 26: jaw drop
    bottom_jaw_x, bottom_jaw_y = shape_coords[8]
    #reference point: landmark 30 ie shape_coords[31] as a static point
    nose_reference_x, nose_reference_y = shape_coords[29]
    jaw_param = .12
#    print("jawDrop",abs(nose_reference_y - bottom_jaw_y)/h)
    if (abs((nose_reference_y - bottom_jaw_y)/h) > .6 + jaw_param ):
      au_array[26] = 1
      
    
    ### Action unit 4: brow lowerer
    # 
    left_brow_x, left_brow_y = shape_coords[21]
    
    right_brow_x, right_brow_y = shape_coords[22]
#    print("brow: ",abs(left_brow_x - right_brow_x )/w)
    inner_brow_param = .034
    # if the brows shrink closer together ie frown, they should be less than the param
    if ((abs(left_brow_x - right_brow_x )/w) < .1374 - inner_brow_param):
      au_array[4] = 1
      
      
    ### Action unit 23: lip tightener: using outer points of the lips
#    print("lip tightener: ", abs((right_lip_corner_x - left_lip_corner_x)/w))
    lip_tighten_param = 0.035 # can be adjusted for different faces
    if (abs((right_lip_corner_x - left_lip_corner_x)/w) < 0.34 - lip_tighten_param):
        au_array[23] = 1
        
    ### Extra Credit: sadness
    ### action unit 15: lip depressor 
    print("lip lowerer:",  abs((nose_reference_y-right_lip_corner_y)/h))
   
    if (abs((nose_reference_y-right_lip_corner_y)/h) > 0.355):
        au_array[15] = 1
    
    return au_array
  


def identify_expression(au_array, frame, rect):
    """
    Identifies facial expression based on action unit array values

    Parameters
    ----------
    au_array : array
        Action Unit array generated by the detect_action_units function
    frame : frame object (OpenCV)
        OpenCV frame produced using the VideoCapture Function
    rect : rect object (dlib)
        rect object generated by dlib frontal face detector

    Returns
    ----------
    updated_frame : frame object (OpenCV)
        Image frame with an identifier for facial expressions
    """

    # Happines, Surprise, Angry

    (x, y, w, h) = rect_to_bb(rect)
    # Expression for Happiness is AU 6 + AU 12
    # Currently only using AU 12
    if au_array[12]==1:
        cv2.putText(frame, "Happiness", (x-10, y-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        return frame

      
    
    # FILL IN CODE FOR VARIOUS EXPRESSIONS
    # Expression for Surprise is AU 5 + AU 26
    
    ### Question 2: surprise
#    if au_array[26] == 1:
#        cv2.putText(frame, "Jaw Drops", (x-10, y-10),
#        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
#        return frame
#    if au_array[5] == 1:
#        cv2.putText(frame, "Eye Elevates", (x-10, y-10),
#        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
#        return frame
      
    # After talking to Ivy the TA, using only one action unity to test for surprise or anger
    elif au_array[5] == 1:#and au_array[26] == 1:
        cv2.putText(frame, "Surprise", (x-10, y-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        return frame
    # Expression for Anger is AU 4(Brow Lowerer),5(Upper Lid Raiser), and optionally 23
    
    ### Extra credit: sadness: frown and action unit 15: lower your lips down
    # need to have this before otherwise anger is returned as the frame first 
    elif au_array[4] == 1 and au_array[15] == 1:
        cv2.putText(frame, "Sadness", (x-10, y-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        return frame
      
    ### Question 3: anger
    elif au_array[4] == 1:#and au_array[23]==1:
        cv2.putText(frame, "Anger", (x-10, y-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        return frame

#    elif au_array[23] == 1:
#        cv2.putText(frame, "Lip Tightens", (x-10, y-10),
#        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
#        return frame
    # elif au_array[4]==1 and au_array[5]==1 and au_array[23]==1:
    

    return frame


def stream_start():
    """
    Starts the video stream to process facial expressions and opens up a Video
    window when a face is detected

    Parameters
    ----------

    Returns
    ----------
    Press the Esc key to exit the program
    """

    print("Preparing the Program")
    detector, predictor = initialize()
    time.sleep(3.0)


    print("[INFO] Starting Camera...")
    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()
        keyPress = 0
        if cap.isOpened():
            # Convert image to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape_coords = shape_to_np(shape)

                # We create the red dots here
                for (x, y) in shape_coords:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

                (x, y, w, h) = rect_to_bb(rect)
                cv2.rectangle(frame, (x, y), (x+h, y+h), (0, 255, 0), 2)

                au_array = detect_action_units(shape_coords, rect)

                updated_frame = identify_expression(au_array,frame,rect)

                cv2.imshow("Frame",updated_frame)
                keyPress = cv2.waitKey(1)
                # if keyPress==27: # ASCII for Esc Key
                #     break

            if keyPress==27: # ASCII for Esc Key
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    stream_start()
