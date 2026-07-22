import io
import csv
from openpyxl import Workbook

def export_to_csv(data, columns):
    """
    data: list of dicts or objects
    columns: list of dicts like [{"header": "ColName", "key": "col_key"}] or list of string keys
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    if not columns:
        if data and isinstance(data[0], dict):
            columns = list(data[0].keys())
        else:
            columns = []

    if columns and isinstance(columns[0], dict):
        headers = [col.get('header', col.get('key')) for col in columns]
        keys = [col.get('key') for col in columns]
    else:
        headers = columns
        keys = columns

    writer.writerow(headers)
    
    for row in data:
        if isinstance(row, dict):
            writer.writerow([row.get(k, '') for k in keys])
        elif hasattr(row, '__dict__'):
            writer.writerow([getattr(row, k, '') for k in keys])
        else:
            writer.writerow(row)
            
    return output.getvalue().encode('utf-8')

def export_to_excel(data, columns, sheet_name="Data"):
    """
    data: list of dicts or objects
    columns: list of dicts like [{"header": "ColName", "key": "col_key"}] or list of string keys
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:30]
    
    if not columns:
        if data and isinstance(data[0], dict):
            columns = list(data[0].keys())
        else:
            columns = []

    if columns and isinstance(columns[0], dict):
        headers = [col.get('header', col.get('key')) for col in columns]
        keys = [col.get('key') for col in columns]
    else:
        headers = columns
        keys = columns

    ws.append(headers)
    
    for row in data:
        row_data = []
        for k in keys:
            val = ''
            if isinstance(row, dict):
                val = row.get(k, '')
            elif hasattr(row, '__dict__'):
                val = getattr(row, k, '')
            row_data.append(val)
        ws.append(row_data)
        
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def export_data(data, columns, format='xlsx', sheet_name="Data"):
    fmt = format.lower()
    if fmt == 'csv':
        return {
            'buffer': export_to_csv(data, columns),
            'mimetype': 'text/csv',
            'extension': 'csv'
        }
    else:
        return {
            'buffer': export_to_excel(data, columns, sheet_name),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'extension': 'xlsx'
        }
