require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const db = require('../db');

const vendors = [
  {
    id: 'V001',
    name: 'ABC Facilities Pvt Ltd',
    type: 'soft_services',
    category: 'Housekeeping',
    gstNumber: '27AABCU9603R1ZM',
    pan: 'AABCU9603R',
    msmeStatus: true,
    bankDetails: { bankName: 'HDFC Bank', accountNumber: '50200012345678', ifsc: 'HDFC0001234' },
    slaRating: 4.5,
    approvedTowers: ['Tower A', 'Tower B', 'Tower C'],
    complianceExpiry: '2025-12-31',
    status: 'active',
    contactPerson: 'Mahesh Sharma',
    email: 'mahesh@abcfacilities.com',
    phone: '+91 98765 43210',
  },
  {
    id: 'V002',
    name: 'TechCool HVAC Solutions',
    type: 'amc',
    category: 'HVAC',
    gstNumber: '27AAACT2727Q1Z5',
    pan: 'AAACT2727Q',
    msmeStatus: false,
    bankDetails: { bankName: 'ICICI Bank', accountNumber: '087405000123', ifsc: 'ICIC0000874' },
    slaRating: 4.2,
    approvedTowers: ['Tower A', 'Tower B'],
    complianceExpiry: '2025-06-30',
    status: 'active',
    contactPerson: 'Rakesh Patel',
    email: 'rakesh@techcool.com',
    phone: '+91 98123 45678',
  },
  {
    id: 'V003',
    name: 'ElectroPower Systems',
    type: 'service',
    category: 'Electrical',
    gstNumber: '27AABCE3456P1ZK',
    pan: 'AABCE3456P',
    msmeStatus: true,
    bankDetails: { bankName: 'SBI', accountNumber: '39876543210', ifsc: 'SBIN0001234' },
    slaRating: 4.8,
    approvedTowers: ['Tower A', 'Tower B', 'Tower C'],
    complianceExpiry: '2025-09-15',
    status: 'active',
    contactPerson: 'Sunil Kumar',
    email: 'sunil@electropower.com',
    phone: '+91 99887 76655',
  },
  {
    id: 'V004',
    name: 'PlumbMaster Services',
    type: 'service',
    category: 'Plumbing',
    gstNumber: '27AABCP7890Q1ZL',
    pan: 'AABCP7890Q',
    msmeStatus: true,
    bankDetails: { bankName: 'Axis Bank', accountNumber: '917020043210123', ifsc: 'UTIB0001234' },
    slaRating: 3.9,
    approvedTowers: ['Tower B', 'Tower C'],
    complianceExpiry: '2025-03-31',
    status: 'active',
    contactPerson: 'Ravi Verma',
    email: 'ravi@plumbmaster.com',
    phone: '+91 98765 12345',
  },
  {
    id: 'V005',
    name: 'SecureGuard Services',
    type: 'soft_services',
    category: 'Security',
    gstNumber: '27AABCS1234R1ZN',
    pan: 'AABCS1234R',
    msmeStatus: false,
    bankDetails: { bankName: 'Kotak Mahindra', accountNumber: '8712345678901', ifsc: 'KKBK0001234' },
    slaRating: 4.6,
    approvedTowers: ['Tower A', 'Tower B', 'Tower C'],
    complianceExpiry: '2025-11-30',
    status: 'active',
    contactPerson: 'Vijay Singh',
    email: 'vijay@secureguard.com',
    phone: '+91 99001 23456',
  },
  {
    id: 'V006',
    name: 'GreenScape Landscaping',
    type: 'amc',
    category: 'Landscaping',
    gstNumber: '27AABCG5678S1ZP',
    pan: 'AABCG5678S',
    msmeStatus: true,
    bankDetails: { bankName: 'Yes Bank', accountNumber: '001234567890123', ifsc: 'YESB0001234' },
    slaRating: 4.3,
    approvedTowers: ['Tower A', 'Tower B', 'Tower C'],
    complianceExpiry: '2025-08-15',
    status: 'active',
    contactPerson: 'Arjun Patel',
    email: 'arjun@greenscape.com',
    phone: '+91 98234 56789',
  },
  {
    id: 'V007',
    name: 'SparesPro Trading',
    type: 'material',
    category: 'MEP Spares',
    gstNumber: '27AABCT9012U1ZQ',
    pan: 'AABCT9012U',
    msmeStatus: true,
    bankDetails: { bankName: 'Punjab National Bank', accountNumber: '0123456789012', ifsc: 'PUNB0001234' },
    slaRating: 4.0,
    approvedTowers: ['Tower A', 'Tower B', 'Tower C'],
    complianceExpiry: '2025-07-20',
    status: 'active',
    contactPerson: 'Dinesh Gupta',
    email: 'dinesh@sparespro.com',
    phone: '+91 97654 32109',
  },
];

const items = [
  { id: 'I001', name: 'LED Tube Light 20W', type: 'spare', category: 'Electrical', uom: 'Nos', minStockLevel: 50, reorderLevel: 100, currentStock: 75, preferredVendor: 'V003', unitPrice: 450 },
  { id: 'I002', name: 'HVAC Filter 24x24x2', type: 'spare', category: 'HVAC', uom: 'Nos', minStockLevel: 20, reorderLevel: 40, currentStock: 25, preferredVendor: 'V002', unitPrice: 1200 },
  { id: 'I003', name: 'Cleaning Chemical (Floor)', type: 'consumable', category: 'Housekeeping', uom: 'Ltr', minStockLevel: 100, reorderLevel: 200, currentStock: 150, preferredVendor: 'V001', unitPrice: 85 },
  { id: 'I004', name: 'PVC Pipe 4 inch', type: 'spare', category: 'Plumbing', uom: 'Mtr', minStockLevel: 30, reorderLevel: 60, currentStock: 45, preferredVendor: 'V004', unitPrice: 320 },
  { id: 'I005', name: 'Disinfectant Spray', type: 'consumable', category: 'Housekeeping', uom: 'Ltr', minStockLevel: 50, reorderLevel: 100, currentStock: 180, preferredVendor: 'V001', unitPrice: 250 },
  { id: 'I006', name: 'Electrical MCB 32A', type: 'spare', category: 'Electrical', uom: 'Nos', minStockLevel: 25, reorderLevel: 50, currentStock: 30, preferredVendor: 'V003', unitPrice: 890 },
  { id: 'I007', name: 'AC Compressor Belt', type: 'spare', category: 'HVAC', uom: 'Nos', minStockLevel: 10, reorderLevel: 20, currentStock: 8, preferredVendor: 'V002', unitPrice: 2500 },
  { id: 'I008', name: 'Fire Extinguisher Refill', type: 'service', category: 'Safety', uom: 'Nos', minStockLevel: 0, reorderLevel: 0, currentStock: 0, preferredVendor: 'V005', unitPrice: 1500 },
];

const budgets = [
  { id: 'BUD-001', fy: 'FY 2025-26', type: 'opex', tower: 'Tower A', department: 'Engineering', category: 'HVAC', glCode: '5002-AMC', period: 'annual', annualBudget: 4800000, allocated: 4800000, committed: 3200000, actual: 2950000, owner: 'Deepak Joshi', status: 'approved' },
  { id: 'BUD-002', fy: 'FY 2025-26', type: 'opex', tower: 'Tower A', department: 'Engineering', category: 'Electrical', glCode: '5001-RM', period: 'annual', annualBudget: 2400000, allocated: 2400000, committed: 1850000, actual: 1620000, owner: 'Rajesh Kumar', status: 'approved' },
  { id: 'BUD-003', fy: 'FY 2025-26', type: 'opex', tower: 'Tower B', department: 'Soft Services', category: 'Housekeeping', glCode: '5004-SOFT', period: 'annual', annualBudget: 6000000, allocated: 6000000, committed: 4100000, actual: 3900000, owner: 'Priya Sharma', status: 'approved' },
  { id: 'BUD-004', fy: 'FY 2025-26', type: 'opex', tower: 'Tower B', department: 'Security', category: 'Security', glCode: '5005-SEC', period: 'annual', annualBudget: 3600000, allocated: 3600000, committed: 2700000, actual: 2600000, owner: 'Amit Verma', status: 'approved' },
  { id: 'BUD-005', fy: 'FY 2025-26', type: 'opex', tower: 'Tower C', department: 'Facilities', category: 'Consumables', glCode: '5003-CONSUM', period: 'annual', annualBudget: 1500000, allocated: 1500000, committed: 1480000, actual: 1460000, owner: 'Suresh Patel', status: 'revised', notes: 'Cost overrun – approved revision' },
  { id: 'BUD-006', fy: 'FY 2025-26', type: 'capex', tower: 'Common Area', department: 'Projects', category: 'Project Works', glCode: '6001-CAPEX-CIVIL', period: 'annual', annualBudget: 15000000, allocated: 12000000, committed: 8500000, actual: 6200000, owner: 'Sandeep Mehta', status: 'approved' },
  { id: 'BUD-007', fy: 'FY 2025-26', type: 'capex', tower: 'Tower A', department: 'Projects', category: 'Project Works', glCode: '6002-CAPEX-MEP', period: 'annual', annualBudget: 9000000, allocated: 9000000, committed: 4200000, actual: 3100000, owner: 'Sandeep Mehta', status: 'approved' },
  { id: 'BUD-008', fy: 'FY 2025-26', type: 'opex', tower: 'Tower C', department: 'Engineering', category: 'Spares', glCode: '5001-RM', period: 'annual', annualBudget: 1200000, allocated: 1200000, committed: 760000, actual: 690000, owner: 'Rajesh Kumar', status: 'submitted' },
  { id: 'BUD-009', fy: 'FY 2026-27', type: 'opex', tower: 'Tower A', department: 'Engineering', category: 'HVAC', glCode: '5002-AMC', period: 'annual', annualBudget: 5200000, allocated: 0, committed: 0, actual: 0, owner: 'Deepak Joshi', status: 'draft' },
];

// 8 POs with varied categories, towers, statuses, and dates spread across last 6 months
// net_value sum = 100300 + 531000 + 218300 + 185000 + 95000 + 125000 + 78000 + 65000 = 1,397,600
const purchaseOrders = [
  {
    id: 'PO-2024-001',
    type: 'po',
    vendor: 'V003',
    vendorName: 'ElectroPower Systems',
    linkedRfq: 'RFQ-2024-001',
    items: [
      { id: 'POI1', itemName: 'LED Tube Light 20W', quantity: 100, uom: 'Nos', rate: 425, amount: 42500, deliveredQty: 60, balanceQty: 40 },
      { id: 'POI2', itemName: 'Electrical MCB 32A', quantity: 50, uom: 'Nos', rate: 850, amount: 42500, deliveredQty: 50, balanceQty: 0 },
    ],
    totalValue: 85000,
    taxes: 15300,
    netValue: 100300,
    retentionPercent: 5,
    startDate: '2026-01-15',
    endDate: '2026-03-31',
    status: 'active',
    tower: 'Tower A',
    category: 'Electrical',
  },
  {
    id: 'PO-2024-002',
    type: 'amc',
    vendor: 'V002',
    vendorName: 'TechCool HVAC Solutions',
    items: [
      { id: 'POI3', itemName: 'Annual HVAC Maintenance', quantity: 1, uom: 'Contract', rate: 450000, amount: 450000, deliveredQty: 0, balanceQty: 1 },
    ],
    totalValue: 450000,
    taxes: 81000,
    netValue: 531000,
    retentionPercent: 10,
    milestones: [
      { id: 'M1', name: 'Q1 Service', dueDate: '2026-03-31', percentage: 25, status: 'completed' },
      { id: 'M2', name: 'Q2 Service', dueDate: '2026-06-30', percentage: 25, status: 'pending' },
    ],
    startDate: '2026-02-01',
    endDate: '2026-12-31',
    status: 'active',
    tower: 'Tower B',
    category: 'HVAC',
  },
  {
    id: 'WO-2024-001',
    type: 'wo',
    vendor: 'V004',
    vendorName: 'PlumbMaster Services',
    linkedRfq: 'RFQ-2024-002',
    items: [
      { id: 'POI4', itemName: 'Washroom Renovation Work', quantity: 1, uom: 'Job', rate: 185000, amount: 185000, deliveredQty: 0, balanceQty: 1 },
    ],
    totalValue: 185000,
    taxes: 33300,
    netValue: 218300,
    retentionPercent: 10,
    milestones: [
      { id: 'M5', name: 'Demolition', dueDate: '2026-02-05', percentage: 20, status: 'completed' },
      { id: 'M6', name: 'Plumbing Work', dueDate: '2026-02-15', percentage: 40, status: 'pending' },
      { id: 'M7', name: 'Finishing', dueDate: '2026-02-25', percentage: 40, status: 'pending' },
    ],
    startDate: '2026-03-10',
    endDate: '2026-04-28',
    status: 'completed',
    tower: 'Tower C',
    category: 'Housekeeping',
  },
  {
    id: 'PO-2024-003',
    type: 'po',
    vendor: 'V005',
    vendorName: 'SecureGuard Services',
    items: [
      { id: 'POI5', itemName: 'Security System Upgrade', quantity: 1, uom: 'Job', rate: 185000, amount: 185000, deliveredQty: 0, balanceQty: 1 },
    ],
    totalValue: 157000,
    taxes: 28000,
    netValue: 185000,
    retentionPercent: 5,
    startDate: '2026-04-01',
    endDate: '2026-06-30',
    status: 'active',
    tower: 'Tower A',
    category: 'Security',
  },
  {
    id: 'PO-2024-004',
    type: 'po',
    vendor: 'V001',
    vendorName: 'ABC Facilities Pvt Ltd',
    items: [
      { id: 'POI6', itemName: 'Deep Cleaning Supplies', quantity: 200, uom: 'Ltr', rate: 400, amount: 80000, deliveredQty: 100, balanceQty: 100 },
    ],
    totalValue: 80000,
    taxes: 15000,
    netValue: 95000,
    retentionPercent: 5,
    startDate: '2025-12-15',
    endDate: '2026-02-15',
    status: 'completed',
    tower: 'Tower B',
    category: 'Housekeeping',
  },
  {
    id: 'PO-2024-005',
    type: 'po',
    vendor: 'V002',
    vendorName: 'TechCool HVAC Solutions',
    items: [
      { id: 'POI7', itemName: 'HVAC Filter Replacement', quantity: 50, uom: 'Nos', rate: 2100, amount: 105000, deliveredQty: 50, balanceQty: 0 },
    ],
    totalValue: 105000,
    taxes: 20000,
    netValue: 125000,
    retentionPercent: 5,
    startDate: '2026-05-01',
    endDate: '2026-07-31',
    status: 'pending',
    tower: 'Tower C',
    category: 'HVAC',
  },
  {
    id: 'PO-2024-006',
    type: 'po',
    vendor: 'V003',
    vendorName: 'ElectroPower Systems',
    items: [
      { id: 'POI8', itemName: 'Panel Board Maintenance', quantity: 1, uom: 'Job', rate: 66000, amount: 66000, deliveredQty: 0, balanceQty: 1 },
    ],
    totalValue: 66000,
    taxes: 12000,
    netValue: 78000,
    retentionPercent: 5,
    startDate: '2026-06-01',
    endDate: '2026-08-31',
    status: 'pending',
    tower: 'Tower A',
    category: 'Electrical',
  },
  {
    id: 'PO-2024-007',
    type: 'po',
    vendor: 'V006',
    vendorName: 'GreenScape Landscaping',
    items: [
      { id: 'POI9', itemName: 'Landscape Maintenance Q2', quantity: 1, uom: 'Contract', rate: 55000, amount: 55000, deliveredQty: 0, balanceQty: 1 },
    ],
    totalValue: 55000,
    taxes: 10000,
    netValue: 65000,
    retentionPercent: 5,
    startDate: '2026-03-15',
    endDate: '2026-06-15',
    status: 'active',
    tower: 'Tower B',
    category: 'Others',
  },
];

const invoices = [
  {
    id: 'INV-2024-001',
    vendorId: 'V003',
    vendorName: 'ElectroPower Systems',
    invoiceNumber: 'EPS/2024/0125',
    invoiceDate: '2026-01-25',
    poId: 'PO-2024-001',
    amount: 125000,
    gst: 22500,
    totalAmount: 147500,
    dueDate: '2026-02-10',
    status: 'pending',
    matchingStatus: '2way',
    attachments: ['invoice_eps_jan.pdf'],
  },
  {
    id: 'INV-2024-002',
    vendorId: 'V002',
    vendorName: 'TechCool HVAC Solutions',
    invoiceNumber: 'TC/2024/Q1-001',
    invoiceDate: '2026-01-28',
    poId: 'PO-2024-002',
    amount: 112500,
    gst: 20250,
    totalAmount: 132750,
    dueDate: '2026-02-15',
    status: 'pending',
    matchingStatus: '3way',
    attachments: ['invoice_tc_q1.pdf'],
  },
  {
    id: 'INV-2024-003',
    vendorId: 'V003',
    vendorName: 'ElectroPower Systems',
    invoiceNumber: 'EPS/2024/001',
    invoiceDate: '2026-01-20',
    poId: 'PO-2024-001',
    grnId: 'GRN-2024-001',
    amount: 48575,
    gst: 8743.5,
    totalAmount: 57318.5,
    dueDate: '2026-02-05',
    status: 'pending',
    matchingStatus: '3way',
    attachments: ['invoice_eps_jan2.pdf'],
  },
  {
    id: 'INV-2024-004',
    vendorId: 'V005',
    vendorName: 'SecureGuard Services',
    invoiceNumber: 'SG/2024/002',
    invoiceDate: '2026-04-15',
    poId: 'PO-2024-003',
    amount: 92500,
    gst: 16650,
    totalAmount: 109150,
    dueDate: '2026-05-01',
    status: 'verified',
    matchingStatus: '2way',
    attachments: ['invoice_sg_apr.pdf'],
  },
];

const rfqs = [
  {
    id: 'RFQ-001',
    title: 'HVAC Annual Maintenance Contract',
    category: 'HVAC',
    tower: 'All Towers',
    linkedPr: 'PR-2024-001',
    estimatedValue: 1500000,
    bidDueDate: '2024-02-01',
    status: 'evaluation',
    createdBy: 'Procurement Team',
    createdDate: '2024-01-10',
    vendors: [
      { vendorId: 'V001', vendorName: 'CoolAir Solutions', quoteAmount: 1400000, technicalScore: 92, commercialScore: 88, overallScore: 90, deliveryDays: 30, submitted: true, submittedDate: '2024-01-28', recommendation: 'recommended' },
      { vendorId: 'V002', vendorName: 'TempControl Inc', quoteAmount: 1350000, technicalScore: 78, commercialScore: 95, overallScore: 85, deliveryDays: 45, submitted: true, submittedDate: '2024-01-29', recommendation: 'acceptable' },
      { vendorId: 'V003', vendorName: 'AirFlow Masters', quoteAmount: 1600000, technicalScore: 95, commercialScore: 72, overallScore: 85, deliveryDays: 25, submitted: true, submittedDate: '2024-01-30', recommendation: 'acceptable' },
    ]
  },
  {
    id: 'RFQ-002',
    title: 'Security Services - Tower B',
    category: 'Security',
    tower: 'Tower B',
    linkedPr: 'PR-2024-002',
    estimatedValue: 800000,
    bidDueDate: '2024-02-05',
    status: 'bidding',
    createdBy: 'Procurement Team',
    createdDate: '2024-01-15',
    vendors: [
      { vendorId: 'V004', vendorName: 'SecureGuard Services', quoteAmount: 0, technicalScore: 0, commercialScore: 0, overallScore: 0, deliveryDays: 0, submitted: false, recommendation: 'acceptable' },
      { vendorId: 'V005', vendorName: 'SafeZone Security', quoteAmount: 750000, technicalScore: 0, commercialScore: 0, overallScore: 0, deliveryDays: 15, submitted: true, submittedDate: '2024-01-30', recommendation: 'acceptable' },
    ]
  },
  {
    id: 'RFQ-003',
    title: 'Electrical Panel Upgrade',
    category: 'Electrical',
    tower: 'Tower A',
    linkedPr: 'PR-2024-003',
    estimatedValue: 2500000,
    bidDueDate: '2024-02-10',
    status: 'published',
    createdBy: 'Procurement Team',
    createdDate: '2024-01-20',
    vendors: [
      { vendorId: 'V007', vendorName: 'PowerGrid Solutions', quoteAmount: 0, technicalScore: 0, commercialScore: 0, overallScore: 0, deliveryDays: 0, submitted: false, recommendation: 'acceptable' },
    ]
  },
];

const contracts = [
  {
    id: 'RC-001',
    vendor: 'CoolAir Solutions',
    vendorId: 'V002',
    type: 'amc',
    serviceScope: 'HVAC Systems Maintenance - All Towers',
    category: 'HVAC',
    contractValue: 1800000,
    billingCycle: 'quarterly',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    slaKpis: ['Response Time: 4 hrs', 'Resolution: 24 hrs', 'Uptime: 99%'],
    status: 'active',
    utilizationPercent: 65,
    lastBillingDate: '2024-01-01',
    nextBillingDate: '2024-04-01',
  },
  {
    id: 'RC-002',
    vendor: 'SecureGuard Services',
    vendorId: 'V005',
    type: 'amc',
    serviceScope: 'Security Personnel & Equipment Maintenance',
    category: 'Security',
    contractValue: 2400000,
    billingCycle: 'monthly',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    slaKpis: ['Guards on duty: 24/7', 'Patrol frequency: 2 hrs', 'Incident response: 5 min'],
    status: 'active',
    utilizationPercent: 75,
    lastBillingDate: '2024-01-15',
    nextBillingDate: '2024-02-15',
  },
  {
    id: 'RC-003',
    vendor: 'CleanPro Services',
    vendorId: 'V001',
    type: 'amc',
    serviceScope: 'Housekeeping Services - Tower A & B',
    category: 'Soft Services',
    contractValue: 960000,
    billingCycle: 'monthly',
    startDate: '2023-06-01',
    endDate: '2024-05-31',
    slaKpis: ['Cleaning cycles: 3/day', 'Deep cleaning: Weekly', 'Satisfaction: >90%'],
    status: 'expiring_soon',
    utilizationPercent: 90,
    lastBillingDate: '2024-01-01',
    nextBillingDate: '2024-02-01',
  },
  {
    id: 'RC-004',
    vendor: 'PowerGrid Solutions',
    vendorId: 'V003',
    type: 'rate_contract',
    serviceScope: 'Electrical Spares Supply',
    category: 'Electrical',
    contractValue: 500000,
    billingCycle: 'monthly',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    slaKpis: ['Delivery: 48 hrs', 'Quality: 100%', 'Stock availability: 95%'],
    status: 'active',
    utilizationPercent: 35,
    lastBillingDate: '2024-01-10',
    nextBillingDate: '2024-02-10',
  },
];

const proposals = [
  {
    id: 'PAY-001',
    vendorName: 'ABC Facilities Pvt Ltd',
    vendorId: 'V001',
    invoices: ['INV-2024-001', 'INV-2024-002'],
    totalAmount: 250000,
    gstAmount: 45000,
    retentionAmount: 12500,
    netPayable: 282500,
    dueDate: '2024-01-25',
    status: 'pending_approval',
    createdBy: 'Priya Sharma',
    createdDate: '2024-01-15',
    currentApprover: 'Finance Manager',
    approvalLevel: 2,
    maxApprovalLevel: 3,
  },
  {
    id: 'PAY-002',
    vendorName: 'SecureGuard Services',
    vendorId: 'V005',
    invoices: ['INV-2024-003'],
    totalAmount: 150000,
    gstAmount: 27000,
    retentionAmount: 7500,
    netPayable: 169500,
    dueDate: '2024-01-28',
    status: 'approved',
    createdBy: 'Amit Patel',
    createdDate: '2024-01-16',
    currentApprover: 'Project Head',
    approvalLevel: 3,
    maxApprovalLevel: 3,
  },
  {
    id: 'PAY-003',
    vendorName: 'GreenScape Landscaping',
    vendorId: 'V006',
    invoices: ['INV-2024-002'],
    totalAmount: 75000,
    gstAmount: 13500,
    retentionAmount: 3750,
    netPayable: 84750,
    dueDate: '2024-01-30',
    status: 'processing',
    createdBy: 'Rajesh Kumar',
    createdDate: '2024-01-17',
    approvalLevel: 3,
    maxApprovalLevel: 3,
  },
];

const indents = [
  {
    id: 'IND-2024-001',
    type: 'material',
    tower: 'Tower A',
    floor: 'Floor 5',
    category: 'Electrical',
    items: [{ itemName: 'LED Tube Light 20W', quantity: 50, uom: 'Nos' }],
    estimatedCost: 22500,
    requiredDate: '2026-02-15',
    budgetHead: 'BUD-002',
    justification: 'Replacement of faulty lights on Floor 5',
    status: 'submitted',
    createdBy: 'Rajesh Kumar',
  },
  {
    id: 'IND-2024-002',
    type: 'service',
    tower: 'Tower B',
    floor: 'Floor 3',
    category: 'HVAC',
    items: [{ itemName: 'AC Filter Replacement', quantity: 20, uom: 'Nos' }],
    estimatedCost: 24000,
    requiredDate: '2026-03-01',
    budgetHead: 'BUD-001',
    justification: 'Scheduled quarterly filter replacement',
    status: 'submitted',
    createdBy: 'Deepak Joshi',
  },
  {
    id: 'IND-2024-003',
    type: 'material',
    tower: 'Tower C',
    floor: 'Floor 8',
    category: 'Housekeeping',
    items: [{ itemName: 'Floor Cleaning Chemical', quantity: 100, uom: 'Ltr' }],
    estimatedCost: 8500,
    requiredDate: '2026-02-28',
    budgetHead: 'BUD-003',
    justification: 'Monthly cleaning supplies restock',
    status: 'approved',
    createdBy: 'Priya Sharma',
  },
];

async function seed() {
  console.log('🌱 Seeding initial business data...');
  try {
    // 1. Vendors
    for (const v of vendors) {
      await db.query(
        `INSERT INTO vendors (id, name, type, category, gst_number, pan, msme_status, bank_name, account_number, ifsc, sla_rating, approved_towers, compliance_expiry, status, contact_person, email, phone)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
         ON CONFLICT (id) DO UPDATE SET
           sla_rating = EXCLUDED.sla_rating,
           status = EXCLUDED.status,
           name = EXCLUDED.name`,
        [v.id, v.name, v.type, v.category, v.gstNumber, v.pan, v.msmeStatus, v.bankDetails.bankName, v.bankDetails.accountNumber, v.bankDetails.ifsc, v.slaRating, JSON.stringify(v.approvedTowers), v.complianceExpiry, v.status, v.contactPerson, v.email, v.phone]
      );
    }
    console.log('  ✅ Vendors seeded (' + vendors.length + ')');

    // 2. Items
    for (const item of items) {
      await db.query(
        `INSERT INTO items (id, name, type, category, uom, min_stock_level, reorder_level, current_stock, preferred_vendor, unit_price)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
         ON CONFLICT (id) DO UPDATE SET
           current_stock = EXCLUDED.current_stock,
           unit_price = EXCLUDED.unit_price`,
        [item.id, item.name, item.type, item.category, item.uom, item.minStockLevel, item.reorderLevel, item.currentStock, item.preferredVendor, item.unitPrice]
      );
    }
    console.log('  ✅ Items seeded (' + items.length + ')');

    // 3. Budgets
    for (const b of budgets) {
      await db.query(
        `INSERT INTO budgets (id, fy, type, tower, department, category, gl_code, period, annual_budget, allocated, committed, actual, owner, status, notes)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
         ON CONFLICT (id) DO UPDATE SET
           annual_budget = EXCLUDED.annual_budget,
           actual = EXCLUDED.actual`,
        [b.id, b.fy, b.type, b.tower, b.department, b.category, b.glCode, b.period, b.annualBudget, b.allocated, b.committed, b.actual, b.owner, b.status, b.notes || null]
      );
    }
    console.log('  ✅ Budgets seeded (' + budgets.length + ')');

    // 4. Purchase Orders
    for (const po of purchaseOrders) {
      await db.query(
        `INSERT INTO purchase_orders (id, type, vendor, vendor_name, linked_rfq, items, total_value, taxes, net_value, retention_percent, milestones, start_date, end_date, status, tower, category)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
         ON CONFLICT (id) DO UPDATE SET
           net_value = EXCLUDED.net_value,
           status = EXCLUDED.status`,
        [po.id, po.type, po.vendor, po.vendorName, po.linkedRfq || null, JSON.stringify(po.items), po.totalValue, po.taxes, po.netValue, po.retentionPercent, JSON.stringify(po.milestones || []), po.startDate, po.endDate, po.status, po.tower, po.category]
      );
    }
    console.log('  ✅ Purchase Orders seeded (' + purchaseOrders.length + ')');

    // 5. Invoices
    for (const inv of invoices) {
      await db.query(
        `INSERT INTO invoices (id, vendor_id, vendor_name, invoice_number, invoice_date, po_id, grn_id, ses_id, amount, gst, total_amount, due_date, status, matching_status, attachments)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
         ON CONFLICT (id) DO UPDATE SET
           total_amount = EXCLUDED.total_amount,
           status = EXCLUDED.status`,
        [inv.id, inv.vendorId, inv.vendorName, inv.invoiceNumber, inv.invoiceDate, inv.poId, inv.grnId || null, inv.sesId || null, inv.amount, inv.gst, inv.totalAmount, inv.dueDate, inv.status, inv.matchingStatus, JSON.stringify(inv.attachments || [])]
      );
    }
    console.log('  ✅ Invoices seeded (' + invoices.length + ')');

    // 6. RFQs
    for (const rfq of rfqs) {
      await db.query(
        `INSERT INTO rfqs (id, title, category, tower, linked_pr, estimated_value, bid_due_date, status, vendors, created_by, created_date)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
         ON CONFLICT (id) DO NOTHING`,
        [rfq.id, rfq.title, rfq.category, rfq.tower, rfq.linkedPr, rfq.estimatedValue, rfq.bidDueDate, rfq.status, JSON.stringify(rfq.vendors), rfq.createdBy, rfq.createdDate]
      );
    }
    console.log('  ✅ RFQs seeded (' + rfqs.length + ')');

    // 7. Rate Contracts
    for (const rc of contracts) {
      await db.query(
        `INSERT INTO rate_contracts (id, vendor, vendor_id, type, service_scope, category, contract_value, billing_cycle, start_date, end_date, sla_kpis, status, utilization_percent, last_billing_date, next_billing_date)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
         ON CONFLICT (id) DO NOTHING`,
        [rc.id, rc.vendor, rc.vendorId, rc.type, rc.serviceScope, rc.category, rc.contractValue, rc.billingCycle, rc.startDate, rc.endDate, JSON.stringify(rc.slaKpis), rc.status, rc.utilizationPercent, rc.lastBillingDate, rc.nextBillingDate]
      );
    }
    console.log('  ✅ Rate Contracts seeded (' + contracts.length + ')');

    // 8. Payment Proposals
    for (const prop of proposals) {
      await db.query(
        `INSERT INTO payment_proposals (id, vendor_name, vendor_id, invoices, total_amount, gst_amount, retention_amount, net_payable, due_date, status, created_by, created_date, current_approver, approval_level, max_approval_level)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
         ON CONFLICT (id) DO NOTHING`,
        [prop.id, prop.vendorName, prop.vendorId, JSON.stringify(prop.invoices), prop.totalAmount, prop.gstAmount, prop.retentionAmount, prop.netPayable, prop.dueDate, prop.status, prop.createdBy, prop.createdDate, prop.currentApprover || null, prop.approvalLevel, prop.maxApprovalLevel]
      );
    }
    console.log('  ✅ Payment Proposals seeded (' + proposals.length + ')');

    // 9. Indents
    for (const ind of indents) {
      await db.query(
        `INSERT INTO indents (id, type, tower, floor, category, items, estimated_cost, required_date, budget_head, justification, status, created_by)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
         ON CONFLICT (id) DO UPDATE SET
           status = EXCLUDED.status`,
        [ind.id, ind.type, ind.tower, ind.floor, ind.category, JSON.stringify(ind.items), ind.estimatedCost, ind.requiredDate, ind.budgetHead, ind.justification, ind.status, ind.createdBy]
      );
    }
    console.log('  ✅ Indents seeded (' + indents.length + ')');

    console.log('\n🎉 All business data seeded successfully.');
  } catch (err) {
    console.error('❌ Seeding failed:', err);
    throw err;
  }
}

// Support both direct execution and require()
if (require.main === module) {
  seed().then(() => process.exit(0)).catch(() => process.exit(1));
} else {
  module.exports = seed();
}
