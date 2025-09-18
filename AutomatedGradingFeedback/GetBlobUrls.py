import pyodbc
import os

def get_blob_urls_for_folder(StudyFiles: str, AssignmentFiles: str):
    # Fetch values from env
    server = os.getenv('SERVER')
    username = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')
    database = os.getenv('DATABASE')

    # Establishing Connection with SQL Server
    connection = pyodbc.connect(
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};Database={database};UID={username};PWD={password};"
    )
    cursor = connection.cursor()

    query = os.getenv("SQL_QUERY_STUDYMATERIAL")
    query2 = os.getenv("SQL_QUERY_ASSIGNMENTS")

    # Executing first query (StudyFiles)
    cursor.execute(query, (StudyFiles,))
    study_results = [row[0] for row in cursor.fetchall()]

    # Executing second query (AssignmentFiles)
    cursor.execute(query2, (AssignmentFiles,))
    assignment_results = [row[0] for row in cursor.fetchall()]

    # Close connection
    cursor.close()
    connection.close()

    return study_results, assignment_results
