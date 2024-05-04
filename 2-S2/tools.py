import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import ultra

def checkdist_average():
    distance_list = []
    while len(distance_list) < 5:
        distance = ultra.checkdist() * 100
        distance_list.append(distance)
    
    average_distance = sum(distance_list) / len(distance_list)
    print("📡 %.2f cm" % average_distance)
    return average_distance