import sqlite3
import sys
import os

def display_table_data(cursor, table_name):
    print(f"\n--- Viewing Table: '{table_name}' ---")

    try:
        cursor.execute(f'PRAGMA table_info("{table_name}");')
        columns_info = cursor.fetchall()

        print("\n[Schema]")
        if not columns_info:
            print("  Could not retrieve schema information for this table.")
        else:
            print("  {:<25} {:<15}".format("Column Name", "Data Type"))
            print("  " + "-" * 42)
            for col in columns_info:
                col_name = col[1]
                col_type = col[2]
                print(f"  {col_name:<25} {col_type:<15}")

        print("\n[Data (first 50 rows)]")
        columns = [col[1] for col in columns_info]

        limit = 50
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit};')
        rows = cursor.fetchall()

        if not rows:
            print("  Table is empty.")
            input("\nPress Enter to return to the menu...")
            return

        col_widths = [len(col) for col in columns]
        for row in rows:
            for i, cell in enumerate(row):
                cell_len = len(str(cell))
                if cell_len > col_widths[i]:
                    col_widths[i] = cell_len

        header = " | ".join(columns[i].ljust(col_widths[i]) for i in range(len(columns)))
        print(header)
        print("-" * len(header))

        for row in rows:
            row_str = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
            print(row_str)

        if len(rows) == limit:
            print(f"\nNOTE: Displaying first {limit} rows.")

    except sqlite3.Error as e:
        print(f"An error occurred while fetching data: {e}")

    input("\nPress Enter to return to the menu...")


def interactive_viewer(db_file):
    if not os.path.exists(db_file):
        print(f"Error: File '{db_file}' not found.")
        return

    conn = None
    try:
        db_uri = f'file:{db_file}?mode=ro'
        conn = sqlite3.connect(db_uri, uri=True)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No tables found in this database.")
            return

        while True:
            print("\n" + "="*30)
            print("           SeeQLite")
            print("="*30)
            print(f"DATABASE: {os.path.basename(db_file)}\n")
            print("Tables:")
            for i, table_name in enumerate(tables):
                print(f"  {i + 1}: {table_name}")
            print("\n  q: Quit")

            choice = input("\nSelect a table to view by number, or 'q' to quit: ").strip().lower()

            if choice == 'q':
                print("Exiting.")
                break

            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(tables):
                    selected_table = tables[choice_index]
                    display_table_data(cursor, selected_table)
                else:
                    print("\n*** Invalid number. Please try again. ***")
            except ValueError:
                print("\n*** Invalid input. Please enter a number or 'q'. ***")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    database_file = sys.argv[1]
    interactive_viewer(database_file)


