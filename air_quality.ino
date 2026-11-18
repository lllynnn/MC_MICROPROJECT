const int sensorPin = A0;
const int buzzerPin = 8;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
}

void loop() {
  int sensorValue = analogRead(sensorPin);

  const char* status;

  if (sensorValue <= 160) {
    status = "GOOD";
    digitalWrite(buzzerPin, LOW);
  }
  else if (sensorValue <= 300) {
    status = "MODERATE";
    digitalWrite(buzzerPin, LOW);
  }
  else {
    status = "POOR";
    digitalWrite(buzzerPin, HIGH);
  }

  Serial.print("VALUE:");
  Serial.print(sensorValue);
  Serial.print(",STATUS:");
  Serial.println(status);

  delay(500);
}
