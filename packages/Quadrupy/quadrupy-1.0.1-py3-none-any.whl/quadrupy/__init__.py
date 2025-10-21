from .core import STQV1

_dog = None

def _get_dog():
    global _dog
    if _dog is None:
        _dog = STQV1()
    return _dog

def walk():
    _get_dog().walk()

def writeScreen(text):
    _get_dog().writeScreen(text)

def writeMotor(val):
    _get_dog().writeMotor(val)

def reset():
    _get_dog().reset()

def led(state):
    _get_dog().led(state)

def clearScreen():
    _get_dog().clearScreen()

def send(cmd: str):
    _get_dog().send(cmd)

def close():
    global _dog
    if _dog is not None:
        _dog.close()
        _dog = None

