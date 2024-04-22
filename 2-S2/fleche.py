import numpy as np
import cv2

def detect_fleche():
    img = cv2.imread('image_zoomee.png')

    #réduisons le bruit en utilisant un flou gaussien
    img = cv2.GaussianBlur(img, (11,11), 0)
    #On travaille sur une image en niveau de gris
    img_gris = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #on calcule les sommets avec une fonction bien pratique d'openCV, en prenant les 7 meilleurs sommets d'une éventuelle figure
    sommets = np.intp(cv2.goodFeaturesToTrack(img_gris,7,0.01,10))
    if sommets is None:
        print("🚫 Erreur : pas de sommets détectés !")
        return 0
        
    #rendu visuel pour débugger
    for i,vals in enumerate(sommets):
        x,y = vals.ravel()
        cv2.circle(img,(x,y),3,(255,255,0),-1)
        cv2.putText(img, str(i), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv2.LINE_AA )
        
    #on prends les sommets les plus éloignés
    xmax, ymax = (np.max(sommets, axis = 0)).ravel()
    xmin, ymin = (np.min(sommets, axis = 0)).ravel() 

    #déterminons l'axe du milieu de notre flèche, puis traçons le visuellemet (cv2.line)
    xmil=int(xmin+((xmax-xmin)/2))
    cv2.line(img,(xmil,0),(xmil,img.shape[0]),(255,0,0),2)

    #au vu de la forme de notre flèche le nombre de sommmets le plus grand est dans la partie "pointe" notre flèche
    nbSommetsDroite=np.count_nonzero(sommets[:,0,0]>xmil)
    nbSommetsGauche=np.count_nonzero(sommets[:,0,0]<xmil)

    print("🎯 Flèche détectée ! Son sens est à ", end="")
    #on finit par afficher le sens de notre flèche
    if nbSommetsDroite>nbSommetsGauche:
        print('Droite')
        
        #les prochaines lignes ne servent qu'à l'affichage graphique
        cv2.imshow('Flèche trouvée !',img)
        cv2.waitKey(0)
        
        return 4
    else:
        print('Gauche')
        
        #les prochaines lignes ne servent qu'à l'affichage graphique
        cv2.imshow('Flèche trouvée !',img)
        cv2.waitKey(0)
        
        return 5
    
if __name__ == "__main__":
    detect_fleche()


    