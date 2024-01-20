import cv2
import numpy as np

# Initialisation de la vidéo
video = cv2.VideoCapture(0)

if video.isOpened() == False:
    print("Error opening video stream or file")

frame_width = int(video.get(3))
frame_height = int(video.get(4))
size = (frame_width, frame_height)

# Adjusted color range for white and black
limiteBlanc = [([0, 0, 150], [255, 50, 255])]  # Adjusted range for white
limiteNoir = [([0, 0, 0], [180, 255, 50])]      # Adjusted range for black

# Boucle de traitement
while True:

    # Mise en place des filtres
    ret, frame = video.read()
    if not ret:
        break

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Détection de la couleur blanche
    for (lower, upper) in limiteBlanc:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask_white = cv2.inRange(frame_hsv, lower, upper)
        output_white = cv2.bitwise_and(frame, frame, mask=mask_white)

    # Détection de la couleur noire
    for (lower, upper) in limiteNoir:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask_black = cv2.inRange(frame, lower, upper)
        output_black = cv2.bitwise_and(frame, frame, mask=mask_black)

    # Combine the two images to get the black shapes on a white rectangle
    combined_shapes = cv2.bitwise_and(output_white, output_black)

    # Check if a black triangle or star is detected
    _, contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for count in contours:
        epsilon = 0.02 * cv2.arcLength(count, True)
        approx = cv2.approxPolyDP(count, epsilon, True)

        if len(approx) == 3:  # Triangle
            x, y, w, h = cv2.boundingRect(approx)
            if w > 5 and h > 5:
                # Check if it is an equilateral triangle
                side_lengths = [np.linalg.norm(approx[i] - approx[(i + 1) % 3]) for i in range(3)]
                min_side = min(side_lengths)
                max_side = max(side_lengths)
                deviation = max_side - min_side

                if deviation < 20:  # Adjust this threshold based on your requirements
                    cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)
                    cv2.putText(frame, "Equilateral Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (255, 255, 255))

        elif len(approx) == 10:  # Star
            x, y, w, h = cv2.boundingRect(approx)
            if w > 15 and h > 15:
                # Check if all sides of the star are nearly the same length
                side_lengths = [np.linalg.norm(approx[i] - approx[(i + 1) % 10]) for i in range(10)]
                min_side = min(side_lengths)
                max_side = max(side_lengths)
                deviation = max_side - min_side

                if deviation < 20:  # Adjust this threshold based on your requirements
                    cv2.drawContours(frame, [approx], 0, (255, 0, 0), 3)
                    cv2.putText(frame, "Star", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
    
    # Display the result
    cv2.imshow("Detection", frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
video.release()
cv2.destroyAllWindows()
