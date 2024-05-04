import numpy as np
import cv2

def detect_fleche(image):

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


    