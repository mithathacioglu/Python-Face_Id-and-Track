import serial

class ard_connect():
    def __init__(self, parent):
        self.parent = parent
        self.startMarker = 60 #utf-8 for '<'
        self.endMarker = 62   #utf-8 for '>'
        #self.ser = serial.Serial('COM3', 9600)
        print("ard baglandi")


    def connect(self, port):
        try:
            self.ser = serial.Serial(port, 128000)
            self.waitForArduino()
            self.parent.is_connected = True
            return True
        except:
            print("bu porta baglanamaz")
            return False

    def waitForArduino(self):

        msg = ""
        while msg.find("bak bu oldu") == -1:  #string.find() dön -1 eğer değer bulunamazsa

            while self.ser.inWaiting() == 0:  #inWaiting() arabellekteki bayt sayısını döndür, equivalent of Serial.available arduino da 
                pass

            msg = self.recvFromArduino()   #kodu çözülmüş seri verileri döndür
            print(msg)  # python3 parantez gerektirir
            #print()

    def recvFromArduino(self):

        message_received = "" # mesaj boş bir dize olarak başladı
        x = "z"  #sonraki karakter diziden okundu. bitiş veya startMarker olmayan herhangi bir değer olarak başlatılması gerekir
        byteCount = -1  #son artışın çok fazla olacağı gerçeğine izin vermek

        # başlangıç karakterini bekle
        while ord(x) != self.startMarker:  # ord() return utf-8 için char(1 uzunluk dizesi)  örnek:karakter için 60 döndür <
            x = self.ser.read()  # başlangıç işareti bulunana kadar döngü

        # bitiş işareti bulunana kadar verileri kaydet
        while ord(x) != self.endMarker:  # lbitiş işareti bulunana kadar döngü
            if ord(x) != self.startMarker:  # if not start marker
                message_received = message_received + x.decode("utf-8")  # dize koduna çözülmüş karakter ekle
                byteCount += 1  # BYTECOUNT niçin,unuttum :D
            x = self.ser.read()  # bir sonrakini oku

        return (message_received)

    def sendToArduino(self, sendStr):
        #print("sent to arduino func : ", sendStr)
        self.ser.write(sendStr.encode('utf-8'))  #Python3 için değiştir
        #self.ser.write(sendStr)  #yalnızca int ile ilgileniyormuş gibi verileri gönder

    def runTest(self, message_to_send):

        waitingForReply = False

        if waitingForReply == False:
            self.sendToArduino(message_to_send)  # seriye mesaj yaz
            waitingForReply = True

        if waitingForReply == True:    #arduino'dan veri bekle
            while self.ser.inWaiting() == 0:   # eşdeğer Serial.available arduino da
                pass  # veriler mevcut olana kadar döngü

            dataRecvd = self.recvFromArduino() # int verisini böl


            split_data = dataRecvd.split(",")
            #self.parent.update_LCD_display(split_data[0], split_data[1])
            try:
                self.parent.current_pan = split_data[0]
                self.parent.current_tilt = split_data[1]
                self.parent.update_LCD_display()
            except:
                print("error split data : ", len(split_data))

            #print("Reply Received  " + dataRecvd)

            waitingForReply = False

            #print("===========")
