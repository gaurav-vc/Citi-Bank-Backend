const xlsx = require('xlsx');
const csv = require('csv-parser');
const { Readable } = require('stream');

function parseXlsx(buffer) {
  const workbook = xlsx.read(buffer, { type: 'buffer' });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  return xlsx.utils.sheet_to_json(sheet);
}

function parseCsv(buffer) {
  return new Promise((resolve, reject) => {
    const results = [];
    // Handle both UTF-8 and other common string encodings safely
    const stream = Readable.from(buffer.toString('utf8'));
    stream
      .pipe(csv({
        mapHeaders: ({ header }) => header.trim()
      }))
      .on('data', (data) => results.push(data))
      .on('end', () => resolve(results))
      .on('error', (err) => reject(err));
  });
}

async function parseUploadedFile(file) {
  if (!file || !file.buffer) {
    throw new Error('No file data provided');
  }
  const ext = file.originalname.split('.').pop().toLowerCase();
  if (ext === 'csv' || file.mimetype === 'text/csv') {
    return await parseCsv(file.buffer);
  } else if (ext === 'xlsx' || file.mimetype === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
    return parseXlsx(file.buffer);
  } else {
    throw new Error('Unsupported file type. Only CSV and XLSX are supported.');
  }
}

module.exports = {
  parseUploadedFile,
};
