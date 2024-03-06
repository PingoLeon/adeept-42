#code Python nécessitant OpenCV2 permettant de déterminer l'orientation d'une flèche
import numpy as np
import cv2

#ce code travaille par image, on spécifie l'image source
img = cv2.imread('Cours1 S2-20240228\\flecheD.jpg')

#!réduisons le bruit en utilisant un flou, on fait un flou sur 11 voisins :
img = cv2.GaussianBlur(img, (11,11), 0)

#!On travaille sur une image en niveau de gris
#?on pourrait également binariser l'image, mais il faudrait calculer un seuil
#la fonction goodFeaturesToTrack le fait déjà assez bien par elle même
img_gris = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#!on calcule les sommets avec une fonction bien pratique d'openCV
#une flèche devrait avoir 7 sommets
sommets = np.int0(cv2.goodFeaturesToTrack(img_gris,7,0.01,10))

#par principe de déboguage on afiche en console les différents sommets trouvés :
#cette boucle peut donc être supprimée
for i,vals in enumerate(sommets):
    x,y = vals.ravel()
    print('sommet '+str(i)+' : '+str(x)+','+str(y))
    #les lignes suivantes permettent un rendu visuel pour débugger
    cv2.circle(img,(x,y),3,(255,255,0),-1)
    cv2.putText(img, str(i), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv2.LINE_AA )

#on prends les sommets les plus éloignés
xmax, ymax = (np.max(sommets, axis = 0)).ravel()
xmin, ymin = (np.min(sommets, axis = 0)).ravel() 

#déterminons l'axe du milieu de notre flèche, puis traçons le visuellemet (cv2.line)
xmil=int(xmin+((xmax-xmin)/2))
cv2.line(img,(xmil,0),(xmil,img.shape[0]),(255,0,0),2)

#on compte le nombre v de sommets à gauche puis à droite de notre milieu
#au vu de la forme de notre flèche le nombre de sommmets est dans la partie "pointe" notre flèche
nbSommetsDroite=np.count_nonzero(sommets[:,0,0]>xmil)
nbSommetsGauche=np.count_nonzero(sommets[:,0,0]<xmil)

#on finit par afficher le sens de notre flèche
if nbSommetsDroite>nbSommetsGauche:
    print('Droite')
else:
    print('Gauche')


#les prochaines lignes ne servent qu'à l'affichage graphique
cv2.imshow('image',img)
k=cv2.waitKey(0) & 0xff
if k==27:
    cv2.destroyAllWindows()

#NOTA : cette approche est fonctionelle mais vous pouvez l'adapter
#       par exemple, ce code fonctionne mal si la partie triangle est plus grande que le rectangle.
#       on pourrait alors par exemple utiliser plus de sommets pour définir l'axe du milieu
#       on peut aussi utiliser le fait que le bout de la flèche est le seul avec un angle aigu très petit devant 90°
#       n'hésitez pas à expérimenter vos propres codes d'analyse à partir des sommets


#?Pistes d'amélioration : 
    
#!regarder l'orientation au niveau du sommet de la flèche (sur le triangle directement en
#!ren regardant de quel côté trouve t-on un sommet loin et non aligné avec les deux autres sommets en vertical)
    
#!Calculer l'angle aigu du bout de flèche (le seul angle aigu de la flèche) (peut marcher maus nécessite beaucoup de failsafe)