import numpy as np
import cv2, PIL
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import cv2


'''
#!Détection d'Arucos et entourer les coins de l'aruco avec un quadrilatère
#!Pas de maière directe en live
'''


'''The cv2.aruco.detectMarkers
#results in a 3-tuple of:

corners
: The (x, y)-coordinates of our detected ArUco markers

ids
: The identifiers of the ArUco markers (i.e., the ID encoded in the marker itself)

rejected
: A list of potential markers that were detected but ultimately rejected due to the code inside the marker not being able to be parsed
'''


#prendre 5 photos à partir de la webcam
camera = cv2.VideoCapture(0)
return_value, image = camera.read()
cv2.imwrite('opencv1.png', image)
del(camera)

#définir le dictionnaire de travail et les paramètres de détection et instancier le détecteur
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters =  cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

#On prend un des images générées par la webcam
image = cv2.imread('opencv1.png')

#stocker les arucos détectés : les positions de leurs coins, leur identifiants et les éventuelles erreurs
markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)

print(f'Nombre d\'aruco détectés : {len(markerCorners)}')
print(f'IDs : {markerIds}')
print(f'LES COINS : {markerCorners}')

# verifier qu'au moins un aruco est détecté
if len(markerCorners) > 0:
	ids = markerIds.flatten()
	# boucle pour chaque aruco détecté
	for (markerCorner, markerID) in zip(markerCorners, ids):
		# extraire les angles des aruco (toujours dans l'ordre
		# haut-gauche, haut-droite, bas-gauche, bas-droit)
		corners = markerCorner.reshape((4, 2))
		(topLeft, topRight, bottomRight, bottomLeft) = corners
		# convertir en entier (pour l'affichage)
		topRight = (int(topRight[0]), int(topRight[1]))
		bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
		bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
		topLeft = (int(topLeft[0]), int(topLeft[1]))
		
        # dessiner un quadrilatère autour de chaque aruco
		cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
		cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
		cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
		cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
		# calculer puis afficher un point rouge au centre
		cX = int((topLeft[0] + bottomRight[0]) / 2.0)
		cY = int((topLeft[1] + bottomRight[1]) / 2.0)
		cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
		# affiher l'identifiant
		cv2.putText(image, str(markerID),
			(topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 255, 0), 2)
		print("[INFO] ArUco marker ID: {}".format(markerID))
	# afficher l'image
	cv2.imshow("Image", image)
	cv2.waitKey(0)
