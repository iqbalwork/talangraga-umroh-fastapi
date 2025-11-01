from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/talangraga')

with engine.connect() as conn:
    # Check current version
    result = conn.execute(text('SELECT * FROM alembic_version'))
    print("Current version:", list(result))
    
    # Update to the latest existing revision
    conn.execute(text("UPDATE alembic_version SET version_num = 'dac2213323b8'"))
    conn.commit()
    
    # Verify the update
    result = conn.execute(text('SELECT * FROM alembic_version'))
    print("Updated version:", list(result))

print("✓ Database updated to use existing revision 'dac2213323b8'")
