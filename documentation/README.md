# Projecta Darbs

When cloning the project, you need to:

1. Create your own `venv` directory (it should be located next to the `website` directory, not inside it).

2. Create a `.env` file, in which you need to specify:
    - `SECRET_KEY`: For example, `SECRET_KEY = "#your_secret_key_here"`
    - `FLASK_ENV`: For example, `FLASK_ENV = "development"`
    - `MAINTENANCE_MODE`: For example, `MAINTENANCE_MODE = "False"` or `MAINTENANCE_MODE = "True"`

3. Create a `database.py` file following this principle (basically copy/paste when creating your own database). Yes, I misspelled `endWorkDB` and don't want to rewrite all my code (it has been corrected). So far, the code works with PostgreSQL:

```python
import psycopg2

def startWorkDB():
    conn = psycopg2.connect(host="HOST NAME", 
                            dbname = "DB NAME", 
                            user = "USER NAME",
                            password = "PASSWORD",
                            port = PORT)
    
    cur = conn.cursor()

    return conn, cur

def initializeDB():
    conn = psycopg2.connect(host="HOST NAME", 
                            dbname = "DB NAME", 
                            user = "USER NAME",
                            password = "PASSWORD",
                            port = PORT)

    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS person (
                id UUID PRIMARY KEY,
                name VARCHAR(50),
                surname VARCHAR(50),
                email VARCHAR(50) UNIQUE,
                phoneNumber VARCHAR(30)
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS car (
                id UUID PRIMARY KEY,
                brand VARCHAR(50),
                model VARCHAR(50),
                carNum VARCHAR(20),
                carVin VARCHAR(50),
                date VARCHAR(30),
                description VARCHAR(350),
                person_id UUID REFERENCES person(id),
                status BOOLEAN NOT NULL
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS logindata (
                id UUID PRIMARY KEY,
                email VARCHAR(50) REFERENCES person(email),
                password VARCHAR(150),
                admin BOOLEAN NOT NULL
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS admins (
                id UUID PRIMARY KEY,
                email VARCHAR(50),
                password VARCHAR(150),
                admin BOOLEAN NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def endWorkDB(conn):
    conn.commit()
    conn.close()