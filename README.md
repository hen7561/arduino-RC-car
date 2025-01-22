# Arduino RC Car Project

This repository contains the implementation of an Arduino-based RC car system, including client-server communication, servo motor control, ultrasonic distance sensing, and data visualization. Below is an overview of the structure and functionality of the codebase.

---

## Code Breakdown

### 1. Python Client Code (`client.py`)

#### **Functionality:**
- Connects to a server via TCP.
- Provides a GUI for controlling the car's movement and sensors.
- Receives telemetry data from the server and logs it to an Excel file.
- Includes a threaded architecture for seamless server communication.

#### **Dependencies:**
- `socket` - For TCP communication.
- `tkinter` - For GUI.
- `threading` - For handling background processes.
- `openpyxl` - For Excel file creation and logging.
- `datetime` - For timestamping.

#### **Key Features:**
- GUI buttons for movement (`Forward`, `Backward`, `Stop`, `Left`, `Right`) and sensor controls (`Look Left`, `Look Right`, `Beep`, etc.).
- Real-time telemetry updates displayed in the GUI.
- Automated data logging in `data_log.xlsx`.

```python
# Example of sending a command to the server
def send_command(cmd):
    print(f"Sending command: {cmd}")
    client_socket.sendall(cmd.encode('utf-8'))
```
---

### 2. Python Server Code (`server.py`)

#### **Functionality:**
- Hosts a TCP server for receiving commands from the client.
- Interfaces with the Arduino through a serial connection.
- Forwards commands from the client to the Arduino and sends back telemetry data.

#### **Dependencies:**
- `socket` - For TCP communication.
- `threading` - For handling background processes.
- `serial` - For Arduino communication.
- `time` - For delays and time management.

#### **Key Features:**
- Multi-threaded handling of client commands and Arduino data.
- Bi-directional communication between client and Arduino.
- Automatic recovery from client disconnection.

```python
# Example of forwarding data from Arduino to the client
def read_from_arduino_and_send_to_client(client_socket):
    data_line = ser.readline().decode('utf-8', errors='ignore').strip()
    client_socket.send(data_line.encode('utf-8'))
```
---

### 3. Arduino Code (`arduino.ino`)

#### **Functionality:**
- Reads infrared (IR) remote signals and serial commands.
- Controls LEDs, servo motors, and a buzzer based on commands.
- Implements ultrasonic distance sensing with real-time obstacle detection.

#### **Libraries Used:**
- `IRremote` - For IR signal decoding.
- `Servo` - For servo motor control.
- `LiquidCrystal_I2C` - For displaying data on an LCD.

#### **Key Features:**
- Obstacle detection using an ultrasonic sensor.
- Visual and auditory alerts based on proximity (`Green`, `Yellow`, `Red` zones).
- LCD display updates with distance and alert counts.
- Support for remote and serial-based commands.

```cpp
// Example of obstacle detection
void calc_dist() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(trigPin, LOW);

    duration = pulseIn(echoPin, HIGH);
    cm = duration / 29 / 2;

    if (cm < 30) {
        stop_alert();
    }
}
```
---

## Setup Instructions

### Hardware
1. **Arduino**: Connect sensors (ultrasonic, IR receiver) and actuators (servo motor, LEDs, buzzer) as specified in the Arduino code.
2. **PC**: Run the server code on a machine connected to the Arduino via USB.
3. **Network**: Ensure the client machine can reach the server over the specified IP and port.

### Software
1. Install the necessary Python dependencies:
    ```bash
    pip install tkinter openpyxl pyserial
    ```
2. Upload the Arduino sketch to the Arduino board using the Arduino IDE.
3. Run the server script:
    ```bash
    python server.py
    ```
4. Run the client script:
    ```bash
    python client.py
    ```

---

## Features and Usage

### Movement Controls
| Button       | Command | Description              |
|--------------|---------|--------------------------|
| Move Forward | `f`     | Moves the car forward.   |
| Backward     | `b`     | Moves the car backward.  |
| Stop         | `s`     | Stops the car.           |
| Left         | `x`     | Turns the car left.      |
| Right        | `y`     | Turns the car right.     |

### Sensor and Alert Controls
| Button       | Command  | Description                               |
|--------------|----------|-------------------------------------------|
| Look Left    | `l`      | Rotates the servo to the left.            |
| Look Right   | `r`      | Rotates the servo to the right.           |
| Look Front   | `c`      | Resets the servo to the front position.   |
| Beep         | `beep`   | Toggles the buzzer state.                 |
| Send Data    | `data`   | Sends distance and alert data to the GUI. |

---

## Pin Configuration

| Arduino Pin | AVR Port.Bit | Usage in Code       |
|-------------|--------------|---------------------|
| 2           | PD2          | LED_GREEN           |
| 3           | PD3          | LED_YELLOW          |
| 4           | PD4          | LED_RED             |
| 5           | PD5          | BUZZER              |
| 6           | PD6          | trigPin (Ultrasonic)|
| 7           | PD7          | echoPin (Ultrasonic)|
| 8           | PB0          | I0 (Motor)          |
| 9           | PB1          | I1 (Motor)          |
| 10          | PB2          | I2 (Motor)          |
| 11          | PB3          | I3 (Motor)          |
| 12          | PB4          | IR_RECIEVE_PIN      |
| A0 (14)     | PC0          | SERVO_PIN           |

---
## Future Enhancements
- Add WiFi-based communication.
- Include additional sensors for environment mapping.
- Implement advanced obstacle avoidance algorithms.
