




import socket
import tkinter as tk
from threading import Thread
from openpyxl import Workbook
from datetime import datetime
import time

# Adjust these to match your server settings:
SERVER_IP = "172.20.10.4"  # Change to the server machine's IP
SERVER_PORT = 110

# ---------- NETWORKING ----------
def connect_to_server(server_ip, server_port):
    """
    Connects to the TCP server and returns the socket.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print("Connected to Server:", server_ip, server_port)
    return client_socket

# ---------- EXCEL SETUP ----------
wb = Workbook()
ws = wb.active
ws.append(["Timestamp", "Distance", "Warnings", "Stops"])  # header row

# Variables to hold the latest telemetry from the server
dist = 0
yellows = 0
reds = 0

# ---------- TKINTER SETUP ----------
window = tk.Tk()
window.title("Arduino Robot GUI (Client)")

# Label to show telemetry
data_text = tk.Label(
    text=f"Distance:{dist} Warnings:{yellows} Stops:{reds}",
    foreground="black",
    background="purple",
    width=40,
    height=1,
    font=("Courier", 16)
)
data_text.grid(row=6, columnspan=3, padx=4, pady=2)

# ---------- RECEIVE DATA FROM SERVER ----------
def handle_server_data():
    """
    Listens for data from the server socket, parses it, and updates the GUI.
    """
    global dist, yellows, reds
    partial_buffer = []

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Server disconnected.")
                break

            lines = data.decode('utf-8', errors='ignore').split('\n')
            for line in lines:
                # Because we might get partial data in the buffer, we check if line has content
                line = line.strip()
                if not line:
                    continue

                print(f"[Server -> Client] Received data: {line}")
                partial_buffer.append(line)

                # We assume every 3 lines is a set: dist, yellows, reds
                if len(partial_buffer) == 3:
                    dist = partial_buffer[0]
                    yellows = partial_buffer[1]
                    reds = partial_buffer[2]
                    # Update the label
                    data_text.config(
                        text=f"Distance: {dist}  Warnings: {yellows}  Stops: {reds}"
                    )
                    # Log to Excel
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ws.append([timestamp, dist, yellows, reds])
                    wb.save("data_log.xlsx")

                    partial_buffer.clear()

        except Exception as e:
            print("Error reading from server:", e)
            break

# Create a daemon thread to read data continuously
def start_data_thread():
    t = Thread(target=handle_server_data, daemon=True)
    t.start()

# ---------- SEND COMMANDS TO SERVER ----------
def send_command(cmd):
    """
    Sends a command string to the server (which writes it to Arduino).
    """
    try:
        print(f"Sending command: {cmd}")
        client_socket.sendall(cmd.encode('utf-8'))
    except Exception as e:
        print("Error sending command:", e)

# ---------- BUTTON COMMANDS ----------
def forward_click():
    send_command("f")

def left_click():
    send_command("x")

def right_click():
    send_command("y")

def stop_click():
    send_command("s")

def back_click():
    send_command("b")

def look_front_click():
    send_command("c")

def look_left_click():
    send_command("l")

def look_right_click():
    send_command("r")

def beep_click():
    send_command("beep")

def data_click():
    send_command("data")

def finish_click():
    client_socket.close()
    window.quit()

# ---------- BUILD THE GUI ----------
greeting = tk.Label(
    text="Servo Motor Arduino GUI (Client)",
    foreground="black",
    background="purple",
    width=40,
    height=1,
    font=("Courier", 16)
)
greeting.grid(row=0, columnspan=3, padx=4, pady=2)

button_forward = tk.Button(
    text="Move Forward", width=25, height=3, bg="blue", fg="yellow",
    command=forward_click
)
button_left = tk.Button(
    text="Left", width=25, height=3, bg="blue", fg="yellow",
    command=left_click
)
button_stop = tk.Button(
    text="STOP", width=25, height=3, bg="blue", fg="yellow",
    command=stop_click
)
button_right = tk.Button(
    text="Right", width=25, height=3, bg="blue", fg="yellow",
    command=right_click
)
button_back = tk.Button(
    text="Backwards", width=25, height=3, bg="blue", fg="yellow",
    command=back_click
)
button_beep = tk.Button(
    text="BEEP", width=25, height=3, bg="blue", fg="yellow",
    command=beep_click
)
button_data = tk.Button(
    text="Send Data", width=25, height=3, bg="blue", fg="yellow",
    command=data_click
)
button_look_left = tk.Button(
    text="Look Left", width=25, height=3, bg="blue", fg="yellow",
    command=look_left_click
)
button_look_front = tk.Button(
    text="Look Front", width=25, height=3, bg="blue", fg="yellow",
    command=look_front_click
)
button_look_right = tk.Button(
    text="Look Right", width=25, height=3, bg="blue", fg="yellow",
    command=look_right_click
)
button_finish = tk.Button(
    text="Finish", width=25, height=3, bg="blue", fg="yellow",
    command=finish_click
)

# Layout
button_forward.grid(row=1, column=1, padx=4, pady=2)
button_left.grid(row=2, column=0, padx=4, pady=2)
button_stop.grid(row=2, column=1, padx=4, pady=2)
button_right.grid(row=2, column=2, padx=4, pady=2)
button_back.grid(row=3, column=1, padx=4, pady=2)
button_beep.grid(row=4, column=1, padx=4, pady=2)
button_data.grid(row=5, column=1, padx=4, pady=2)
button_look_left.grid(row=7, column=0, padx=4, pady=2)
button_look_front.grid(row=7, column=1, padx=4, pady=2)
button_look_right.grid(row=7, column=2, padx=4, pady=2)
button_finish.grid(row=8, column=1, padx=4, pady=2)

# ---------- STARTUP ----------
if __name__ == "__main__":
    client_socket = connect_to_server(SERVER_IP, SERVER_PORT)
    start_data_thread()
    window.mainloop()
