import sqlite3

# Connect to the database
conn = sqlite3.connect('bookings.db')
print("Connected to database")

# Check if tables exist
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", tables)

# Check if bookings table exists and has correct structure
if ('bookings',) in tables:
    cursor.execute('PRAGMA table_info(bookings)')
    columns = cursor.fetchall()
    print("Bookings table columns:", columns)
else:
    print("Bookings table does not exist")

# Close the connection
conn.close()
