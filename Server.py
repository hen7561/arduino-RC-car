import socket
import threading
import serial
import time

try:
    ser = serial.Serial('COM8', 9600)
    time.sleep(2)
    print("Arduino connected on COM8")
except Exception as e:
    print("Could not connect to Arduino:", e)
    ser = None

def get_ipv4_address():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        print("Error retrieving IPv4 address:", e)
        return None

def connect_server(port=110):
    host_ip = get_ipv4_address()
    if not host_ip:
        host_ip = "127.0.0.1"

    print("Server IP Address (give this to the client):", host_ip)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, port))
    server_socket.listen()
    print(f"Server is listening on port {port}...")

    client_socket, address = server_socket.accept()
    print("Connected with {}".format(str(address)))
    return client_socket

def receive_commands_from_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Client disconnected.")
                break

            message = data.decode('utf-8').strip()
            print("[Client -> Server] Received command:", message)

            if ser:
                cmd_to_arduino = message + "\n"
                ser.write(cmd_to_arduino.encode('utf-8'))
                print(f"[Server -> Arduino] Sent: {cmd_to_arduino.strip()}")

        except Exception as e:
            print("Error receiving commands from client:", e)
            break

def read_from_arduino_and_send_to_client(client_socket):
    while True:
        try:
            if ser and ser.in_waiting > 0:
                data_line = ser.readline().decode('utf-8', errors='ignore').strip()
                if data_line:
                    print("[Arduino -> Server -> Client] Forwarding data:", data_line)
                    data_line_with_newline = data_line + "\n"
                    client_socket.send(data_line_with_newline.encode('utf-8'))
        except Exception as e:
            print("Error reading from Arduino:", e)
            break


client = connect_server(port=110)

thread_receive = threading.Thread(
    target=receive_commands_from_client, args=(client,), daemon=True
)
thread_arduino = threading.Thread(
    target=read_from_arduino_and_send_to_client, args=(client,), daemon=True
)

thread_receive.start()
thread_arduino.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    if ser and ser.is_open:
        ser.close()
    client.close()



