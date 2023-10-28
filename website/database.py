import psycopg2

def startWorkDB():
    conn = psycopg2.connect(host="LocalHost", 
                            dbname = "postgres", 
                            user = "postgres",
                            password = "V8laukums@",
                            port = 5432)
    
    cur = conn.cursor()

    return conn, cur
    
def endWrokDB(conn):
    conn.commit()
    conn.close()

def initializeDB():
    conn = psycopg2.connect(host="LocalHost", 
                            dbname = "postgres", 
                            user = "postgres",
                            password = "V8laukums@",
                            port = 5432)

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
                password VARCHAR(150)
    );
    """)

    conn.commit()
    conn.close()