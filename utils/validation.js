const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateVendor(row, rowIndex) {
  const errors = [];
  const required = ['id', 'name', 'type', 'category', 'gst_number', 'pan', 'bank_name', 'account_number', 'ifsc', 'contact_person', 'email', 'phone', 'compliance_expiry'];
  
  for (const field of required) {
    if (row[field] === undefined || row[field] === null || String(row[field]).trim() === '') {
      errors.push(`Row ${rowIndex}: Field "${field}" is required`);
    }
  }

  if (row.email && !emailRegex.test(String(row.email).trim())) {
    errors.push(`Row ${rowIndex}: Invalid email format "${row.email}"`);
  }

  const validTypes = ['material', 'service', 'amc', 'soft_services'];
  if (row.type && !validTypes.includes(String(row.type).trim())) {
    errors.push(`Row ${rowIndex}: Invalid type "${row.type}". Must be one of ${validTypes.join(', ')}`);
  }

  const validStatus = ['active', 'inactive', 'blacklisted'];
  if (row.status && !validStatus.includes(String(row.status).trim())) {
    errors.push(`Row ${rowIndex}: Invalid status "${row.status}". Must be one of ${validStatus.join(', ')}`);
  }

  return errors;
}

function validateItem(row, rowIndex) {
  const errors = [];
  const required = ['id', 'name', 'type', 'category', 'uom', 'unit_price'];

  for (const field of required) {
    if (row[field] === undefined || row[field] === null || String(row[field]).trim() === '') {
      errors.push(`Row ${rowIndex}: Field "${field}" is required`);
    }
  }

  const validTypes = ['spare', 'consumable', 'service'];
  if (row.type && !validTypes.includes(String(row.type).trim())) {
    errors.push(`Row ${rowIndex}: Invalid type "${row.type}". Must be one of ${validTypes.join(', ')}`);
  }

  if (row.unit_price && isNaN(Number(row.unit_price))) {
    errors.push(`Row ${rowIndex}: Unit price must be a valid number`);
  }

  return errors;
}

function validateBudget(row, rowIndex) {
  const errors = [];
  const required = ['id', 'fy', 'type', 'tower', 'department', 'category', 'gl_code', 'period', 'annual_budget', 'owner'];

  for (const field of required) {
    if (row[field] === undefined || row[field] === null || String(row[field]).trim() === '') {
      errors.push(`Row ${rowIndex}: Field "${field}" is required`);
    }
  }

  const validTypes = ['opex', 'capex'];
  if (row.type && !validTypes.includes(String(row.type).toLowerCase().trim())) {
    errors.push(`Row ${rowIndex}: Invalid type "${row.type}". Must be opex or capex`);
  }

  if (row.annual_budget && isNaN(Number(row.annual_budget))) {
    errors.push(`Row ${rowIndex}: Annual budget must be a valid number`);
  }

  return errors;
}

function validateStockLedger(row, rowIndex) {
  const errors = [];
  const required = ['id', 'current_stock'];

  for (const field of required) {
    if (row[field] === undefined || row[field] === null || String(row[field]).trim() === '') {
      errors.push(`Row ${rowIndex}: Field "${field}" is required`);
    }
  }

  if (row.current_stock && isNaN(Number(row.current_stock))) {
    errors.push(`Row ${rowIndex}: Current stock must be a valid integer`);
  }

  return errors;
}

function validateInvoice(row, rowIndex) {
  const errors = [];
  const required = ['id', 'vendor_id', 'vendor_name', 'invoice_number', 'invoice_date', 'po_id', 'amount', 'gst', 'total_amount', 'due_date'];

  for (const field of required) {
    if (row[field] === undefined || row[field] === null || String(row[field]).trim() === '') {
      errors.push(`Row ${rowIndex}: Field "${field}" is required`);
    }
  }

  if (row.total_amount && isNaN(Number(row.total_amount))) {
    errors.push(`Row ${rowIndex}: Total amount must be a number`);
  }

  return errors;
}

module.exports = {
  validateVendor,
  validateItem,
  validateBudget,
  validateStockLedger,
  validateInvoice,
};
