import socket
import json
import threading

class SocketCommands:
    def __init__(self):
        self.socket = self.find_port()
        self.messenger = self.Messenger(self)
        self.receiver = self.Receiver(self)

    def find_port(self):
        with open("socket.txt", "r") as file:
            return int(file.read())

    class Messenger:
        def __init__(self, parent):
            self.parent = parent

        def send_message(self, message):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode(), ("<broadcast>", self.parent.socket))
            sock.close()

        def send_image(self, name, image):
            data = {
                "Sender": name,
                "Target": "ScreenControl",
                "Type": "Image",
                "Image": image
            }
            self.send_message(json.dumps(data))

        def processes(self, name, processes):
            data = {
                "Sender": name,
                "Target": "ScreenControl",
                "Type": "Processes",
                "Processes": processes
            }
            self.send_message(json.dumps(data))

    class Receiver:
        def __init__(self, parent):
            self.parent = parent

        def udp_listener(self, port, freeze, images, processes):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", port))

            print("Listening for UDP broadcasts on port", port)

            while True:
                data, addr = sock.recvfrom(1024)
                try:
                    message = json.loads(data.decode())
                except:
                    print("Invalid JSON:", data)
                    continue

                if message.get("Sender") == "ScreenFreezer":
                    target = message.get("Target")
                    command = message.get("Command")

                    if target == "ALL":
                        if command == "Freeze":
                            freeze()
                        elif command == "Images":
                            images()
                        elif command == "Processes":
                            processes()

        def thread(self, freeze, images, processes):
            listener_thread = threading.Thread(
                target=self.udp_listener,
                args=(self.parent.socket, freeze, images, processes),
                daemon=True
            )
            listener_thread.start()
