# Na początek zajmijmy się skonfigurowaniem naszej bazy danych. 
# Napisz w tym celu skrypt pythona: create_db.py, w którym:

# Utworzysz bazę danych. Jeśli baza już istnieje, skrypt ma poinformować o tym użytkownika, 
# nie przerywając swojego działania (Podpowiedź: możesz przechwycić błąd: DuplicateDatabase).

from psycopg2 import connect, ProgrammingError # ProgrammingError imports DuplicateDatabase and DuplicateTable

sql_create_db = 'CREATE DATABASE workshop2;'

# Create database workshop2
try:
    cnx = connect(user="postgres", password="hopfizz", host="localhost")
    cursor = cnx.cursor()
    cnx.autocommit = True # This is necessary when creating a new database
    # psycopg2.errors.ActiveSqlTransaction: CREATE DATABASE cannot run inside a transaction block
    cursor.execute(sql_create_db)
    print("The database has been created.")
except ProgrammingError: # can this be made more explicit? (https://www.psycopg.org/docs/errors.html)
    print("The database you're trying to create already exists.")
else:
    cursor.close()
    cnx.close()

# Stworzysz tabelę trzymającą dane użytkownika (users). Powinna posiadać następujące kolumny:
# + id – klucz główny (najlepiej typu serial),
# + username – ciąg znaków (varchar(255)),
# + hashed_password – ciąg znaków (varchar(80)). 
# Jeżeli istnieje już taka tabela, skrypt powinien poinformować o tym użytkownika, 
# nie przerywając swojego działania (Podpowiedź: możesz przechwycić błąd: DuplicateTable).

sql_create_users_tbl = '''CREATE TABLE users (
    id serial,
    username varchar(255),
    hashed_password varchar(80)
    PRIMARY KEY (id)
    )
'''

try:
    cnx = connect(user="postgres", password="hopfizz", host="localhost", database="workshop2")
    cursor = cnx.cursor()
    cursor.execute(sql_create_users_tbl)
    cnx.commit()
    print("Table has been created.")
    cnx.close()
except ProgrammingError: # DuplicateTable
    print("The table you're trying to create already exists.")

# Stworzysz tabelę przechowującą komunikaty (messages). Powinna posiadać następujące kolumny:
# + id – klucz główny (najlepiej typu serial),
# + from_id – klucz obcy do tabeli users,
# + to_id – klucz obcy do tabeli users,
# + creation_date – timestamp, dodawany automatycznie,
# + text – ciąg znaków (varchar(255)). Jeżeli istnieje już taka tabela, skrypt powinien poinformować o tym użytkownika, nie przerywając swojego działania (Podpowiedź: możesz przechwycić błąd: DuplicateTable).

# Pamiętaj o zamknięciu połączenia. Powinieneś też obsłużyć ewentualne błędy połączenia (OperationalError).

sql_create_messages_tbl = '''
CREATE TABLE messages (
    id serial,
    from_id int not null
    to_id int not null
    creation_date timestamp
    text varchar(255)
    PRIMARY KEY(id)
    FOREIGN KEY(from_id)
    FOREIGN KEY(to_id) 

)
'''
