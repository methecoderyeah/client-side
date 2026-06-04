import socket
import json
import threading

class SocketCommands:
    def __init__(self, user):
        self.user_ = user

        # Ask user for port only
        self.port = int(input("Enter main port number: "))

        self.reset_port = 2359

        self.messenger = self.Messenger(self)
        self.receiver = self.Receiver(self)

    class Messenger:
        def __init__(self, parent):
            self.parent = parent

        def send_message(self, message_dict, port=None):
            if port is None:
                port = self.parent.port

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", port))
                sock.sendall(json.dumps(message_dict).encode())
                sock.close()
            except:
                pass

        def send_image(self, name, image):
            data = {
                "Sender": name,
                "Target": "ScreenControl",
                "Type": "Image",
                "Image": image
            }
            self.send_message(data)

        def processes(self, name, processes):
            data = {
                "Sender": name,
                "Target": "ScreenControl",
                "Type": "Processes",
                "Processes": processes
            }
            self.send_message(data)

        def port_reset(self):
            data = {
                "Sender": "ScreenControl",
                "Target": "ALL",
                "Command": "Port Reset"
            }
            self.send_message(data, port=self.parent.reset_port)

    class Receiver:
        def __init__(self, parent):
            self.parent = parent

        def tcp_listener_main(self, port, freeze, images, processes):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("", port))
            server.listen(5)

            print(f"Listening for TCP commands on main port {port}")

            while True:
                conn, addr = server.accept()
                data = conn.recv(65536)

                try:
                    message = json.loads(data.decode())
                except:
                    print("Invalid JSON:", data)
                    conn.close()
                    continue

                if message.get("Sender") == "ScreenControl":
                    target = message.get("Target")
                    command = message.get("Command")

                    if target == "ALL" or target == self.parent.user_:
                        if command == "Freeze":
                            freeze()
                        elif command == "Images":
                            images()
                        elif command == "Processes":
                            processes()

                conn.close()

        def tcp_listener_reset(self, port, port_reset):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("", port))
            server.listen(5)

            print(f"Listening for TCP port resets on port {port}")

            while True:
                conn, addr = server.accept()
                data = conn.recv(65536)

                try:
                    message = json.loads(data.decode())
                except:
                    print("Invalid JSON:", data)
                    conn.close()
                    continue

                if (
                    message.get("Sender") == "ScreenControl"
                    and message.get("Command") == "Port Reset"
                ):
                    port_reset(message.get("Password"), message.get("Port"))

                conn.close()

        def thread(self, freeze, images, processes, port_reset):
            threading.Thread(
                target=self.tcp_listener_main,
                args=(self.parent.port, freeze, images, processes),
                daemon=True
            ).start()

            threading.Thread(
                target=self.tcp_listener_reset,
                args=(self.parent.reset_port, port_reset),
                daemon=True
            ).start()
