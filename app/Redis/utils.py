import os

def is_windows():
    return os.name == 'nt'

def get_command(data:bytes):
    NotImplemented("Need logic to dynamically fetch commnads.")