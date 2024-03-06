import numpy as np
import cv2

# Dictionnaire et paramètres pour la détection des ArUCo (4x4, 250 IDs max)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Ouvrir la webcam
cap = cv2.VideoCapture(0)

#Commencer la capture d'un flux vidéo
while True:
    # Lire une frame
    ret, frame = cap.read()

    # Détection des markers Arucos dans la frame
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)

    # Si au moins un marker ArUCo est détecté, ça mérite de l'attention
    if len(markerCorners) > 0:
        ids = markerIds.flatten()

        # On va aller regarder chaque marker ArUCo détecté
        all_corners = []
        for (markerCorner, markerID) in zip(markerCorners, ids):
            # On extrait les coords des coins du marker ArUCo
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # On convertit les coords en entiers (pour le dessin)
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # Draw a quadrilateral around the ArUCo marker
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # Calculate and draw a red dot at the center of the ArUCo marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

            # Display the ArUCo marker ID
            cv2.putText(frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

            print("[INFO] ArUco marker ID: {}".format(markerID))

            all_corners.append(corners)

        # If we have at least 4 markers, we can define a square
        if len(all_corners) >= 3:
            # Combine all corners into a single array
            all_corners = np.concatenate(all_corners)

            # If only three markers are detected, estimate the fourth one
            if len(all_corners) == 3:
                centroid = np.mean(all_corners, axis=0)
                fourth_corner = 2*centroid - all_corners[0] - all_corners[1]
                all_corners = np.append(all_corners, [fourth_corner], axis=0)

            # Calculate the top-left, top-right, bottom-right, and bottom-left corners of the square
            top_left = np.min(all_corners, axis=0)
            bottom_right = np.max(all_corners, axis=0)
            top_right = np.array([bottom_right[0], top_left[1]])
            bottom_left = np.array([top_left[0], bottom_right[1]])

            # Define the points for perspective transformation
            points1 = np.float32([top_left, top_right, bottom_right, bottom_left])
            points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

            # Calculate the perspective transformation matrix
            vecttrans = cv2.getPerspectiveTransform(points1, points2)

            # Apply the perspective transformation to the square
            zoomed_square = cv2.warpPerspective(frame, vecttrans, (200, 200))

            # Display the zoomed square
            cv2.imshow("Zoomed Square", zoomed_square)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
