import numpy as np
import cv2

def detect_chiffre():
    image = cv2.imread("image_zoomee.png")
    
    #Dictionnaire de correspondance
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

    # 7 zones d'intérêt à scanner
    segments = [
        ((int(L/4), 0), (int(L*3/4), int(H/6))),                # haut
        ((0, int(H/6)), (int(L/4), int(H/2))),                  # haut-gauche
        ((int(L*3/4), int(H/6)), (int(L), int(H/2))),           # haut-droite
        ((int(L/4), int(H*2/5)) , (int(L*3/4), int(H*3/5))),    # centre
        ((0, int(H/2)), (int(L/4), int(H*4/5))),                # bas-gauche
        ((int(L*3/4),int(H/2)),(int(L),int(H*5/6))),            # bas-droite
        ((int(L/4), int(H*5/6)), (int(L*3/4), int(H)))          # bas
    ]

    for rect in segments:
        color=tuple(np.random.random(size=3) * 256)
        image=cv2.rectangle(image, rect[0], rect[1],color, 3)

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
        #calculer l'aire du segment
        area = (xB - xA) * (yB - yA)
        # modifier le tableau d'état vu si le nombre de pixels noir dépasse 30% (à affiner en fonction de vos caméras)
        if nbpixels / float(area) > 0.3:
            on[i]= 1

    #Afficher une croix au centre des segments identifiés
    for i in range(len(on)):
        if on[i]==1:
            milsegement=(int((segments[i][0][0]+segments[i][1][0])/2),int((segments[i][0][1]+segments[i][1][1])/2))
            cv2.putText(image, str("X"), milsegement, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    #finalement on va chercher dans le dictinnaire du début quel est le chiffre lu
    if tuple(on) not in correspondances:
        print("🚫 Aucun chiffre trouvé")
        print("On a tenté de rechercher le chiffre : ",on)
        cv2.imshow('Zones trouvées', image)  
        cv2.waitKey(0)
        return 0
    else:
        nombrelu = correspondances[tuple(on)]
        print("✅ On a trouvé le chiffre : ", nombrelu)
        cv2.imshow('Zones trouvées', image)  
        cv2.waitKey(0)
        return 1
    
if __name__ == "__main__":
    detect_chiffre()