#include <IRremote.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

#define LED_GREEN      2
#define LED_YELLOW     3
#define LED_RED        4
#define BUZZER         5
#define trigPin        6
#define echoPin        7
#define I0             8
#define I1             9
#define I2             10
#define I3             11
#define IR_RECIEVE_PIN 12
#define SERVO_PIN      A0

int last_cm;
bool is_movineg = false;
bool is_forward = false;
Servo myservo;
int counter = 0;
String inputString = "";
bool stringComplete = false, is_beeping = false;
int num_of_yellows = 0, num_of_reds = 0;
long duration, cm;
LiquidCrystal_I2C lcd(0x27, 16, 2);

void calc_dist();
long microsecondsToCentimeters(long microseconds);
void leds_off();
void look_right();
void look_left();
void look_front();
void stop();
void forward();
void backward();
void right();
void left();
void BEEP();
void stop_alert();
void green();
void yellow();
void send_data();
void update_lcd();

ISR(TIMER0_COMPA_vect) {
  if (counter >= 49) {
    counter = 0;
    calc_dist();
  }
  counter++;
}

void setup() {
  cli();

  TCCR0A = 0;
  TCCR0B = 0;
  TCNT0  = 0;
  OCR0A = 156;  
  TCCR0A |= (1 << WGM01);
  TCCR0B |= (1 << CS02) | (1 << CS00);
  TIMSK0 |= (1 << OCIE0A);
  sei();

  inputString.reserve(2000);
  Serial.begin(9600);

  IrReceiver.begin(IR_RECIEVE_PIN, ENABLE_LED_FEEDBACK);

  DDRD |= (1 << PD2) | (1 << PD3) | (1 << PD4) | (1 << PD5) | (1 << PD6);
  DDRD &= ~(1 << PD7);

  DDRB |= (1 << PB0) | (1 << PB1) | (1 << PB2) | (1 << PB3);
  DDRB &= ~(1 << PB4);

  DDRC |= (1 << PC0);

  myservo.attach(SERVO_PIN);
  myservo.write(80);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
}

void loop() {
  if (IrReceiver.decode() || stringComplete) {
    long KEY_Press = IrReceiver.decodedIRData.decodedRawData;
    static long last_key;

    if (stringComplete) {}

    if (KEY_Press == 0xBF40FF00 || inputString == "f\n") {
      forward();
    }
    else if (KEY_Press == 0xB54AFF00 || inputString == "r\n") {
      look_right();
    }
    else if (KEY_Press == 0xAD52FF00 || inputString == "c\n") {
      look_front();
    }
    else if (KEY_Press == 0xBD42FF00 || inputString == "l\n") {
      look_left();
    }
    else if (KEY_Press == 0xEA15FF00 || inputString == "s\n") {
      stop();
    }
    else if (KEY_Press == 0xE619FF00 || inputString == "b\n") {
      backward();
    }
    else if (KEY_Press == 0xF807FF00 || inputString == "x\n") {
      left();
    }
    else if (KEY_Press == 0xF609FF00 || inputString == "y\n") {
      right();
    }
    else if ((KEY_Press == 0xBA45FF00 && last_key != 0xBA45FF00) || inputString == "beep\n") {
      BEEP();
    }
    else if (KEY_Press == 0xB847FF00 || inputString == "data\n") {
      send_data();
    }

    stringComplete = false;
    inputString = "";
    last_key = KEY_Press;
  }

  IrReceiver.resume();
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void calc_dist() {
  PORTD &= ~(1 << PD6);
  delayMicroseconds(2);
  PORTD |= (1 << PD6);
  delayMicroseconds(5);
  PORTD &= ~(1 << PD6);

  duration = pulseIn(echoPin, HIGH);
  cm = microsecondsToCentimeters(duration);

  if (cm < 30) {
    stop_alert();
  }
  else if (cm < 60 && is_forward) {
    yellow();
  }
  else if (is_forward) {
    green();
  }
  else {
    leds_off();
  }

  last_cm = cm;
}

long microsecondsToCentimeters(long microseconds) {
  return microseconds / 29 / 2;
}

void leds_off() {
  PORTD &= ~(1 << PD2);
  PORTD &= ~(1 << PD4);
  PORTD &= ~(1 << PD3);
  PORTD &= ~(1 << PD5);

  if (is_beeping) {
    PORTD |= (1 << PD5);
    PORTD |= (1 << PD3);
  }
  else {
    PORTD &= ~(1 << PD5);
    PORTD &= ~(1 << PD3);
  }
}

void look_right() {
  myservo.write(40);
}

void look_left() {
  myservo.write(120);
}

void look_front() {
  myservo.write(80);
}

void stop() {
  is_forward = false;
  PORTB &= ~(1 << PB0);
  PORTB &= ~(1 << PB1);
  PORTB &= ~(1 << PB2);
  PORTB &= ~(1 << PB3);
}

void forward() {
  is_forward = true;
  PORTB |=  (1 << PB0);
  PORTB &= ~(1 << PB1);
  PORTB |=  (1 << PB2);
  PORTB &= ~(1 << PB3);
}

void backward() {
  is_forward = false;
  PORTB &= ~(1 << PB0);
  PORTB |=  (1 << PB1);
  PORTB &= ~(1 << PB2);
  PORTB |=  (1 << PB3);
}

void right() {
  is_forward = false;
  PORTB |=  (1 << PB0);
  PORTB &= ~(1 << PB1);
  PORTB &= ~(1 << PB2);
  PORTB &= ~(1 << PB3);
}

void left() {
  is_forward = false;
  PORTB &= ~(1 << PB0);
  PORTB &= ~(1 << PB1);
  PORTB |=  (1 << PB2);
  PORTB &= ~(1 << PB3);
}

void BEEP() {
  is_beeping = !is_beeping;
  if (is_beeping) {
    num_of_yellows++;
  }
}

void stop_alert() {
  PORTD |=  (1 << PD4);
  PORTD &= ~(1 << PD5);
  PORTD &= ~(1 << PD2);
  PORTD &= ~(1 << PD3);

  stop();

  if (last_cm > 30 && cm < 30) {
    num_of_reds++;
  }
}

void green() {
  PORTD |=  (1 << PD2);
  PORTD &= ~(1 << PD4);
  PORTD &= ~(1 << PD3);
  PORTD &= ~(1 << PD5);

  if (is_beeping) {
    PORTD |=  (1 << PD5);
    PORTD |=  (1 << PD3);
  }
  else {
    PORTD &= ~(1 << PD5);
    PORTD &= ~(1 << PD3);
  }
}

void yellow() {
  PORTD |=  (1 << PD3);
  PORTD &= ~(1 << PD4);
  PORTD |=  (1 << PD5);
  PORTD &= ~(1 << PD2);

  if (last_cm > 60 && cm < 60) {
    num_of_yellows++;
  }
}

void send_data() {
  Serial.println(cm);
  Serial.println(num_of_yellows);
  Serial.println(num_of_reds);
  update_lcd();
}

void update_lcd() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Dist: ");
  lcd.print(cm);
  lcd.print(" cm");

  lcd.setCursor(0, 1);
  lcd.print("Y: ");
  lcd.print(num_of_yellows);
  lcd.print(" R: ");
  lcd.print(num_of_reds);
}
