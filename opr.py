import cv2
import math

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def remap(value_to_map, new_range_min, new_range_max, old_range_min, old_range_max):

    remapped_val = (value_to_map - old_range_min) * (new_range_max - new_range_min) / (old_range_max - old_range_min) + new_range_min
    if(remapped_val>new_range_max):
        remapped_val = new_range_max
    elif (remapped_val < new_range_min):
        remapped_val = new_range_min

    return remapped_val

def find_face(image_to_check, max_target_distance):
    gray = cv2.cvtColor(image_to_check, cv2.COLOR_BGR2GRAY) #resmi siyah beyaza çevir
    
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)     #yüzlere bak


    if len(faces) >= 1: #yüz bulunursa
        faces = list(faces)[0] #birden fazla yüz bulunursa ilkini kullan

        x = faces[0]
        y = faces[1]
        w = faces[2]
        h = faces[3]

        center_face_X = int(x + w / 2)
        center_face_Y = int(y + h / 2)
        height, width, channels = image_to_check.shape

        distance_from_center_X = (center_face_X - width/2)/220 # bunu yaptık
        distance_from_center_Y = (center_face_Y - height/2)/195 # bunu da...

        target_distance = math.sqrt((distance_from_center_X*220)**2 + (distance_from_center_Y*195)**2) # görüntü merkezi ve yüz merkezi arasındaki mesafeyi hesapla

        if target_distance < max_target_distance :#eklenen geometri rengini ayarla
            locked = True
            color = (0, 255, 0)   #yeşil renk bgr
        else:
            locked = False
            color = (0, 0, 255)   # kırmızı renk bgr


        cv2.rectangle(image_to_check,(center_face_X-10, center_face_Y), (center_face_X+10, center_face_Y),    #+ nın ilk çizgisini yatay olarak çiz
                      color, 2)
        cv2.rectangle(image_to_check,(center_face_X, center_face_Y-10), (center_face_X, center_face_Y+10),    #+ nın 2. çizgisini düşey olarak çiz
                      color,2)

        cv2.circle(image_to_check, (int(width/2), int(height/2)), int(max_target_distance) , color, 2)    #yuvarlak çiz

        return [True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]

    else:
        return [False]
