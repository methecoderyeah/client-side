import socket_commands

commander = socket_commands.SocketCommands()

commander.receiver.thread(
    freeze=lambda: print("FREEZE"),
    images=lambda: print("IMAGES"),
    processes=lambda: print("PROCESSES")
)
