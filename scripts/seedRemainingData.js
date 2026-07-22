const db = require('../db');

const indents = [
  {
    id: 'IND-2024-001',
    type: 'material',
    tower: 'Tower A',
    floor: '5th Floor',
    category: 'Electrical',
    items: [
      { itemId: 'I001', itemName: 'LED Tube Light 20W', quantity: 25, uom: 'Nos', estimatedRate: 450 },
      { itemId: 'I006', itemName: 'Electrical MCB 32A', quantity: 10, uom: 'Nos', estimatedRate: 890 }
    ],
    estimated_cost: 20150,
    required_date: '2024-02-15',
    budget_head: 'opex',
    justification: 'Replacement of faulty lights and MCBs on 5th floor common area',
    attachments: ['scope_doc.pdf'],
    status: 'submitted',
    created_by: 'Rajesh Kumar',
    created_at: '2024-01-20',
    approvals: [
      { id: 'A1', stage: 'HOD Approval', approver: 'Deepak Joshi', approverRole: 'facility_manager', status: 'pending' }
    ]
  },
  {
    id: 'IND-2024-002',
    type: 'service',
    tower: 'Tower B',
    floor: '10th Floor',
    category: 'HVAC',
    items: [
      { itemId: 'I002', itemName: 'HVAC Filter 24x24x2', quantity: 15, uom: 'Nos', estimatedRate: 1200 }
    ],
    estimated_cost: 18000,
    required_date: '2024-02-10',
    budget_head: 'opex',
    justification: 'Quarterly HVAC filter replacement as per AMC schedule',
    attachments: [],
    status: 'hod_approved',
    created_by: 'Suresh Patel',
    created_at: '2024-01-18',
    approvals: [
      { id: 'A2', stage: 'HOD Approval', approver: 'Deepak Joshi', approverRole: 'facility_manager', status: 'approved', timestamp: '2024-01-19' },
      { id: 'A3', stage: 'Procurement Approval', approver: 'Amit Verma', approverRole: 'procurement_manager', status: 'pending' }
    ]
  },
  {
    id: 'IND-2024-003',
    type: 'material',
    tower: 'Tower C',
    floor: '3rd Floor',
    category: 'Plumbing',
    items: [
      { itemId: 'I004', itemName: 'PVC Pipe 4 inch', quantity: 20, uom: 'Mtr', estimatedRate: 320 }
    ],
    estimated_cost: 6400,
    required_date: '2024-02-08',
    budget_head: 'capex',
    justification: 'Emergency pipe replacement due to leakage in washroom area',
    attachments: ['damage_photos.pdf'],
    status: 'procurement_approved',
    created_by: 'Rajesh Kumar',
    created_at: '2024-01-15',
    approvals: [
      { id: 'A4', stage: 'HOD Approval', approver: 'Deepak Joshi', approverRole: 'facility_manager', status: 'approved', timestamp: '2024-01-16' },
      { id: 'A5', stage: 'Procurement Approval', approver: 'Amit Verma', approverRole: 'procurement_manager', status: 'approved', timestamp: '2024-01-17' }
    ]
  }
];

const grns = [
  {
    id: 'GRN-2024-001',
    po_id: 'PO-2024-001',
    received_date: '2024-01-10',
    received_by: 'Amit Patel',
    items: [
      { itemId: 'I001', itemName: 'LED Tube Light 20W', receivedQty: 60, uom: 'Nos' },
      { itemId: 'I006', itemName: 'Electrical MCB 32A', receivedQty: 50, uom: 'Nos' }
    ],
    status: 'received',
    invoice_status: 'pending'
  },
  {
    id: 'GRN-2024-002',
    po_id: 'PO-2024-002',
    received_date: '2024-01-12',
    received_by: 'Suresh Reddy',
    items: [
      { itemId: 'I002', itemName: 'HVAC Filter 24x24x2', receivedQty: 10, uom: 'Nos' }
    ],
    status: 'received',
    invoice_status: 'pending'
  }
];

const stockTransfers = [
  {
    id: 'TRF-001',
    from_location: 'Central Store',
    to_location: 'Tower A Store',
    items: [
      { itemId: 'I001', itemName: 'LED Tube Light 20W', quantity: 20, uom: 'Nos' },
      { itemId: 'I006', itemName: 'Electrical MCB 32A', quantity: 5, uom: 'Nos' }
    ],
    requested_by: 'Rajesh Kumar',
    requested_date: '2024-01-18',
    status: 'received',
    approved_by: 'Amit Patel',
    transfer_date: '2024-01-19'
  },
  {
    id: 'TRF-002',
    from_location: 'Tower B Store',
    to_location: 'Tower C Store',
    items: [
      { itemId: 'I003', itemName: 'Cleaning Chemical (Floor)', quantity: 50, uom: 'Ltr' }
    ],
    requested_by: 'Priya Sharma',
    requested_date: '2024-01-19',
    status: 'in_transit',
    approved_by: 'Amit Patel'
  },
  {
    id: 'TRF-003',
    from_location: 'Central Store',
    to_location: 'Tower B Store',
    items: [
      { itemId: 'I002', itemName: 'HVAC Filter 24x24x2', quantity: 10, uom: 'Nos' }
    ],
    requested_by: 'Suresh Reddy',
    requested_date: '2024-01-20',
    status: 'pending'
  },
  {
    id: 'TRF-004',
    from_location: 'Tower A Store',
    to_location: 'Central Store',
    items: [
      { itemId: 'I007', itemName: 'AC Compressor Belt', quantity: 100, uom: 'Nos' }
    ],
    requested_by: 'Meera Nair',
    requested_date: '2024-01-20',
    status: 'approved',
    approved_by: 'Amit Patel'
  }
];

const scrapDisposals = [
  {
    id: 'SCP-001',
    items: [
      { itemId: 'I007', itemName: 'Damaged HVAC Compressor', quantity: 1, uom: 'Nos' }
    ],
    total_value: 25000.00,
    disposal_date: '2024-01-20',
    buyer: 'Sold to scrap dealer',
    status: 'disposed',
    gate_pass_no: 'GP-2024-001'
  },
  {
    id: 'SCP-002',
    items: [
      { itemId: 'I008', itemName: 'Old Office Chairs', quantity: 15, uom: 'Nos' }
    ],
    total_value: 45000.00,
    disposal_date: '2024-01-22',
    buyer: 'Furniture Recyclers Ltd',
    status: 'approved',
    gate_pass_no: 'GP-2024-002'
  },
  {
    id: 'SCP-003',
    items: [
      { itemId: 'I005', itemName: 'Expired Fire Extinguishers', quantity: 10, uom: 'Nos' }
    ],
    total_value: 15000.00,
    disposal_date: '2024-01-25',
    buyer: 'Safety Disposal Corp',
    status: 'pending',
    gate_pass_no: null
  },
  {
    id: 'SCP-004',
    items: [
      { itemId: 'I001', itemName: 'Damaged LED Tube Lights', quantity: 25, uom: 'Nos' }
    ],
    total_value: 8750.00,
    disposal_date: '2024-01-21',
    buyer: 'E-waste recycler',
    status: 'disposed',
    gate_pass_no: 'GP-2024-003'
  }
];

const materialIssues = [
  {
    id: 'ISS-001',
    issued_date: '2024-01-18',
    issued_to: 'Rajesh Kumar',
    department: 'Maintenance',
    tower: 'Tower A',
    floor: '5th Floor',
    workOrderRef: 'WO-001',
    items: [
      { itemId: 'I001', itemName: 'LED Tube Light 20W', issuedQty: 10, returnedQty: 2, uom: 'Nos' },
      { itemId: 'I006', itemName: 'Electrical MCB 32A', issuedQty: 2, returnedQty: 0, uom: 'Nos' }
    ],
    status: 'partially_returned',
    issuedBy: 'Amit Patel',
    purpose: 'Lighting replacement in common area'
  },
  {
    id: 'ISS-002',
    issued_date: '2024-01-19',
    issued_to: 'Priya Sharma',
    department: 'Housekeeping',
    tower: 'Tower B',
    floor: 'All Floors',
    items: [
      { itemId: 'I003', itemName: 'Cleaning Chemical (Floor)', issuedQty: 20, returnedQty: 0, uom: 'Ltr' },
      { itemId: 'I004', itemName: 'PVC Pipe 4 inch', issuedQty: 10, returnedQty: 0, uom: 'Ltr' }
    ],
    status: 'issued',
    issuedBy: 'Suresh Reddy',
    purpose: 'Weekly cleaning supplies'
  },
  {
    id: 'ISS-003',
    issued_date: '2024-01-17',
    issued_to: 'Suresh Reddy',
    department: 'HVAC',
    tower: 'Tower C',
    floor: '12th Floor',
    workOrderRef: 'WO-003',
    items: [
      { itemId: 'I002', itemName: 'HVAC Filter 24x24x2', issuedQty: 4, returnedQty: 4, uom: 'Nos' }
    ],
    status: 'fully_returned',
    issuedBy: 'Amit Patel',
    purpose: 'Filter replacement - unused filters returned'
  },
  {
    id: 'ISS-004',
    issued_date: '2024-01-20',
    issued_to: 'Meera Nair',
    department: 'Security',
    tower: 'All Towers',
    floor: 'Ground Floor',
    items: [
      { itemId: 'I005', itemName: 'Batteries AA', issuedQty: 50, returnedQty: 0, uom: 'Nos' }
    ],
    status: 'issued',
    issuedBy: 'Amit Patel',
    purpose: 'Torch and remote batteries replacement'
  }
];

const expenses = [
  {
    id: 'EXP-001',
    category: 'Maintenance',
    amount: 15000.00,
    date: '2024-01-15',
    payment_mode: 'Cash',
    status: 'approved',
    description: 'Emergency plumbing repair in basement parking',
    approved_by: 'Vikram Singh'
  },
  {
    id: 'EXP-002',
    category: 'Security',
    amount: 45000.00,
    date: '2024-01-16',
    payment_mode: 'Bank Transfer',
    status: 'submitted',
    description: 'Replacement of 3 damaged CCTV cameras at entry points',
    approved_by: null
  },
  {
    id: 'EXP-003',
    category: 'Soft Services',
    amount: 8500.00,
    date: '2024-01-17',
    payment_mode: 'Cash',
    status: 'rejected',
    description: 'Purchase of landscaping plants and fertilizers',
    approved_by: 'Vikram Singh'
  },
  {
    id: 'EXP-004',
    category: 'Electrical',
    amount: 32000.00,
    date: '2024-01-18',
    payment_mode: 'Credit Card',
    status: 'paid',
    description: 'Main panel repair and component replacement',
    approved_by: 'Vikram Singh'
  },
  {
    id: 'EXP-005',
    category: 'HVAC',
    amount: 18000.00,
    date: '2024-01-19',
    payment_mode: 'Bank Transfer',
    status: 'draft',
    description: 'Quarterly filter replacement for AHUs',
    approved_by: null
  }
];

async function seed() {
  console.log('Truncating tables to clear previous partial seed...');
  try {
    await db.query('TRUNCATE TABLE expenses, material_issues, scrap_disposals, stock_transfers, grns, indents, stock_ledger CASCADE');
  } catch (err) {
    console.warn('Truncate warning:', err.message);
  }

  console.log('Seeding remaining mock data...');
  try {
    // 1. Indents
    for (const ind of indents) {
      await db.query(
        `INSERT INTO indents (id, type, tower, floor, category, items, estimated_cost, required_date, budget_head, justification, attachments, status, created_by, approvals, approval_level, workflow_history, inventory_status, requisition_type, priority)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 0, '[]', 'pending', 'regular', 'medium')
         ON CONFLICT (id) DO NOTHING`,
        [ind.id, ind.type, ind.tower, ind.floor, ind.category, JSON.stringify(ind.items), ind.estimated_cost, ind.required_date, ind.budget_head, ind.justification, JSON.stringify(ind.attachments), ind.status, ind.created_by, JSON.stringify(ind.approvals)]
      );
    }
    console.log('Indents seeded.');

    // 2. GRNs
    for (const g of grns) {
      await db.query(
        `INSERT INTO grns (id, po_id, received_date, received_by, items, status, invoice_status, invoice_number, vendor_name, remarks)
         VALUES ($1, $2, $3, $4, $5, $6, $7, '', '', '')
         ON CONFLICT (id) DO NOTHING`,
        [g.id, g.po_id, g.received_date, g.received_by, JSON.stringify(g.items), g.status, g.invoice_status]
      );

      // Create StockLedger entries for seeded GRN items
      for (const item of g.items) {
        const ledgerId = `SL-SEED-${g.id}-${item.itemId}`;
        const qty = item.receivedQty || item.received_qty || 0;
        await db.query(
          `INSERT INTO stock_ledger (id, transaction_type, source_type, source_id, item_id, quantity, stock_before, stock_after, remarks, reason, timestamp)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
           ON CONFLICT (id) DO NOTHING`,
          [ledgerId, 'GRN_RECEIPT', 'GRN', g.id, item.itemId, qty, 0, qty, `Received via GRN ${g.id}`, 'GRN Entry', g.received_date]
        );
      }
    }
    console.log('GRNs and ledger entries seeded.');

    // 3. Stock Transfers
    for (const st of stockTransfers) {
      await db.query(
        `INSERT INTO stock_transfers (id, from_location, to_location, items, requested_by, requested_date, status, approved_by, transfer_date)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         ON CONFLICT (id) DO NOTHING`,
        [st.id, st.from_location, st.to_location, JSON.stringify(st.items), st.requested_by, st.requested_date, st.status, st.approved_by || null, st.transfer_date || null]
      );
    }
    console.log('Stock Transfers seeded.');

    // 5. Material Issues
    for (const mi of materialIssues) {
      await db.query(
        `INSERT INTO material_issues (id, items, issued_to, issued_date, tower, floor, purpose, status, department, work_order_ref, issued_by)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
         ON CONFLICT (id) DO NOTHING`,
        [mi.id, JSON.stringify(mi.items), mi.issued_to, mi.issued_date, mi.tower, mi.floor, mi.purpose, mi.status, mi.department, mi.workOrderRef, mi.issuedBy]
      );

      // Create StockLedger entries for seeded Material Issues
      for (const item of mi.items) {
        const ledgerId = `SL-SEED-${mi.id}-${item.itemId}`;
        const qty = item.issuedQty || item.issued_qty || 0;
        await db.query(
          `INSERT INTO stock_ledger (id, transaction_type, source_type, source_id, item_id, quantity, stock_before, stock_after, remarks, reason, timestamp)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
           ON CONFLICT (id) DO NOTHING`,
          [ledgerId, 'GOODS_ISSUE', 'GDN', mi.id, item.itemId, qty, 0, 0, `Issued for: ${mi.purpose}`, 'Material Issue', mi.issued_date]
        );
      }
    }
    console.log('Material Issues and ledger entries seeded.');

    // 4. Scrap Disposals
    for (const sd of scrapDisposals) {
      await db.query(
        `INSERT INTO scrap_disposals (id, items, total_value, disposal_date, buyer, status, gate_pass_no, recovered_value)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
         ON CONFLICT (id) DO NOTHING`,
        [sd.id, JSON.stringify(sd.items), sd.total_value, sd.disposal_date, sd.buyer, sd.status, sd.gate_pass_no, sd.recovered_value || 0.00]
      );
    }
    console.log('Scrap Disposals seeded.');

    // 6. Expenses
    for (const e of expenses) {
      await db.query(
        `INSERT INTO expenses (id, category, amount, date, payment_mode, status, description, approved_by, approval_level, workflow_history)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 0, '[]')
         ON CONFLICT (id) DO NOTHING`,
        [e.id, e.category, e.amount, e.date, e.payment_mode, e.status, e.description, e.approved_by]
      );
    }
    console.log('Expenses seeded.');

    console.log('Remaining seed data populated successfully.');

    // Automatically execute the Django inventory reconciliation --fix command
    const { execSync } = require('child_process');
    console.log('Running inventory reconciliation fix...');
    try {
      execSync('backend\\.venv\\Scripts\\python backend\\manage.py reconcile_inventory --fix', {
        input: 'yes\n',
        cwd: require('path').join(__dirname, '../..'),
        stdio: 'inherit'
      });
      console.log('Inventory reconciled successfully.');
    } catch (e) {
      console.warn('Reconciliation failed during seeding:', e.message);
    }

    process.exit(0);
  } catch (err) {
    console.error('Seeding remaining failed:', err);
    process.exit(1);
  }
}

seed();
