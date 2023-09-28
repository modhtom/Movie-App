import os


def check_password_length(password):
    if len(password) < 8:
        return False
    return True


def check_password_characters(password):
    uppercaseFound = False
    lowercaseFound = False
    digitFound = False
    characterFound = False

    for letter in str(password):
        if letter.isupper() and (not uppercaseFound):
            uppercaseFound = True
        elif letter.islower() and (not lowercaseFound):
            lowercaseFound = True
        elif letter.isdigit() and (not digitFound):
            digitFound = True
        elif (
            letter == "@"
            or letter == "!"
            or letter == "#"
            or letter == "$"
            or letter == "%"
            or letter == "&"
            and (not characterFound)
        ):
            characterFound = True

    if uppercaseFound and lowercaseFound and digitFound and characterFound:
        return True
    return False


def checkEmail(email):
    dot_check = False
    at_check = False
    for letter in email:
        if letter == ".":
            dot_check = True
        elif letter == "@":
            at_check = True

    if dot_check and at_check:
        return True
    else:
        return False


ALLOWED_EXTENSIONS_IMAGE = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE_BYTES_IMAGE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS_VIDEO = {"mp4", "mkv", "mpeg"}
MAX_FILE_SIZE_BYTES_VIDEO = 500 * 1024 * 1024


def allowed_fileImage(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE
    )


def allowed_fileVideo(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS_VIDEO
    )


def allowed_file_sizeImage(file):
    original_position = file.tell()
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(original_position)
    return file_size <= MAX_FILE_SIZE_BYTES_IMAGE


def allowed_file_sizeVideo(file):
    original_position = file.tell()
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(original_position)
    return file_size <= MAX_FILE_SIZE_BYTES_VIDEO
