import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def main():
    print("[*] Connecting to postgres database...")
    conn = psycopg2.connect("postgresql://postgres:shubham@localhost:5432/postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'geoalert_ner'")
    if not cur.fetchone():
        print("[*] Creating database geoalert_ner...")
        cur.execute("CREATE DATABASE geoalert_ner")
        print("[+] Database geoalert_ner created successfully!")
    else:
        print("[*] Database geoalert_ner already exists.")
    cur.close()
    conn.close()

    print("[*] Connecting to geoalert_ner database...")
    conn2 = psycopg2.connect("postgresql://postgres:shubham@localhost:5432/geoalert_ner")
    conn2.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur2 = conn2.cursor()
    print("[*] Enabling PostGIS extension...")
    cur2.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    print("[+] PostGIS extension enabled!")
    cur2.execute("SELECT PostGIS_Full_Version()")
    full_ver = cur2.fetchone()[0]
    print("[+] PostGIS Full Version:", full_ver)
    cur2.close()
    conn2.close()

if __name__ == "__main__":
    main()
