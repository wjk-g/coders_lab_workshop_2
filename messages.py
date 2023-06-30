import argparse
from models import User, Message
from clcrypto import check_password
from psycopg2 import connect

# Creating the parser
parser = argparse.ArgumentParser()

# Adding arguments to parser
parser.add_argument("-u", "--username", help="username")
parser.add_argument("-p", "--password", help="password (min 8 characters)")
parser.add_argument("-t", "--to", help="recipient name")
parser.add_argument("-s", "--send", help="message contents")
parser.add_argument("-l", "--list", help="print all messages sent to a user", action="store_true")

args = parser.parse_args()

# Connecting to the db
cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
# Creating the cursor
cursor = cnx.cursor()

def send_message(username, password, to_username, message_text):
    sender = User.load_user_by_username(cursor, username)
    recipient = User.load_user_by_username(cursor, to_username)
    if sender:
        if recipient:
            if check_password(password, sender._hashed_password):
                #message_text = input("Type your message: ")
                message = Message(sender._id, recipient._id, message_text)
                message.save_to_db(cursor)
                cnx.commit()
                print("Message sent.")
            else:
                print("Wrong password.")
        else:
            print("The recipient does not exist.")
    else:
        print("The sender does not exist.")

#send_message("test_sender", "12345678", "test_recipient")
#send_message("test_sender", "12345678", "test_recipient")
#send_message("test_sender", "slkdgjslgj", "test_recipient")

def list_messages_sent_to_user(username, password):
    recipient = User.load_user_by_username(cursor, username)
    if recipient:
        if check_password(password, recipient._hashed_password):
            messages = Message.load_all_messages(cursor)
            [print(message.text) for message in messages if message.to_id == recipient._id]
        else:
            print("Wrong password.")
    else:
        print("No such user.")

#list_messages_sent_to_user("test_recipient")

# Control flow
if args.username and args.password and args.to and args.send:
    send_message(args.username, args.password, args.to, args.send)
elif args.username and args.password and args.list:
    list_messages_sent_to_user(args.username, args.password)
else:
    parser.print_help()