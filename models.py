# Klasa użytkownika
# Stwórz klasę, obsługującą użytkownika. Powinna ona posiadać następujące atrybuty:
# _id – ustawione podczas tworzenia na -1,
# username – nazwa użytkownika,
# _hashed_password – zahaszowane hasło użytkownika.

# Udostępnij _id i _hashed_password do odczytu na zewnątrz.
# Dodaj metodę, która pozwoli, na ustawienie nowego hasła (Podpowiedź: możesz użyć settera).
# Dodaj metody do obsługi bazy: save_to_db – zapis do bazy danych lub aktualizacja obiektu w bazie,
# load_user_by_username – wczytanie użytkownika z bazy danych na podstawie jego nazwy, load_user_by_id – wczytanie użytkownika z bazy danych na podstawie jego id, load_all_users – wczytanie wszystkich użytkowników z bazy danych, delete – usunięcie użytkownika z bazy i nastawienie jego _id na -1.

# Podpowiedzi:

# Wszystkie powyższe metody, powinny przyjmować kursor do obsługi bazy danych.
# Możesz wykorzystać kod, który omówiliśmy w artykule poświęconym wzorcowi projektowemu Active Record. Wystarczy, że dodasz do niego metodę, wczytującą użytkownika z bazy na podstawie jego imienia.

from psycopg2 import connect, OperationalError, ProgrammingError
from password_hashing import hash_password

class User:
    def __init__(self, username="", password="", salt=""):
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
                            VALUES(%s, %s) RETURNING id"""
            values = (self.username, self.hashed_password)
            cursor.execute(sql, values)
            self._id = cursor.fetchone()[0]  # or cursor.fetchone()['id'], first object in a tupe
            return True
        else:
            sql = """UPDATE Users SET username=%s, hashed_password=%s
                           WHERE id=%s"""
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
        sql = "DELETE FROM Users WHERE id=%s"
        cursor.execute(sql, (self.id,))
        self._id = -1
        return True

user1 = User("E.T", "go_home") # id = 3
user2 = User("Alf", "eat_cat")

#try:
#    cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
#    cursor = cnx.cursor()
#    user1.save_to_db(cursor)
#    user2.save_to_db(cursor)
#    cnx.commit()
#    cnx.close()
#except OperationalError:
#    print("Something went wrong.")


try:
    cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
    cursor = cnx.cursor()
    
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



# Klasa wiadomości
# Utwórz teraz klasę, która będzie obsługiwała nasze wiadomości. 
# Powinna ona posiadać następujące atrybuty:
# _id – ustawione podczas tworzenia na -1,
# from_id – id nadawcy, ustawiane podczas tworzenia obiektu,
# to_id – id odbiorcy, ustawiane podczas tworzenia obiektu,
# text – tekst do przesłania,
# creation_data – data utworzenia wiadomości. Podczas tworzenia przypisz do niej None. Ustawisz ją w momencie zapisu do bazy danych.

# Udostępnij _id na zewnątrz.
# Dodaj metody do obsługi bazy:
# save_to_db – zapis do bazy danych lub aktualizacja obiektu w bazie,
# load_all_messages – wczytanie wszystkich wiadomości.

# Podpowiedzi:

# Usuwanie wiadomości, nie będzie nam potrzebne.
# Metody, będą bardzo podobne do tych z klasy użytkownika. Wystarczy, że lekko je zmodyfikujesz.
# Pamiętaj, żeby przetestować, czy biblioteka działa. Możesz wykorzystać scenariusze testowe, opisane w artykule omawiającym Active Record.

class Messages:
    def __init__(self, username="", password="", salt=""):
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
                            VALUES(%s, %s) RETURNING id"""
            values = (self.username, self.hashed_password)
            cursor.execute(sql, values)
            self._id = cursor.fetchone()[0]  # or cursor.fetchone()['id'], first object in a tupe
            return True
        else:
            sql = """UPDATE Users SET username=%s, hashed_password=%s
                           WHERE id=%s"""
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
        sql = "DELETE FROM Users WHERE id=%s"
        cursor.execute(sql, (self.id,))
        self._id = -1
        return True
