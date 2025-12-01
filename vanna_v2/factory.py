
#db_connect/factory.py
import os
from dotenv import load_dotenv

# Import Runners
from db_connect.sqlite_runner import SqliteRunner
from db_connect.oracle_runner import OracleRunner
from db_connect.postgres_runner import PostgresRunner
from db_connect.mssql_runner import MSSQLRunner

load_dotenv()


class UnsupportedDatabaseError(Exception):
    """Custom exception for unsupported database types."""
    pass


def _validate_env(var_name: str):
    """Ensure critical environment variables exist."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"❌ ERROR: Missing required environment variable: {var_name}")
    return value


def build_oracle_dsn():
    """
    Oracle DSN builder.
    Supports SERVICE_NAME or SID.
    """
    host = _validate_env("ORACLE_HOST")
    port = _validate_env("ORACLE_PORT")

    service = os.getenv("ORACLE_SERVICE_NAME")
    sid = os.getenv("ORACLE_SID")

    if service:
        return f"{host}:{port}/{service}"
    elif sid:
        return f"{host}:{port}:{sid}"
    else:
        raise ValueError(
            "❌ ERROR: For Oracle, you must specify either ORACLE_SERVICE_NAME or ORACLE_SID."
        )


def build_postgres_url():
    """
    Provides full Postgres URL from environment.
    Format: postgresql://user:pass@host:port/db
    """
    user = _validate_env("POSTGRES_USER")
    password = _validate_env("POSTGRES_PASSWORD")
    host = _validate_env("POSTGRES_HOST")
    port = _validate_env("POSTGRES_PORT")
    db = _validate_env("POSTGRES_DB")

    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def build_mssql_url():
    """
    MSSQL URL builder.
    Format:
      mssql+pyodbc://user:pass@host:port/db?driver=ODBC+Driver+18+for+SQL+Server
    """
    user = _validate_env("MSSQL_USER")
    password = _validate_env("MSSQL_PASSWORD")
    host = _validate_env("MSSQL_HOST")
    port = _validate_env("MSSQL_PORT")
    db = _validate_env("MSSQL_DB")
    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")

    return (
        f"mssql+pyodbc://{user}:{password}@{host}:{port}/{db}"
        f"?driver={driver.replace(' ', '+')}"
    )


# ===========================================================
#   THE FACTORY (MAIN ENTRYPOINT)
# ===========================================================

def get_db_runner():
    """
    Factory Pattern:
    Returns the correct DB Runner based on DB_TYPE.
    Supported:
        sqlite, oracle, postgres, postgresql, mssql
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    print(f"🔧 [Factory] Selecting DB Runner for DB_TYPE = {db_type}")

    # -------------------------------------------------------
    # 1. SQLite (Local Development)
    # -------------------------------------------------------
    if db_type == "sqlite":
        sqlite_path = os.getenv("SQLITE_DB_PATH")
        if not sqlite_path:
            raise ValueError("❌ SQLITE_DB_PATH is missing in .env")
        print(f"📂 Using SQLite at: {sqlite_path}")
        return SqliteRunner(sqlite_path)

    # -------------------------------------------------------
    # 2. Oracle (Enterprise)
    # -------------------------------------------------------
    if db_type == "oracle":
        user = _validate_env("ORACLE_USER")
        password = _validate_env("ORACLE_PASSWORD")
        dsn = build_oracle_dsn()

        print(f"🏦 Using Oracle: DSN={dsn}")
        return OracleRunner(user=user, password=password, dsn=dsn)

    # -------------------------------------------------------
    # 3. PostgreSQL
    # -------------------------------------------------------
    if db_type in ("postgres", "postgresql"):
        url = build_postgres_url()
        print(f"🐘 Using PostgreSQL: {url}")
        return PostgresRunner(url)

    # -------------------------------------------------------
    # 4. MSSQL
    # -------------------------------------------------------
    if db_type == "mssql":
        url = build_mssql_url()
        print(f"🧩 Using MSSQL: {url}")
        return MSSQLRunner(url)

    # -------------------------------------------------------
    # 5. Unsupported
    # -------------------------------------------------------
    raise UnsupportedDatabaseError(
        f"❌ Unsupported DB_TYPE: {db_type}\n"
        f"   Valid options: sqlite, oracle, postgres, postgresql, mssql"
    )
