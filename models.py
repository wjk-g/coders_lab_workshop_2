from psycopg2 import connect, OperationalError, ProgrammingError
from clcrypto import hash_password

### ===========
# User class
### ===========

class User:
    def __init__(self, username="", password="", salt=""): # not sure what salt actually does here
        self._id = -1
        self.username = username
        self._hashed_password = hash_password(password, salt)

    @property
    def id(self):
        return self._id

    @property
    def hashed_password(self):
        return self._hashed_password

    def set_password(self, password, salt=""):
        self._hashed_password = hash_password(password, salt)

    @hashed_password.setter
    def hashed_password(self, password):
        self.set_password(password)

    def save_to_db(self, cursor):
        if self._id == -1:
            sql = """INSERT INTO users(username, hashed_password)
                            VALUES(%s, %s) RETURNING id;""" # https://www.postgresql.org/docs/current/dml-returning.html (~ostatni wstawiony / edytowany element)
            values = (self.username, self.hashed_password)
            cursor.execute(sql, values)
            self._id = cursor.fetchone()[0]  # or cursor.fetchone()['id'], first object in a tupe
            return True
        else:
            sql = """UPDATE Users SET username=%s, hashed_password=%s
                           WHERE id=%s;"""
            values = (self.username, self.hashed_password, self.id)
            cursor.execute(sql, values)
            return True
    
    @staticmethod
    def load_user_by_id(cursor, id_):
        sql = 'SELECT id, username, hashed_password FROM users WHERE id=%s;' # there are no semicolons on LMS
        cursor.execute(sql, (id_,))
        data = cursor.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            # we cannot used the setter for _hashed_password because the password has already been hashed!
            loaded_user._hashed_password = hashed_password 
            
            return loaded_user
        else: # not necessary, improves code readability
            return None
        
    @staticmethod
    def load_user_by_username(cursor, username):
        sql = 'SELECT id, username, hashed_password FROM users WHERE username=%s;'
        cursor.execute(sql, (username,))
        data = cursor.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            #loaded_user.username = username
            return loaded_user
        else: # not necessary, improves code readability
            return None

        
    @staticmethod
    def load_all_users(cursor):
        sql = 'SELECT id, username, hashed_password FROM users;' # no semicolon on LMS
        users = []
        cursor.execute(sql)
        for row in cursor:
            id_, username, hashed_password = row
            loaded_user = User()
            loaded_user._id = id_
            loaded_user.username = username
            loaded_user._hashed_password = hashed_password
            users.append(loaded_user)
        return users
    
    def delete(self, cursor):
        sql = "DELETE FROM Users WHERE id=%s;"
        cursor.execute(sql, (self.id,))
        self._id = -1
        return True

user1 = User("E.T", "go_home")
user2 = User("Alf", "eat_cat")
user3 = User("Dalek", "exterminate!")

if False: 
    try:
        cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
        cursor = cnx.cursor()
        user1.save_to_db(cursor)
        user2.save_to_db(cursor)
        user3.save_to_db(cursor)
        cnx.commit()
        cnx.close()
    except OperationalError:
        print("Something went wrong.")


### ================
# Message class
### ================

class Message:
    def __init__(self, from_id="", to_id="", text="", salt=""):
        self._id = -1
        self.from_id = from_id
        self.to_id = to_id
        self.text = text
        self._creation_date = None

    @property
    def id(self):
        return self._id
    
    @property
    def creation_date(self):
        return self._creation_date

    def save_to_db(self, cursor):
        if self._id == -1:

            sql = """INSERT INTO messages(from_id, to_id, text)
                            VALUES(%s, %s, %s) RETURNING id, creation_date;"""
            values = (self.from_id, self.to_id, self.text)
            cursor.execute(sql, values)
            self._id, self._creation_date = cursor.fetchone()
            #print("unpacking the contents of RETURNING: " + str(self._id) + " " + str(self._creation_date))
            return True
        else:
            sql = """UPDATE messages SET from_id=%s, to_id=%s, text=%s
                           WHERE id=%s;"""
            values = (self.from_id, self.to_id, self.text, self.id)
            cursor.execute(sql, values)
            return True
        
    @staticmethod
    def load_all_messages(cursor):
        sql = 'SELECT id, from_id, to_id, text, creation_date FROM messages;' # no semicolon on LMS
        messages = []
        cursor.execute(sql)
        for row in cursor:
            id_, from_id, to_id, text, creation_date = row
            message = Message()
            message._id = id_
            message.from_id = from_id
            message.to_id = to_id 
            message.text = text
            message._creation_date = creation_date
            messages.append(message)
        return messages
    
    @staticmethod
    def clear_messages(cursor):
        sql = 'DELETE FROM messages;'
        cursor.execute(sql)
        return True

### ================
# Testing User
### ================

if False:
    try:
        cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
        cursor = cnx.cursor()

        # Clearing messages to avoid conflicts
        Message.clear_messages(cursor)

        # Check load_user_by_id method
        user_with_existing_id = User.load_user_by_id(cursor, 3)
        user_with_wrong_id = User.load_user_by_id(cursor, 999)
        print(user_with_existing_id)
        print(user_with_wrong_id)
        
        # Check load_all_users method
        all_users = User.load_all_users(cursor)
        print(all_users[1]._id, all_users[1].username, all_users[1].hashed_password)
        
        # Check expanded save_to_db (update user)
        user_with_existing_id.username = "Dalek"
        user_with_existing_id.hashed_password = "exterminate"
        user_with_existing_id.save_to_db(cursor)
        print(User.load_user_by_id(cursor, 3)._id)
        print(User.load_user_by_id(cursor, 3).username)
        print(User.load_user_by_id(cursor, 3).hashed_password)
        cnx.commit() # necessary to save changes in the db

        # Check delete
        print(f"There are now {len(all_users)} users in the database.")
        dalek = User.load_user_by_id(cursor, 3)
        print(dalek._id)
        dalek.delete(cursor)
        print(dalek._id)
        all_users = User.load_all_users(cursor)
        print(f"There are now {len(all_users)} users in the database.")
    except OperationalError:
        print("Something went wrong.")

### ================
# Testing Message
### ================

if False:
    try:
        cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
        cursor = cnx.cursor()

        # Check save_to_db
        message1 = Message(3, 4, "Exterminate! Exterminate!")
        message1.save_to_db(cursor)
        print(f"From: {message1.from_id}, to: {message1.to_id}. Message: {message1.text}")
        cnx.commit()
    except OperationalError:
        print("Something went wrong.")