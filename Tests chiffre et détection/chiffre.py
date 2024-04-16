import cv2
import numpy as np

image = cv2.imread("image_zoomee.png")

#créons un dictionnaire de correspondance entre état des segement set valeur lue
correspondances = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 0, 1): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1):5,
    (1, 1, 0, 1, 1, 1, 1):6,
    (1, 0, 1, 0, 0, 1, 0):7,
    (1, 1, 1, 1, 1, 1, 1):8,
    (1, 1, 1, 1, 0, 1, 1):9
}

(H, L) = image.shape[:2] #récupérer la hauteur et largeur de l'image

# définir 7 zones d'intérêts, une par segment
#complétez les positions des rengles définissants les zones d'intérêts
#on propose d'utiliser une grille 6x4 sauf pour le centre
segments = [
	((int(L/4), 0), (int(L*3/4), int(H/6))),  # haut
	((0, int(H/6)), (int(L/4), int(H/2))),  # haut-gauche
	((int(L*3/4), int(H/6)), (int(L), int(H/2))),  # haut-droite
	((int(L/4), int(H*2/5)) , (int(L*3/4), int(H*3/5))),  # centre
	((0, int(H/2)), (int(L/4), int(H*4/5))),  # bas-gauche
	((int(L*3/4),int(H/2)),(int(L),int(H*5/6))),  # bas-droite
	((int(L/4), int(H*5/6)), (int(L*3/4), int(H)))  # bas
]

for rect in segments:
    color=tuple(np.random.random(size=3) * 256)
    image=cv2.rectangle(image, rect[0], rect[1],color, 3)
cv2.imshow('segments', image) #optionnel


#passer en niveau de gris
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#définir un seuil et binariser l'image
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
#nettoyer l'image avec un morphose (optionnel)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

#créer un tableau des états vus des segments (1 le segment est noir, 0 le segment est blanc)
on = [0] * len(segments) 

#voir l'état pour chaque segment :
for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
	# extraire une image binaire de la zone d'intérêt correspondant au segment
	segROI = thresh[yA:yB, xA:xB]
	#compter le nombre de pixel noir
	nbpixels = cv2.countNonZero(segROI)
	print("segment "+str(i)+" a "+ str(nbpixels) +" pixels non blancs")
	#calculer l'aire du segment
	area = (xB - xA) * (yB - yA)
	# modifier le tableau d'état vu si le nombre de pixels noir dépasse 30% (à affiner en fonction de vos caméras)
	if nbpixels / float(area) > 0.3:
		on[i]= 1

print(on) #optionnel

#optionnel : afficher une croix au centre des segments identifiés
for i in range(len(on)):
	if on[i]==1:
		milsegement=(int((segments[i][0][0]+segments[i][1][0])/2),int((segments[i][0][1]+segments[i][1][1])/2))
		cv2.putText(image, str("X"), milsegement,
		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#finalement on va chercher dans le dictinnaire du début quel est le chiffre lu
nombrelu = correspondances[tuple(on)]

print(nombrelu)

cv2.imshow('test', image)  
cv2.waitKey(0)