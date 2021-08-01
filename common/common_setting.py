from datetime import datetime


def hyphen_now():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
