import sqlite3

# Connect to database (it will create if it doesn't exist)
conn = sqlite3.connect('campusconnect.db')
cursor = conn.cursor()

# Read SQL schema file
with open('schema.sql', 'r') as f:
    sql = f.read()

# Execute the SQL commands
cursor.executescript(sql)

conn.commit()
conn.close()
print("Database initialized successfully!")
