from hashlib import md5

def hash_password(email, password):
    return md5("%s:%s" % (email, password)).hexdigest()

def check_password(email, password, hashed_password):
    if hash_password(email, password) != hashed_password:
        return False
    return True
