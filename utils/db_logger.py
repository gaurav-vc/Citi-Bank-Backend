from django.db import connection
import json

def log_export(module, filename, file_type, filters=None):
    if filters is None:
        filters = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO export_logs (module, filename, file_type, filters) VALUES (%s, %s, %s, %s)",
                [module, filename, file_type, json.dumps(filters)]
            )
    except Exception as e:
        print("Failed to log export:", e)

def log_import_start(module, filename, file_type, total_rows):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO import_logs (module, filename, file_type, status, total_rows) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                [module, filename, file_type, 'processing', total_rows]
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print("Failed to log import start:", e)
        return None

def log_import_failed_row(import_log_id, row_index, row_data, error_message):
    if not import_log_id:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO failed_import_rows (import_log_id, row_index, row_data, error_message) VALUES (%s, %s, %s, %s)",
                [import_log_id, row_index, json.dumps(row_data), error_message]
            )
    except Exception as e:
        print("Failed to log failed import row:", e)

def log_import_end(import_log_id, status, processed_rows, failed_rows):
    if not import_log_id:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE import_logs SET status = %s, processed_rows = %s, failed_rows = %s WHERE id = %s",
                [status, processed_rows, failed_rows, import_log_id]
            )
    except Exception as e:
        print("Failed to log import end:", e)
