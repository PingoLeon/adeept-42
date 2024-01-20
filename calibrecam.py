#import opencv
import cv2
import numpy as np
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

#Initialisation de la vidéo
video = cv2.VideoCapture(0)

if(video.isOpened()==False):
    print("Error opening video stream or file")

frame_width = int(video.get(3))
frame_height = int(video.get(4))
size = (frame_width, frame_height)

#Définition des marges de couleurs
limite1Rouge = [([150,100,100],[180,255,255])]
limite2Rouge = [([0,100,100],[7,255,255])]
limiteVert = [([50, 100, 100], [70, 255, 255])]
limitejaune = [([20, 100, 100], [42, 255, 255])]

# Boucle de traitement
rectangle_positions = []

# Counter for each color
red_counter = 0
green_counter = 0
yellow_counter = 0
triangle_counter = 0

number_of_rectangles_counted = 4

# Threshold for considering rectangles as the same position
position_threshold = 10
triangle_position_threshold = 5

# Keep track of rectangle positions
# Initial positions for each color
initial_red_positions = [(0, 0), (0, 0), (0, 0)]
initial_green_positions = [(0, 0), (0, 0), (0, 0)]
initial_yellow_positions = [(0, 0), (0, 0), (0, 0)]

red_positions = set(initial_red_positions)
green_positions = set(initial_green_positions)
yellow_positions = set(initial_yellow_positions)

#Boucle de traitement
while True:

    #Mise en place des filtres
    ret, frame = video.read()
    if not ret:
        break

    framehsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, framenb = cv2.threshold(framegray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    framedilate = cv2.erode(framenb, kernel, iterations=1)
    frameerode = cv2.dilate(framenb, kernel, iterations=1)
    frame_contours = frame.copy()
    frame_contour = cv2.findContours(frameerode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #Détection de la couleur rouge
    for (lower, upper) in limite1Rouge:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(framehsv, lower, upper)
        output = cv2.bitwise_and(frame, frame, mask=mask)
        #cv2.imshow("images", np.hstack([framehsv, output]))
    for (lower, upper) in limite2Rouge:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask2 = cv2.inRange(framehsv, lower, upper)
        output2 = cv2.bitwise_and(frame, frame, mask=mask2)    
    #Combinaison des deux images pour avoir le rouge complet
    combined_red = cv2.add(output, output2)

    #Détection de la couleur verte
    for (lower, upper) in limiteVert:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask_green = cv2.inRange(framehsv, lower, upper)
        output_green = cv2.bitwise_and(frame, frame, mask=mask_green)

    #Détection de la couleur jaune
    for (lower, upper) in limitejaune:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask_yellow = cv2.inRange(framehsv, lower, upper)
        output_yellow = cv2.bitwise_and(frame, frame, mask=mask_yellow)

    # Check if a red rectangle is detected
    mask_red = cv2.add(mask, mask2)
    _, red_contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for count in red_contours:
        epsilon = 0.02 * cv2.arcLength(count, True)
        approx = cv2.approxPolyDP(count, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if w > 50 and h > 50:
                cv2.drawContours(combined_red, [approx], 0, (0, 255, 0), 3)
                cv2.putText(combined_red, "Rectangle rouge", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
                # Check if the position is close to a previous position
                close_positions = [pos for pos in red_positions if abs(pos[0] - x) < position_threshold and abs(pos[1] - y) < position_threshold]
                if len(close_positions) == 0:
                    # New position detected
                    red_positions.add((x, y))
                # Move the counter increment outside the loop
                red_counter += 1

    # Increment the counter only once per frame
    if red_counter == number_of_rectangles_counted:
        print("Red detected!")
        red_counter = 0
        red_positions.clear()

    # Check if a green rectangle is detected
    _, green_contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for count in green_contours:
        epsilon = 0.02 * cv2.arcLength(count, True)
        approx = cv2.approxPolyDP(count, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if w > 50 and h > 50:
                cv2.drawContours(output_green, [approx], 0, (0, 255, 0), 3)
                cv2.putText(output_green, "Rectangle vert", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
                # Check if the position is close to a previous position
                close_positions = [pos for pos in green_positions if abs(pos[0] - x) < position_threshold and abs(pos[1] - y) < position_threshold]
                if len(close_positions) == 0:
                    # New position detected
                    green_positions.add((x, y))
                # Move the counter increment outside the loop
                green_counter += 1

    # Increment the counter only once per frame
    if green_counter == number_of_rectangles_counted:
        print("Green detected!")
        green_counter = 0
        green_positions.clear()

    # Check if a yellow rectangle is detected
    _, yellow_contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for count in yellow_contours:
        epsilon = 0.02 * cv2.arcLength(count, True)
        approx = cv2.approxPolyDP(count, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if w > 50 and h > 50:
                cv2.drawContours(output_yellow, [approx], 0, (0, 255, 0), 3)
                cv2.putText(output_yellow, "Rectangle jaune", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
                # Check if the position is close to a previous position
                close_positions = [pos for pos in yellow_positions if abs(pos[0] - x) < position_threshold and abs(pos[1] - y) < position_threshold]
                if len(close_positions) == 0:
                    # New position detected
                    yellow_positions.add((x, y))
                # Move the counter increment outside the loop
                yellow_counter += 1

    # Increment the counter only once per frame
    if yellow_counter == number_of_rectangles_counted:
        print("Yellow detected!")
        yellow_counter = 0
        yellow_positions.clear()
        
    combined_all_up = np.hstack([frame_contours, combined_red])
    combined_all_down = np.hstack([output_green, output_yellow])
    combined_final = np.vstack([combined_all_up, combined_all_down])
    cv2.imshow("Final Output", combined_final)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()