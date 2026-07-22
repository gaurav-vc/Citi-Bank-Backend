const ExcelJS = require('exceljs');
const { Parser } = require('json2csv');
const PDFDocument = require('pdfkit');

async function exportExcel(data, columns, title = 'Report') {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet(title);
  worksheet.columns = columns.map(c => ({
    header: c.header,
    key: c.key,
    width: c.width || 20
  }));
  
  // Style headers
  worksheet.getRow(1).font = { bold: true };
  
  data.forEach(row => {
    worksheet.addRow(row);
  });
  
  return await workbook.xlsx.writeBuffer();
}

function exportCsv(data, fields) {
  const parser = new Parser({ fields });
  const csv = parser.parse(data);
  return Buffer.from(csv, 'utf8');
}

function exportPdf(data, columns, title = 'Report') {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({ margin: 30, size: 'A4' });
      const buffers = [];
      doc.on('data', buffers.push.bind(buffers));
      doc.on('end', () => resolve(Buffer.concat(buffers)));

      // Title
      doc.fontSize(18).text(title, { align: 'center' });
      doc.fontSize(10).text(`Generated on: ${new Date().toLocaleDateString()}`, { align: 'center' });
      doc.moveDown(2);

      const tableX = 30;
      const totalWidth = doc.page.width - 60;
      const colWidth = totalWidth / columns.length;

      // Draw Header Row
      let y = doc.y;
      columns.forEach((col, i) => {
        doc.font('Helvetica-Bold').text(col.header, tableX + i * colWidth, y, {
          width: colWidth - 5,
          align: 'left'
        });
      });
      
      doc.moveDown(0.5);
      doc.moveTo(tableX, doc.y).lineTo(tableX + totalWidth, doc.y).stroke();
      doc.moveDown(0.5);

      // Draw Data Rows
      data.forEach(row => {
        if (doc.y > doc.page.height - 60) {
          doc.addPage();
          y = doc.y;
          // Re-draw headers on new page
          columns.forEach((col, i) => {
            doc.font('Helvetica-Bold').text(col.header, tableX + i * colWidth, y, {
              width: colWidth - 5,
              align: 'left'
            });
          });
          doc.moveDown(0.5);
          doc.moveTo(tableX, doc.y).lineTo(tableX + totalWidth, doc.y).stroke();
          doc.moveDown(0.5);
        }
        
        y = doc.y;
        columns.forEach((col, i) => {
          let val = row[col.key];
          if (val === undefined || val === null) {
            val = '';
          } else if (typeof val === 'object') {
            val = JSON.stringify(val);
          } else {
            val = String(val);
          }
          
          doc.font('Helvetica').text(val, tableX + i * colWidth, y, {
            width: colWidth - 5,
            align: 'left'
          });
        });
        
        doc.moveDown(1.2);
      });

      doc.end();
    } catch (err) {
      reject(err);
    }
  });
}

module.exports = {
  exportExcel,
  exportCsv,
  exportPdf
};
