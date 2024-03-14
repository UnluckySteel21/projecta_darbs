# Projecta Darbs

Šis projekts ir Autoservisa vadības sistēma, kas veic klientu un remontdarbu uzskaiti. 

Klonējot darbu jums nepieciešams:

1. Izveidot savu `venv` direktoriju (tam jāatrodas blakus jūsu `website` direktorijam, nevis tajā iekšā).
    - Lai to izdarītu sāciet ar komandas ierakstīšanu:
    ```cmd
    py -m venv venv
    ```
    - Tālāk aktivizējiet `venv`:
    ```cmd
    venv\scripts\activate.bat
    ```

2. Ieinstallējiet nepieciešamās bibliotēkas:
    ```cmd
    pip install -r documentation\requirments.txt
    ```

3. Iekšā `website` direktorijā izveidojiet `.env` failu, kurā norādiet:
    - `SECRET_KEY`: Piemēram, `SECRET_KEY = "#your_secret_key_here"`
    - `FLASK_ENV`: Piemēram, `FLASK_ENV = "development"`
    - `MAINTENANCE_MODE`: Piemēram, `MAINTENANCE_MODE = "False"` vai `MAINTENANCE_MODE = "True"`

4. Izveidojiet `database.py` failu kurā faktiski nokopēsiet apakšā redzamo kodu. Jums nāksies pielāgot failu atbilstoši jūsu datubāzei. Sākotnēji kods bijis paredzēts postgreSQL datubāzei, bet vēlāk pārveidots tā, lai darbotos arī ar mySQL. 
    - Ja vēlaties izmantot postgreSQL (Būs manuāli jāpieinstalē bibliotēka):
    ```cmd
    pip install psycopg2
    ```

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
    
        cur.execute("""
        CREATE TABLE IF NOT EXISTS person (
            id CHAR(36) PRIMARY KEY,
            name VARCHAR(50),
            surname VARCHAR(50),
            password VARCHAR(150),
            email VARCHAR(50) UNIQUE,
            phoneNumber VARCHAR(30),
            description VARCHAR(350),
            admin BOOLEAN NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS reservation (
            reservation_id CHAR(36) PRIMARY KEY,
            person_id CHAR(36),
            car_number VARCHAR(50),
            description VARCHAR(350),
            FOREIGN KEY (person_id) REFERENCES person(id)
            );
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS car (
            id CHAR(36) PRIMARY KEY,
            brand VARCHAR(50),
            model VARCHAR(50),
            carNum VARCHAR(20),
            carVin VARCHAR(50),
            date VARCHAR(30),
            description VARCHAR(350),
            person_id CHAR(36),
            status BOOLEAN NOT NULL,
            FOREIGN KEY (person_id) REFERENCES person(id)
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id CHAR(36) PRIMARY KEY,
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
    ```
    - Ja plānojat izmantot mySQL:

    ```python
    import mysql.connector
    
    def startWorkDB():
        conn = mysql.connector.connect(host="LOCALHOST", 
                                       user="ROOT", 
                                       password="PASSWORD", 
                                       database="DATABASE_NAME")
        cur = conn.cursor()
        return conn, cur
    
    def endWorkDB(conn):
        conn.commit()
        conn.close()
    
    def initializeDB():
        conn, cur = startWorkDB()
    
        cur.execute("""
        CREATE TABLE IF NOT EXISTS person (
            id CHAR(36) PRIMARY KEY,
            name VARCHAR(50),
            surname VARCHAR(50),
            password VARCHAR(150),
            email VARCHAR(50) UNIQUE,
            phoneNumber VARCHAR(30),
            description VARCHAR(350),
            admin BOOLEAN NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS reservation (
            reservation_id CHAR(36) PRIMARY KEY,
            person_id CHAR(36),
            car_number VARCHAR(50),
            description VARCHAR(350),
            FOREIGN KEY (person_id) REFERENCES person(id)
            );
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS car (
            id CHAR(36) PRIMARY KEY,
            brand VARCHAR(50),
            model VARCHAR(50),
            carNum VARCHAR(20),
            carVin VARCHAR(50),
            date VARCHAR(30),
            description VARCHAR(350),
            person_id CHAR(36),
            status BOOLEAN NOT NULL,
            FOREIGN KEY (person_id) REFERENCES person(id)
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id CHAR(36) PRIMARY KEY,
            email VARCHAR(50),
            password VARCHAR(150),
            admin BOOLEAN NOT NULL
        );
        """)
    
        endWorkDB(conn)
    ```
