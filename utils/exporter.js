const xlsx = require('xlsx');

function exportToCsv(data) {
  const worksheet = xlsx.utils.json_to_sheet(data);
  const csvString = xlsx.utils.sheet_to_csv(worksheet);
  return Buffer.from(csvString, 'utf8');
}

function exportToXlsx(data) {
  const worksheet = xlsx.utils.json_to_sheet(data);
  const workbook = xlsx.utils.book_new();
  xlsx.utils.book_append_sheet(workbook, worksheet, 'Data');
  return xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });
}

function exportData(data, format = 'xlsx') {
  const fmt = format.toLowerCase();
  if (fmt === 'csv') {
    return {
      buffer: exportToCsv(data),
      mimetype: 'text/csv',
      extension: 'csv',
    };
  } else {
    return {
      buffer: exportToXlsx(data),
      mimetype: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      extension: 'xlsx',
    };
  }
}

module.exports = {
  exportData,
};
