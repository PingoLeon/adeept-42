import cv2
import numpy as np


imageread = cv2.imread('opencv1.png')
#mesurons l'image
h,w=imageread.shape[:2]
print('w = '+str(w))
print('h = '+str(h))
#specifions d'abord la positions de points dans la première image puis leurs position dans la nouvelle
points1 = np.float32([[268, 239], [514, 209], [350, 430], [600, 402]])
points2 = np.float32([[0, 100], [w, 0], [0, h], [w, h]])
#calculons une matrice de transformation
vecttrans = cv2.getPerspectiveTransform(points1, points2)
#appliquons la transformation" à l'image d'orgine,spécifions un taille
finalimage = cv2.warpPerspective(imageread, vecttrans, (w, h))
#displaying the original image and the transformed image as the output on the screen
cv2.imshow('Source_image', imageread)
cv2.imshow('Destination_image', finalimage)
cv2.waitKey(0)
cv2.destroyAllWindows()