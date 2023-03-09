import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.uic import loadUi
import opr
import kom_ard
import random
import pickle

import cv2


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.ui = loadUi('grafik.ui', self)    #Pencere düzenini tanımla

        self.setMouseTracking(True)    #fare izlemeye izin ver (manuel modda kullan)
        self.manual_mode = False       #izleme yüz modunda başlamak için manuel modu false olarak ayarla
        self.LED_ON = True             #LED'i açık moda ayarla
        self.CameraID = 0             #kamera kimliğini tanımla, ilk kamera = ID 0, ikinci ID 1 vb.

        self.rec = True                #kamera kaydının başlatılmasına izin ver
        self.cap = cv2.VideoCapture(self.CameraID)  #açık CV kamera kaydını tanımla
        self.cap.set(3, 960)                        #yakalama genişliğini ayarlama
        self.cap.set(4, 540)                        #yakalama yüksekliğini ayarlama
        #Görüntü ne kadar büyük olursa, işlemin işlenmesi de o kadar uzun sürer
        ## hiç kasmaya gerek yok.

        self.min_tilt = 22          #derece olarak minimum eğim açısı (yukarı / aşağı açı)
        self.max_tilt = 80          #derece olarak maksimum eğim açısı
        self.current_tilt = 0       #geçerli eğim (arduino'dan alınan ve LCD numaralarında görüntülenen bilgiler)
        self.target_tilt = 90      #ulaşılması gereken eğim açısı

        self.min_pan = 80            #derece cinsinden minimum pan açısı (sol / sağ açı)
        self.max_pan = 100         #derece olarak maksimum pan açısı
        self.current_pan = 80        #geçerli pan (arduino'dan alınan ve LCD numaralarında görüntülenen bilgiler)
        self.target_pan = 90       #ulaşılması gereken kaydırma açısı

        self.roam_target_pan = 90
        self.roam_target_tilt = 90
        self.roam_pause = 40      #dolaşım eğimi veya kaydırma hedefine ulaşıldığında kameranın duraklatacağı kare miktarı
        self.roam_pause_count = self.roam_pause   #geçerli duraklama kare sayısı


        self.is_connected = False    #arduino bağlıysa boole tanımlaması

        self.InvertPan = False       #panın çevrilmesine izin ver
        self.InvertTilt = False      #eğimin çevrilmesine izin ver

        self.face_detected = False     #bir yüzün algılanıp algılanmadığını tanımlama
        self.target_locked = False     #algılanan yüzün yakalanan görüntünün merkezine yeterince yakın olup olmadığını tanımla
        self.max_target_distance = 30  #kilitli hedefi ayarlamak için yüz / görüntü merkezi arasındaki minimum mesafe
        self.max_empty_frame = 100      #dolaşıma başlamadan önce boş çerçeve sayısı (yüz algılanmadı) algılandı
        self.empty_frame_number = self.max_empty_frame   #geçerli boş kare sayısı

        self.ard = kom_ard.ard_connect(self)     #arduino ile iletişime izin veren nesne yarat
        self.initUI()    #kullanıcı arayüzünü ayarlama (aşağıya bakkkk)

    def initUI(self):     #UI ile ilgili şeyler
        self.setWindowTitle('yüz izleme')              #pencere başlığını ayarla
        self.label = self.ui.label                      #etiketi ayarla (çekilen görüntüleri görüntülemek için kullanılacaktır)
        self.QuitButton = self.ui.QuitButton            #çıkış düğmesini ayarla
        self.PauseButton = self.ui.PauseButton          #durdur düğmesini ayarla
        self.Pan_LCD = self.ui.Pan_LCD                  #vsvsvs
        self.Tilt_LCD = self.ui.Tilt_LCD                #...
        self.Manual_checkbox = self.ui.Manual_checkbox  #...
        self.ConnectButton = self.ui.ConnectButton
        self.COMlineEdit = self.ui.COMlineEdit
        self.COMConnectLabel = self.ui.COMConnectLabel
        self.UpdateButton = self.ui.UpdateButton
        self.MinTiltlineEdit = self.ui.MinTiltlineEdit
        self.MaxTiltlineEdit = self.ui.MaxTiltlineEdit
        self.InvertTilt_checkbox = self.ui.InvertTilt_checkbox
        self.InvertTilt = self.InvertTilt_checkbox.isChecked()
        self.MinPanlineEdit = self.ui.MinPanlineEdit
        self.MaxPanlineEdit = self.ui.MaxPanlineEdit
        self.InvertPan_checkbox = self.ui.InvertPan_checkbox
        self.InvertPan = self.InvertPan_checkbox.isChecked()
        self.TiltSensivityEdit = self.ui.TiltSensivityEdit
        self.TiltSensivity = 1
        self.PanSensivityEdit = self.ui.PanSensivityEdit
        self.PanSensivity = 1
        self.LED_checkbox = self.ui.LED_checkbox
        self.CameraIDEdit = self.ui.CameraIDEdit

        self.QuitButton.clicked.connect(self.quit)               
        self.PauseButton.clicked.connect(self.toggle_recording)  
        self.Manual_checkbox.stateChanged.connect(self.set_manual_mode)  #vsvsvs
        self.ConnectButton.clicked.connect(self.connect)
        self.UpdateButton.clicked.connect(self.update_angles)

        self.load_init_file()
        self.update_angles() 

        self.record()  #kayda başla

    def load_init_file(self):
        #bu yöntem, yazılımı kapattıktan sonra bile metin kutularına girilen en son değerlerin yeniden yüklenmesini sağlar
        try:         #Varsa init dosyasını açmaya çalışın
            with open('init.pkl', 'rb') as init_file:
                var = pickle.load(init_file)  #tüm değişkenleri yükle ve metin kutularını güncelle
                self.COMlineEdit.setText(var[0])
                if(var[4]):
                    self.MinTiltlineEdit.setText(str(var[2]))
                    self.MaxTiltlineEdit.setText(str(var[1]))
                else:
                    self.MinTiltlineEdit.setText(str(var[1]))
                    self.MaxTiltlineEdit.setText(str(var[2]))
                self.TiltSensivityEdit.setText(str(var[3]))
                self.InvertTilt_checkbox.setChecked(var[4])
                if (var[8]):
                    self.MinPanlineEdit.setText(str(var[6]))
                    self.MaxPanlineEdit.setText(str(var[5]))
                else:
                    self.MinPanlineEdit.setText(str(var[5]))
                    self.MaxPanlineEdit.setText(str(var[6]))
                self.PanSensivityEdit.setText(str(var[7]))
                self.InvertPan_checkbox.setChecked(var[8])
                #self.CameraIDEdit.setText(str(var[9]))
                self.LED_checkbox.setChecked(var[10])
            print(var)
            #değişkenleri ayarla
        except:
            pass

    def save_init_file(self):
        init_settings = [self.COMlineEdit.text(),
        self.min_tilt, self.max_tilt, self.TiltSensivity, self.InvertTilt,
        self.min_pan, self.max_pan, self.PanSensivity, self.InvertPan,
        self.CameraID, self.LED_ON]
        with open('init.pkl', 'wb') as init_file:
            pickle.dump(init_settings, init_file)


    def connect(self):    #Arduino zaten bağlı değilse COM portunu metin kutusundan ayarla
        if(not self.is_connected):
            port = self.COMlineEdit.text()
            if (self.ard.connect(port)):    #port etiket mesajını ayarla
                self.COMConnectLabel.setText("..................... Bağlandı : " + port + " ......................")
            else:
                self.COMConnectLabel.setText(".................... bağlanamadı : " + port + " .....................")

    def update_angles(self):  #metin kutularındaki değişkenleri güncelle
        try:
            self.InvertTilt = self.InvertTilt_checkbox.isChecked()
            self.InvertPan = self.InvertPan_checkbox.isChecked()
            self.TiltSensivity = float(self.TiltSensivityEdit.text())
            self.PanSensivity = float(self.PanSensivityEdit.text())
            self.LED_ON = self.LED_checkbox.isChecked()

            self.cap.release()    #kamera kimliğini güncellemek için kameranın serbest bırakılması gerekir (değiştirilirse)
            self.CameraID = int(self.CameraIDEdit.text())
            self.cap = cv2.VideoCapture(self.CameraID)

            if(self.InvertPan):
                self.max_pan = int(self.MinPanlineEdit.text())
                self.min_pan = int(self.MaxPanlineEdit.text())
            else:
                self.min_pan = int(self.MinPanlineEdit.text())
                self.max_pan = int(self.MaxPanlineEdit.text())

            if(self.InvertTilt):
                self.max_tilt = int(self.MinTiltlineEdit.text())
                self.min_tilt = int(self.MaxTiltlineEdit.text())
            else:
                self.min_tilt = int(self.MinTiltlineEdit.text())
                self.max_tilt = int(self.MaxTiltlineEdit.text())

            self.save_init_file()
            print("değerler güncellendi")
        except:
            print("değerler güncellenemedi")

    def mouseMoveEvent(self, event):

        #farenin konumu pencereden izlenir ve kaydırma ve eğme miktarına dönüştürülür
        #örneğin fare tamamen sol-> pan_target = 0 ise (veya minimum pan_target değeri ne olursa olsun)
        # tamamen sağa doğru ise-> pan_target = 180 (veya maksimum pan_target değeri ne olursa olsun)
        #eğim için aynı prensip

        if(self.manual_mode): #manuel mod seçildiyse
            if(35<event.y()<470 and 70<event.x()<910):
                if(self.InvertTilt):  #eğer ters eğme seçili değerler ters yönde eşlenecekse
                    self.target_tilt = opr.remap(event.y(), self.max_tilt, self.min_tilt, 470, 35)
                    #((470,35, farenin yalnızca resmin üzerinde izlenmesini sağlar.)
                else:
                    self.target_tilt =  opr.remap(event.y(), self.min_tilt, self.max_tilt, 35, 470)

                if (self.InvertPan):
                    self.target_pan = opr.remap(event.x(), self.max_pan, self.min_pan, 910, 70)  # event.x()
                else:
                    self.target_pan = opr.remap(event.x(), self.min_pan, self.max_pan, 70, 910)  # event.x()

    def update_LCD_display(self):

        #arduino tarafından gönderilen servo açısı değerlerini güncelle
        ##aslında arduino gerçek dünyadaki konumunu değil, hedef değerini döndürdüğü için oldukça işe yaramaz
        self.Pan_LCD.display(self.current_pan)
        self.Tilt_LCD.display(self.current_tilt)

    def quit(self):
        print('Quit')
        self.rec = False
        sys.exit()

    def closeEvent(self, event):
        self.quit()# çapraz basıldığında çağrı bırakma yöntemi

    def set_manual_mode(self):
        self.manual_mode = self.Manual_checkbox.isChecked()
        if(not self.manual_mode):          #manuel modda değilse
            self.random_servos_position()  #rastgele bir kaydırma ve eğme hedefi seç
        print(self.manual_mode)

    def random_servos_position(self):
        self.target_tilt = random.uniform(self.min_tilt, self.max_tilt)
        self.target_pan = random.uniform(self.min_pan, self.max_pan)


    def toggle_recording(self):
        if(self.rec):
            self.rec = False                   #Kaydetmeyi bırak
            self.PauseButton.setText("Devam et") #duraklatma düğmesi metnini değiştir
        else:
            self.rec = True
            self.PauseButton.setText("Durdur")
            self.record()


    def record(self):  #video kaydı

        while(self.rec):
            ret, img = self.cap.read() #görüntü yakala

            if(self.is_connected):            #arduino bağlıysa
                if(self.manual_mode):         #ve manuel mod açık
                    processed_img = img       #resmi işleme
                else:
                    processed_img = self.image_process(img) #görüntü işleme (yüzleri kontrol et ve daire ve çarpı çiz)
            else:                             #arduino bağlı değilse
                processed_img = img           #resmi işleme

            self.update_GUI(processed_img)    #pencerede resmi güncelle
            cv2.waitKey(0)                    #çerçeveler arasında gecikme yok


            self.move_servos() #servoları hareket ettir

            if (not self.rec):     #duraklatma düğmesine basıldığında loopun durmasına izin verir
                break

    def update_GUI(self, openCV_img): # OpenCV resmini dönüştürme ve pyQt etiketini güncelleme

        try: #Bu işe yaramazsa kamera kimliğini kontrol et
            openCV_img = cv2.resize(openCV_img, (960, 540))  #bu görüntüyü biraz uzatıyor ancak yapılmazsa kullanıcı arayüzüne uymuyor
            height, width, channel = openCV_img.shape
            bytesPerLine = 3 * width
            qImg = QImage(openCV_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

            pixmap = QPixmap(qImg)
            self.label.setPixmap(pixmap)

        except:
            self.label.setText("ID yi kontrol et")

        self.show()

    def move_servos(self):
        if (self.is_connected):

            if self.LED_ON and not self.manual_mode:
                if not self.face_detected: #led modunu ayarla (0: kırmızı, 1: sarı 2: yeşil)
                    led_mode = 0
                else:
                    if self.target_locked:
                        led_mode = 1
                    else :
                        led_mode = 2

            elif self.LED_ON and self.manual_mode:
                led_mode = 3 #bütün ledleri aç
            else:
                led_mode = 4 #turn led's off

            data_to_send = "<" + str(int(self.target_pan)) + "," + str(int(self.target_tilt)) + "," + str(led_mode) + ">"
            self.ard.runTest(data_to_send)
            #arduino'ya gönderilen veriler şöyle görünecektir (<154, 23, 0>)
            #arduino "<" başlangıç karakterini arayacaktır.
            #sonra ">" bitiş karakterini bulana kadar aşağıdaki her şeyi kaydedin
            #o noktada arduino şöyle bir mesaj kaydetmiş olacak "154, 23, 0"
            #daha sonra her komada mesajı böler ve servoları hareket ettirmek için veri parçalarını kullanır

        
        


    def roam(self):
        if(self.roam_pause_count < 0 ):      #dolaşım sayısı 0'dan düşükse

            self.roam_pause_count = self.roam_pause                                        #dolaşım sayısını sıfırla
            self.roam_target_pan = int(random.uniform(self.min_pan, self.max_pan))
            self.roam_target_tilt = int(random.uniform(self.min_tilt, self.max_tilt))

        else:        #dolaşım sayısı> 1 ise
                     #kaydırma hedefini dolaşım hedefine doğru artır
            if (int(self.target_pan) > self.roam_target_pan):
                self.target_pan -= 1
            elif (int(self.target_pan) < self.roam_target_pan):
                self.target_pan += 1
            else:    #dolaşım hedefine ulaşıldıysa dolaşım duraklama sayısını azalt
                self.roam_pause_count -= 1

            if (int(self.target_tilt) > self.roam_target_tilt):
                self.target_tilt -= 1
            elif (int(self.target_tilt) < self.roam_target_tilt):
                self.target_tilt += 1
            else:
                self.roam_pause_count -= 1


    def image_process(self, img):  #görüntü işlemeyi yönetme
        #daha sonra eklemek için: kare atlama özelliğini kullan (her n karede yalnızca 1'i işaretle)

        processed_img = opr.find_face(img, self.max_target_distance)  # yüz bulmaya ve işlenmiş görüntüyü döndürmeye çalış
        # işlem sırasında yüz bulunursa, veri dönüşü aşağıdaki gibi olacaktır:
        #[True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]
        #değilse, sadece Yanlış döndürür

        if(processed_img[0]):             #yüz bulunmassa
            self.face_detected = True
            self.empty_frame_number = self.max_empty_frame  #boş çerçeve sayısını sıfırla
            self.target_locked = processed_img[4]
            self.calculate_camera_move(processed_img[2], processed_img[3])  # yüz ve görüntü merkezi arasındaki mesafeye bağlı olarak yeni hedefler hesapla
            return processed_img[1]
        else:
            self.face_detected = False
            self.target_locked = False
            if(self.empty_frame_number> 0):
                self.empty_frame_number -= 1  #0'a eşit olana kadar kare sayısını azalt
            else:
                self.roam()              #then roam
            return img


    def calculate_camera_move(self, distance_X, distance_Y):

        #self.target_pan += distance_X * self.PanSensivity

        if(self.InvertPan): 
            self.target_pan += distance_X * self.PanSensivity
            if(self.target_pan>self.min_pan):
                self.target_pan = self.min_pan
            elif (self.target_pan < self.max_pan):
                self.target_pan = self.max_pan

        else:
            self.target_pan -= distance_X * self.PanSensivity
            if(self.target_pan>self.max_pan):
                self.target_pan = self.max_pan
            elif (self.target_pan < self.min_pan):
                self.target_pan = self.min_pan


        #self.target_tilt += distance_Y * self.TiltSensivity

        if(self.InvertTilt): 
            self.target_tilt -= distance_Y * self.TiltSensivity
            if(self.target_tilt>self.min_tilt):
                self.target_tilt = self.min_tilt
            elif (self.target_tilt < self.max_tilt):
                self.target_tilt = self.max_tilt
        else:
            self.target_tilt += distance_Y * self.TiltSensivity
            if(self.target_tilt>self.max_tilt):
                self.target_tilt = self.max_tilt
            elif (self.target_tilt < self.min_tilt):
                self.target_tilt = self.min_tilt

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()
    #sys.exit(app.exec_())
