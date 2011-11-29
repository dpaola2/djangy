import sys
from hashlib import md5
from management_database import User

def hash_password(email, password):
    return md5("%s:%s" % (email, password)).hexdigest()

def main(email, password):
    try:
        user = User.get_by_email(email)
        user.passwd = hash_password(email, password)
        user.save()
    except Exception as e:
        print "Exception: %s" % e

    print "Success."

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python change_password.py <email> <new_password>"
    email = str(sys.argv[1])
    password = str(sys.argv[2])
    main(email, password)
