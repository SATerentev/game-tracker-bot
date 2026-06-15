import psycopg2
import os
import csv
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

root_dir = Path(__file__).parent.parent
dotenv_path = root_dir / '.env'
load_dotenv(dotenv_path)

CSV_path = root_dir / 'DATA' / 'migrations-schema.csv'

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def DB_connection():
    return psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname=DB_NAME
)

def get_applied_versions():
    if not CSV_path.exists():
        print("CSV file not found. It will be created when the migration process starts")
        return []
    
    versions = []

    with open(CSV_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            versions.append(row.get("version"))
    
    return versions

def mark_version_applied(version: str):
    CSV_file_exists = CSV_path.exists()

    with open(CSV_path, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        if not CSV_file_exists:
            writer.writerow(['version', 'applied_at'])
        
        writer.writerow([version, datetime.now().date()])

def make_migration(connection, version, sql_file):
    try:
        with connection.cursor() as cursor:
            with open(sql_file, encoding="utf-8") as file:
                cursor.execute(file.read())
    except Exception as e:
        print(f"Migration process error:\n{e}")
        connection.rollback()
        return

    connection.commit()
    mark_version_applied(version)

def main():
    connection = DB_connection()
    applied_version = get_applied_versions()
    migrations_dir = Path(__file__).parent / 'migrations'

    if not migrations_dir.exists():
        print("Directory 'migrations' does not exist. It will be created now")
        Path.mkdir(migrations_dir)

    migrations_files = migrations_dir.glob('*.sql')

    for sql_file in migrations_files:
        version = sql_file.name.split('_')[0]
        if version not in applied_version:
            print("Migration " + sql_file.name + " starting")
            make_migration(connection, version, sql_file)
            print("Complete")

    connection.close()

if __name__ == "__main__":
    main()