import csv
import sqlite3
import os

def sync_voters_from_csv(csv_path='C:/Users/DELL/Desktop/evote/voters.csv'):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return

    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist (safety check)
    cursor.execute('''CREATE TABLE IF NOT EXISTS authorized_voters (
                        roll TEXT PRIMARY KEY, 
                        name TEXT, 
                        phone TEXT, 
                        branch TEXT)''')

    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                # Using INSERT OR IGNORE to prevent errors if the roll already exists
                cursor.execute('''INSERT OR IGNORE INTO authorized_voters (roll, name, phone, branch) 
                                 VALUES (?, ?, ?, ?)''', 
                              (row['roll'], row['name'], row['phone'], row['branch']))
                count += 1
            except KeyError as e:
                print(f"Error: CSV missing column {e}")
                break

    conn.commit()
    conn.close()
    print(f"Successfully synced {count} voters from CSV to database.")

if __name__ == "__main__":
    sync_voters_from_csv()