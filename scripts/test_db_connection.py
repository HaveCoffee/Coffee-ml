import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

# This will load the DATABASE_URL from your .env file
load_dotenv()

# We import the 'engine' directly from your existing database configuration
# This ensures we are testing with the exact same settings as your app
from app.database import engine

def check_db_connection():
    """
    Attempts to connect to the database and run a simple query.
    This is a safe, non-destructive check.
    """
    print("Attempting to connect to the database configured in your .env file...")
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("\n--- WARNING ---")
        print("DATABASE_URL not found in .env file. Testing connection to local Docker DB.")
    else:
        # Mask the password for security
        try:
            user, password_host, dbname = db_url.split("://")[1].split(":")
            password, host_port = password_host.split("@")
            print(f"Target: postgresql://{user}:*****@{host_port}/{dbname}")
        except Exception:
            print("Could not parse DATABASE_URL to display target safely.")

    try:
        # The 'with' statement ensures the connection is properly closed
        with engine.connect() as connection:
            # Run a very simple, standard query to confirm the connection is live
            connection.execute(text("SELECT 1"))
        
        print("\n SUCCESS: Database connection established successfully!")
        print("You can now safely run 'python -m app.seed_db'")

    except OperationalError as e:
        print("\n FAILED: Could not connect to the database. (OperationalError)")
        print("\n--- Likely Causes ---")
        print("1. AWS Security Group: Your current IP address is likely not whitelisted. Check the inbound rules.")
        print("2. Network Issue: Check your internet connection or if a VPN is blocking the port.")
        print("3. RDS Endpoint/Port: Double-check the host URL and port in your DATABASE_URL.")
        print("\n--- Raw Error ---")
        print(e)

    except ProgrammingError as e:
        print("\n FAILED: Connected, but authentication failed. (ProgrammingError)")
        print("\n--- Likely Causes ---")
        print("1. Wrong Credentials: Double-check the username, password, or database name in your DATABASE_URL.")
        print("\n--- Raw Error ---")
        print(e)
        
    except Exception as e:
        print(f"\n FAILED: An unexpected error occurred.")
        print("\n--- Raw Error ---")
        print(e)

if __name__ == "__main__":
    check_db_connection()