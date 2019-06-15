const int xPin = 0;
const int yPin = 1;
const int zPin = 2;

int xValue;
int yValue;
int zValue;

void setup() {
  Serial.begin(9600);
}

void loop() {
  getAnalogValues();
  while (!Serial.available()) {}
  char c = Serial.read();
  Serial.println(xValue, DEC);
  
  while (!Serial.available()) {}
  c = Serial.read();
  Serial.println(yValue, DEC);
  
  while (!Serial.available()) {}
  c = Serial.read();
  Serial.println(zValue, DEC);
}

void getAnalogValues() {
  xValue = analogRead(xPin);
  yValue = analogRead(yPin);
  zValue = analogRead(zPin);
}
