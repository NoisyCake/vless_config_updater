import socket


def get_free_port() -> int:
    '''
    Gets the port that is free at the time of the function call.
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]