

#include <Servo.h>

Servo panServo;
Servo tiltServo; 

byte redledPin = 2;
byte yellowledPin = 3;
byte greenledPin = 4;

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

float panServoAngle = 90.0;
float tiltServoAngle = 90.0;
int LED_state = 0;

//8=============D

void setup() {
  Serial.begin(128000);
  
  panServo.attach(8);
  tiltServo.attach(9);

  pinMode(redledPin, OUTPUT);
  pinMode(yellowledPin, OUTPUT);
  pinMode(greenledPin, OUTPUT);
  
  //moveServo();
  start_sequence();

  delay(50);
  
  Serial.println("<bak bu oldu>"); // bilgisayara mesaj gönder
}

//8=============D

void loop() {
  getDataFromPC();
  replyToPC();
  moveServo();
  setLED();
}

//8=============D

void getDataFromPC() {

    // PC'den veri alma ve inputBuffer'a kaydetme
    
  if(Serial.available() > 0) {

    char x = Serial.read();              //char'ı diziden oku
      
    if (x == endMarker) {                //son işaretine bak
      readInProgress = false;            //bulunursa, devam eden okuma değerini true olarak ayarla (arabelleğe yeni bayt eklemeyi durduracaktır)
      newDataFromPC = true;              //arduino'ya yeni verilerin mevcut olduğunu bildirin
      inputBuffer[bytesRecvd] = 0;       //giriş arabelleğini temizle
      processData();                      // arabellekte veri işleme
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;      //girdi arabelleğini baytla doldur
      bytesRecvd ++;                    //artış endeksi
      if (bytesRecvd == buffSize) {     //arabellek dolduğunda
        bytesRecvd = buffSize - 1;      //son işaretleyici tut
      }
    }

    if (x == startMarker) {              // başlangıç işaretini ara
      bytesRecvd = 0;                    // if found, set byte received to 0
      readInProgress = true;             // okumaya devam et
    }
  }
}

//8=============D

void processData() // veri türü için "<float, float, int>" 
{
  char * strtokIndx; // bu strtok () tarafından dizin olarak kullanılır

   strtokIndx = strtok(inputBuffer,",");      // ilk kısmı al
   panServoAngle = atof(strtokIndx);         // bu parçayı float dönüştür

   strtokIndx = strtok(NULL,",");          // ikinci kısmı al (bu önceki çağrının kaldığı yerden devam eder)
   tiltServoAngle = atof(strtokIndx);     // bu parçayı floata dönüştür

   strtokIndx = strtok(NULL, ",");      // son kısmı al
   LED_state = atoi(strtokIndx);          // int e çevir (string to int)
}

//8=============D

void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    Serial.print("<");
    Serial.print(panServo.read());
    Serial.print(",");
    Serial.print(tiltServo.read());
    Serial.println(">");
  }
}

//8=============D

void moveServo() 
{
  panServo.write(panServoAngle);
  tiltServo.write(tiltServoAngle);
}

void setLED()
{
  if(LED_state == 2){
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, HIGH);
    digitalWrite(greenledPin, LOW);
    }
  else if(LED_state == 1){
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, HIGH);    
    }
  else if(LED_state == 0){
    digitalWrite(redledPin, HIGH);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);  
    }  
  else if(LED_state == 3){
    digitalWrite(redledPin, HIGH);
    digitalWrite(yellowledPin, HIGH);
    digitalWrite(greenledPin, HIGH);  
    }  
  else{
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);    
    }
  
  }

//8=============D

  void start_sequence()
  {
    panServo.write(90);
    tiltServo.write(90);
    delay(300);

  
    digitalWrite(redledPin, HIGH);
    delay(100);
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, HIGH);
    delay(100);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, HIGH);
    delay(100);
  
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);
    delay(100);
    digitalWrite(redledPin, HIGH);
    digitalWrite(yellowledPin, HIGH);
    digitalWrite(greenledPin, HIGH);
    delay(100);
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);
    }
