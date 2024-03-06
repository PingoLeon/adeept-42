import numpy as np
import cv2

# Define the dictionary and parameters for ArUCo detection
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Detect ArUCo markers in the frame
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)

    # If at least one ArUCo marker is detected
    if len(markerCorners) > 0:
        ids = markerIds.flatten()

        # Loop over each detected ArUCo marker
        all_corners = []
        for (markerCorner, markerID) in zip(markerCorners, ids):
            # Extract the corners of the ArUCo marker
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # Convert the corner coordinates to integers (for drawing)
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

        # If we have exactly 3 markers, we can determine the position of the fourth marker
        if len(all_corners) == 3:
            # Extract the corners of the first three markers
            corners1 = all_corners[0]
            corners2 = all_corners[1]
            corners3 = all_corners[2]

            # Determine the position of the fourth marker
            if np.linalg.norm(corners1[0] - corners2[0]) < np.linalg.norm(corners1[0] - corners2[1]):
                # The first and second markers are horizontally adjacent
                if np.linalg.norm(corners1[0] - corners3[0]) < np.linalg.norm(corners1[0] - corners3[1]):
                    # The first and third markers are horizontally adjacent
                    fourth_corner = corners1[2] + (corners2[2] - corners1[2]) + (corners3[2] - corners1[2])
                else:
                    # The first and third markers are vertically adjacent
                    fourth_corner = corners1[3] + (corners2[3] - corners1[3]) + (corners3[3] - corners1[3])
            else:
                # The first and second markers are vertically adjacent
                if np.linalg.norm(corners1[0] - corners3[0]) < np.linalg.norm(corners1[0] - corners3[1]):
                    # The first and third markers are horizontally adjacent
                    fourth_corner = corners1[1] + (corners2[1] - corners1[1]) + (corners3[1] - corners1[1])
                else:
                    # The first and third markers are vertically adjacent
                    fourth_corner = corners1[0] + (corners2[0] - corners1[0]) + (corners3[0] - corners1[0])

            # Convert the fourth corner coordinates to integers (for drawing)
            fourth_corner = (int(fourth_corner[0]), int(fourth_corner[1]))

            # Draw a red dot at the calculated position of the fourth marker
            cv2.circle(frame, fourth_corner, 4, (0, 0, 255), -1)

            # Define the points for perspective transformation
            points1 = np.float32([all_corners[0][0], all_corners[1][0], all_corners[2][0], fourth_corner])
            points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

            # Calculate the perspective transformation matrix
            vecttrans = cv2.getPerspectiveTransform(points1, points2)

            # Apply the perspective transformation to the rectangle
            zoomed_rectangle = cv2.warpPerspective(frame, vecttrans, (200, 200))

            # Display the zoomed rectangle
            cv2.imshow("Zoomed Rectangle", zoomed_rectangle)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
