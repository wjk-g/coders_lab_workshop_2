import argparse
from models import User
from psycopg2 import connect, IntegrityError
from clcrypto import check_password, hash_password

# Creating the parser
parser = argparse.ArgumentParser()

# Adding arguments to parser
parser.add_argument("-u", "--username", help="username")
parser.add_argument("-p", "--password", help="password (min 8 characters)")
parser.add_argument("-l", "--list", help="list users", action="store_true")
parser.add_argument("-n", "--new_pass", help="change password")
parser.add_argument("-d", "--delete", help="delete user", action="store_true")
parser.add_argument("-e", "--edit", help="edit user", action="store_true")

args = parser.parse_args()

# Connecting to the db
cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
# Creating the cursor
cursor = cnx.cursor()

def create_user(username, password):
    try:
        if len(password) > 7:
            new_user = User(username, password)
            new_user.save_to_db(cursor)
            cnx.commit()            
            print("New user succesfully created.")
        else:
            print("Your password must be at least 8 characters long.")
    except IntegrityError:
        print("The user already exists.")

def edit_password(username, password, new_password):
    loaded_user = User.load_user_by_username(cursor, username)
    #print("loaded_user: ", loaded_user.username)
    if loaded_user:
        if check_password(password, loaded_user._hashed_password):
            loaded_user._hashed_password = hash_password(new_password) # !
            print("Check id: " + str(loaded_user._id))
            loaded_user.save_to_db(cursor)
            cnx.commit()
            print("Password succesfully changed.")
        else:
            print("Wrong password.")
    else:
        print("There is no such user.")
    
def delete_user(username, password):
    loaded_user = User.load_user_by_username(cursor, username)
    if loaded_user:
        if check_password(password, loaded_user._hashed_password):
            loaded_user.delete(cursor)
            cnx.commit() # !
            print("The user was succesfully delted.")
        else:
            print("Wrong password.")
    else:
        print("There is no such user.")

def list_all_users():
    all_users = User.load_all_users(cursor)
    [print(user.id, user.username) for user in all_users]

# Control flow
if args.list:
    list_all_users()
elif args.username and args.password:
    if args.edit:
        edit_password(args.username, args.password, args.new_pass)
    elif args.delete:
        delete_user(args.username, args.password)
    else:
        create_user(args.username, args.password)
else:
    parser.print_help()
