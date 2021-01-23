import socket

from app import utils


def main():
    reuse_port:bool = not utils.is_windows()
    s = socket.create_server(("localhost", 6379), reuse_port=reuse_port)

    s.accept()  # wait for client


if __name__ == "__main__":
    main()
