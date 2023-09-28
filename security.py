import bcrypt
from flask import session


def hashPassword(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()


def checkPassMatch(stored_hashpassword, password):
    if stored_hashpassword:
        if bcrypt.checkpw(password.encode(), stored_hashpassword[0].encode()):
            return True
    return False


SECRET_KEY = "T&v$2PQsLx!9j8Rk@5gFw#ZmDp1YhCn*4uXy7eBdAa6VbGz3JqU"
