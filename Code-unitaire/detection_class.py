import numpy as np
import cv2

class Detection:
    def __init__(self):
        pass

    def chiffre(self,image):
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
        
        cv2.imwrite('ChiffreOutput.png', image)

        #finalement on va chercher dans le dictinnaire du début quel est le chiffre lu
        if tuple(on) not in correspondances:
            print("🚫 Aucun chiffre trouvé")
            print("🤔 On a tenté de rechercher le chiffre : ",on)
            return 0
        else:
            nombrelu = correspondances[tuple(on)]
            print("✅ On a trouvé le chiffre : ", nombrelu)
            return 1
        
    def rectangle(self, image):
        # Définir les plages de couleur comme des variables globales
        limite1Rouge = [([179,100,100],[180,255,255])]
        limite2Rouge = [([0,100,100],[9,255,255])]
        limiteVert = [([40, 100, 100], [80, 255, 255])]
        limiteJaune = [([20, 100, 100], [42, 255, 255])]
        
        # Convertir l'image en HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Créer des masques pour chaque couleur
        mask_red1 = cv2.inRange(hsv, np.array(limite1Rouge[0][0]), np.array(limite1Rouge[0][1]))
        mask_red2 = cv2.inRange(hsv, np.array(limite2Rouge[0][0]), np.array(limite2Rouge[0][1]))
        mask_green = cv2.inRange(hsv, np.array(limiteVert[0][0]), np.array(limiteVert[0][1]))
        mask_yellow = cv2.inRange(hsv, np.array(limiteJaune[0][0]), np.array(limiteJaune[0][1]))

        # Compter le nombre de pixels de chaque couleur
        count_red = cv2.countNonZero(mask_red1) #+ cv2.countNonZero(mask_red2)
        count_green = cv2.countNonZero(mask_green)
        count_yellow = cv2.countNonZero(mask_yellow)

        # Créer un dictionnaire pour mapper les noms de couleur aux emojis
        color_emoji_map = {
            "red": "\U0001F534",  # Emoji de cercle rouge
            "green": "\U0001F7E2",  # Emoji de cercle vert
            "yellow": "\U0001F7E1"  # Emoji de cercle jaune
        }
        
        # Créer un dictionnaire pour mapper les noms de couleur aux valeurs de retour
        color_return_map = {
            "red": 1,
            "yellow": 2,
            "green": 3,
            
        }
        
        # Trouver la couleur avec le plus grand nombre de pixels
        max_color = max([("red", count_red), ("green", count_green), ("yellow", count_yellow)], key=lambda x: x[1])

        # Retourner la valeur correspondante
        return color_return_map[max_color[0]] 
    
    def fleche(self, image):

        #réduisons le bruit en utilisant un flou gaussien
        image = cv2.GaussianBlur(image, (11,11), 0)
        #On travaille sur une image en niveau de gris
        image_gris = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        #on calcule les sommets avec une fonction bien pratique d'openCV, en prenant les 7 meilleurs sommets d'une éventuelle figure
        sommets = np.intp(cv2.goodFeaturesToTrack(image_gris,7,0.01,10))
        if sommets is None:
            print("🚫 Erreur : pas de sommets détectés !")
            return 0
            
        #rendu visuel pour débugger
        for i,vals in enumerate(sommets):
            x,y = vals.ravel()
            cv2.circle(image,(x,y),3,(255,255,0),-1)
            cv2.putText(image, str(i), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv2.LINE_AA )
            
        #on prends les sommets les plus éloignés
        xmax, ymax = (np.max(sommets, axis = 0)).ravel()
        xmin, ymin = (np.min(sommets, axis = 0)).ravel() 

        #déterminons l'axe du milieu de notre flèche, puis traçons le visuellemet (cv2.line)
        xmil=int(xmin+((xmax-xmin)/2))
        cv2.line(image,(xmil,0),(xmil,image.shape[0]),(255,0,0),2)

        #au vu de la forme de notre flèche le nombre de sommmets le plus grand est dans la partie "pointe" notre flèche
        nbSommetsDroite=np.count_nonzero(sommets[:,0,0]>xmil)
        nbSommetsGauche=np.count_nonzero(sommets[:,0,0]<xmil)

        print("🎯 Flèche détectée ! Son sens est à ", end="")
        
        #on finit par afficher le sens de notre flèche
        if nbSommetsDroite>nbSommetsGauche:
            print('Droite ➡️')
            cv2.imwrite("FlecheOutput.png",image)
            return 4
        else:
            print('Gauche ⬅️')
            cv2.imwrite("FlecheOutput.png",image)
            return 5