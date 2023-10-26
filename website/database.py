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
                name VARCHAR(255),
                surname VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                phoneNumber VARCHAR(255)
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS car (
                id UUID PRIMARY KEY,
                brand VARCHAR(255),
                model VARCHAR(255),
                carNum VARCHAR(255),
                carVin VARCHAR(255),
                date VARCHAR(255),
                description VARCHAR(255),
                person_id UUID REFERENCES person(id)
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS logindata (
                id UUID PRIMARY KEY,
                email VARCHAR(255) REFERENCES person(email),
                password VARCHAR(255)
    );
    """)

    conn.commit()
    conn.close()