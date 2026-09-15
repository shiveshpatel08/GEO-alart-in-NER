"""
setup_portable_postgres.py
==========================
Sets up a fully self-contained, portable PostgreSQL 16 + PostGIS 3.6 instance
in the user's directory (C:\\Users\\<user>\\pgsql) with NO admin/UAC required.
Initializes the database cluster with user 'postgres' and password 'shubham',
creates 'geoalert_ner' database, and installs the PostGIS spatial extension.
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
import urllib.request

USER_DIR = Path(os.environ.get("USERPROFILE", "C:\\Users\\shive"))
PG_BASE = USER_DIR / "pgsql"
PG_DIR = PG_BASE / "pgsql"
PG_DATA = PG_BASE / "data"
PG_BIN = PG_DIR / "bin"
DOWNLOADS = USER_DIR / "Downloads"

PG_ZIP_URL = "https://get.enterprisedb.com/postgresql/postgresql-16.3-1-windows-x64-binaries.zip"
POSTGIS_ZIP_URL = "https://download.osgeo.org/postgis/windows/pg16/postgis-bundle-pg16-3.6.2x64.zip"

PG_ZIP_FILE = DOWNLOADS / "postgresql-16.3-1-windows-x64-binaries.zip"
POSTGIS_ZIP_FILE = DOWNLOADS / "postgis-bundle-pg16-3.6.2x64.zip"


def download_file(url: str, dest: Path):
    if dest.exists() and dest.stat().st_size > 1000000:
        print(f"[*] Already downloaded: {dest.name} ({dest.stat().st_size // (1024*1024)} MB)")
        return
    print(f"[*] Downloading {url} -> {dest} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    def report_progress(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, int(block_num * block_size * 100 / total_size))
            if block_num % 1000 == 0:
                print(f"    Progress: {percent}% ({block_num * block_size // (1024*1024)} MB / {total_size // (1024*1024)} MB)")
    
    urllib.request.urlretrieve(url, str(dest), reporthook=report_progress)
    print(f"[+] Download complete: {dest.name}")


def extract_zip(zip_path: Path, extract_to: Path):
    print(f"[*] Extracting {zip_path.name} -> {extract_to} ...")
    extract_to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    print(f"[+] Extracted: {zip_path.name}")


def main():
    print("=== GeoAlert-NER Portable PostgreSQL + PostGIS Auto-Setup ===")
    PG_BASE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    # 1. Download PostgreSQL 16
    download_file(PG_ZIP_URL, PG_ZIP_FILE)

    # 2. Extract PostgreSQL
    if not (PG_BIN / "postgres.exe").exists():
        extract_zip(PG_ZIP_FILE, PG_BASE)
    else:
        print("[*] PostgreSQL binaries already extracted.")

    # 3. Download PostGIS bundle
    download_file(POSTGIS_ZIP_URL, POSTGIS_ZIP_FILE)

    # 4. Extract PostGIS into PG_DIR (overwrites bin, lib, share)
    postgis_marker = PG_DIR / "share" / "extension" / "postgis.control"
    if not postgis_marker.exists():
        temp_postgis = PG_BASE / "temp_postgis"
        extract_zip(POSTGIS_ZIP_FILE, temp_postgis)
        
        # Merge contents of extracted PostGIS folder into PG_DIR
        subdirs = list(temp_postgis.glob("postgis-bundle*"))
        src_root = subdirs[0] if subdirs else temp_postgis
        
        print(f"[*] Copying PostGIS files from {src_root} to {PG_DIR} ...")
        for item in src_root.iterdir():
            target = PG_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
        
        # Cleanup temp
        shutil.rmtree(temp_postgis, ignore_errors=True)
        print("[+] PostGIS extension files copied successfully.")
    else:
        print("[*] PostGIS extension already present in PostgreSQL share directory.")

    # Add PG_BIN to PATH for current session
    os.environ["PATH"] = str(PG_BIN) + os.pathsep + os.environ["PATH"]

    # 5. Initialize cluster if data dir doesn't exist
    if not (PG_DATA / "PG_VERSION").exists():
        print("[*] Initializing PostgreSQL cluster in:", PG_DATA)
        pwfile = PG_BASE / "pw.txt"
        pwfile.write_text("shubham", encoding="utf-8")
        
        init_cmd = [
            str(PG_BIN / "initdb.exe"),
            "-D", str(PG_DATA),
            "-U", "postgres",
            "-A", "scram-sha-256",
            f"--pwfile={pwfile}",
            "-E", "UTF8",
            "--locale=C",
        ]
        res = subprocess.run(init_cmd, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print("initdb error:", res.stderr)
            sys.exit(1)
        if pwfile.exists():
            pwfile.unlink()
        print("[+] Database cluster initialized.")
    else:
        print("[*] Database cluster data directory already initialized.")

    # 6. Check if server is running; if not, start it
    status_cmd = [str(PG_BIN / "pg_ctl.exe"), "-D", str(PG_DATA), "status"]
    status_res = subprocess.run(status_cmd, capture_output=True, text=True)
    if "is running" not in status_res.stdout:
        print("[*] Starting PostgreSQL server...")
        log_file = PG_BASE / "server.log"
        start_cmd = [
            str(PG_BIN / "pg_ctl.exe"),
            "-D", str(PG_DATA),
            "-l", str(log_file),
            "start",
        ]
        start_res = subprocess.run(start_cmd, capture_output=True, text=True)
        print(start_res.stdout)
        if start_res.returncode != 0:
            print("Failed to start PostgreSQL:", start_res.stderr)
            sys.exit(1)
        print("[+] PostgreSQL server started successfully.")
    else:
        print("[*] PostgreSQL server is already running.")

    # 7. Create database 'geoalert_ner' if it doesn't exist
    env = os.environ.copy()
    env["PGPASSWORD"] = "shubham"
    
    check_db_cmd = [
        str(PG_BIN / "psql.exe"),
        "-U", "postgres",
        "-tAc", "SELECT 1 FROM pg_database WHERE datname='geoalert_ner'",
    ]
    check_db = subprocess.run(check_db_cmd, env=env, capture_output=True, text=True)
    if "1" not in check_db.stdout:
        print("[*] Creating database 'geoalert_ner'...")
        create_db_cmd = [str(PG_BIN / "createdb.exe"), "-U", "postgres", "geoalert_ner"]
        cd_res = subprocess.run(create_db_cmd, env=env, capture_output=True, text=True)
        if cd_res.returncode != 0:
            print("createdb error:", cd_res.stderr)
        else:
            print("[+] Database 'geoalert_ner' created.")
    else:
        print("[*] Database 'geoalert_ner' already exists.")

    # 8. Create PostGIS extension
    print("[*] Enabling PostGIS extension in 'geoalert_ner'...")
    postgis_cmd = [
        str(PG_BIN / "psql.exe"),
        "-U", "postgres",
        "-d", "geoalert_ner",
        "-c", "CREATE EXTENSION IF NOT EXISTS postgis; SELECT PostGIS_Version();",
    ]
    pg_res = subprocess.run(postgis_cmd, env=env, capture_output=True, text=True)
    print(pg_res.stdout)
    if "POSTGIS" in pg_res.stdout or "postgis_version" in pg_res.stdout.lower() or pg_res.returncode == 0:
        print("🎉 SUCCESS: PostgreSQL + PostGIS is fully operational!")
    else:
        print("PostGIS warning/error:", pg_res.stderr)


if __name__ == "__main__":
    main()
