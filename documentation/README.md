"# projecta_darbs" 

Klonējot darbu nepieciešams:
    1.Izveidot pašam savu venv mapi (tā atrodas blakus website mapei, nevis tajā iekšā)
    2.Izveidot .env failu, kurā
        2.1 Jānorāda secret_key 
            SECRET_KEY = "#ievadi atslēgu šeit"
        2.2 Jānorāda flask_env
            FLASK_ENV = "piemēram development"
        2.3 Jānorāda maintenence mode status
            MAINTENANCE_MODE = "False vai True"
    3. Jāizveido database.py fails pēc šāda principa (Ffaktiski copy/paste izveidojot savu datubāzi):
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

        def endWrokDB(conn):
            conn.commit()
            conn.close()
    
