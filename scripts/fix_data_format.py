import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load connection settings
load_dotenv()
sys.path.append(os.getcwd())

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def fix_uuids():
    print("--- 🛠️  Starting Data Migration (Hyphenated -> Hex) ---")
    
    with engine.connect() as conn:
        # 1. Find the exact name of the Foreign Key constraint
        # (It is usually 'profiles_user_id_fkey', but we verify to be safe)
        print("1. Identifying Foreign Key constraint...")
        result = conn.execute(text("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'profiles'::regclass
            AND confrelid = 'users'::regclass
            AND contype = 'f';
        """))
        fk_name = result.scalar()
        
        if not fk_name:
            print("   [WARNING] No Foreign Key found on 'profiles'. Skipping drop step.")
        else:
            print(f"   -> Found constraint: {fk_name}")
            
            # 2. Drop the Foreign Key temporarily
            print("2. Dropping Foreign Key temporarily...")
            conn.execute(text(f"ALTER TABLE profiles DROP CONSTRAINT {fk_name}"))
            conn.commit()

        try:
            # 3. Update the USERS table
            # Removes all '-' characters from the user_id
            print("3. Updating 'users' table (Removing hyphens)...")
            conn.execute(text("UPDATE users SET user_id = REPLACE(user_id, '-', '')"))
            
            # 4. Update the PROFILES table
            print("4. Updating 'profiles' table (Removing hyphens)...")
            conn.execute(text("UPDATE profiles SET user_id = REPLACE(user_id, '-', '')"))
            
            conn.commit()
            print("   -> Data update successful.")

        except Exception as e:
            print(f"   [ERROR] Update failed: {e}")
            print("   Rolling back changes...")
            # Ideally we would re-add the constraint here, but since the update failed, 
            # the IDs might be mismatched. You might need to check manually.
            raise e

        # 5. Re-create the Foreign Key
        print("5. Re-creating Foreign Key constraint...")
        # Note: We assume ON DELETE CASCADE because that's standard for profiles
        conn.execute(text("""
            ALTER TABLE profiles 
            ADD CONSTRAINT profiles_user_id_fkey 
            FOREIGN KEY (user_id) REFERENCES users(user_id) 
            ON DELETE CASCADE
        """))
        conn.commit()

    print("\n✅ SUCCESS: All User IDs have been converted to Hex format.")

if __name__ == "__main__":
    fix_uuids()