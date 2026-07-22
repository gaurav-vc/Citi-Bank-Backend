-- Drop existing business tables to ensure clean slate
DROP TABLE IF EXISTS failed_import_rows CASCADE;
DROP TABLE IF EXISTS export_logs CASCADE;
DROP TABLE IF EXISTS import_logs CASCADE;
DROP TABLE IF EXISTS payment_proposals CASCADE;
DROP TABLE IF EXISTS rate_contracts CASCADE;
DROP TABLE IF EXISTS rfqs CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;

-- Create business tables

CREATE TABLE vendors (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,
  category VARCHAR(100) NOT NULL,
  gst_number VARCHAR(50) NOT NULL,
  pan VARCHAR(50) NOT NULL,
  msme_status BOOLEAN NOT NULL DEFAULT false,
  bank_name VARCHAR(100) NOT NULL,
  account_number VARCHAR(100) NOT NULL,
  ifsc VARCHAR(50) NOT NULL,
  sla_rating NUMERIC(3, 2) NOT NULL DEFAULT 0.0,
  approved_towers JSONB NOT NULL DEFAULT '[]'::jsonb,
  compliance_expiry DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  contact_person VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(50) NOT NULL
);

CREATE TABLE items (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,
  category VARCHAR(100) NOT NULL,
  uom VARCHAR(50) NOT NULL,
  min_stock_level INTEGER NOT NULL DEFAULT 0,
  reorder_level INTEGER NOT NULL DEFAULT 0,
  current_stock INTEGER NOT NULL DEFAULT 0,
  preferred_vendor VARCHAR(255),
  unit_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE budgets (
  id VARCHAR(50) PRIMARY KEY,
  fy VARCHAR(50) NOT NULL,
  type VARCHAR(50) NOT NULL,
  tower VARCHAR(100) NOT NULL,
  department VARCHAR(100) NOT NULL,
  category VARCHAR(100) NOT NULL,
  gl_code VARCHAR(50) NOT NULL,
  period VARCHAR(50) NOT NULL,
  annual_budget NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  allocated NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  committed NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  actual NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  owner VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  notes TEXT
);

CREATE TABLE purchase_orders (
  id VARCHAR(50) PRIMARY KEY,
  type VARCHAR(50) NOT NULL,
  vendor VARCHAR(50) NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  vendor_name VARCHAR(255) NOT NULL,
  linked_rfq VARCHAR(50),
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  total_value NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  taxes NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  net_value NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  retention_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
  milestones JSONB DEFAULT '[]'::jsonb,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  tower VARCHAR(100) NOT NULL,
  category VARCHAR(100) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE invoices (
  id VARCHAR(50) PRIMARY KEY,
  vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  vendor_name VARCHAR(255) NOT NULL,
  invoice_number VARCHAR(100) NOT NULL UNIQUE,
  invoice_date DATE NOT NULL,
  po_id VARCHAR(50) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  grn_id VARCHAR(50),
  ses_id VARCHAR(50),
  amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  gst NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  total_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  due_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  matching_status VARCHAR(50) NOT NULL DEFAULT '2way',
  attachments JSONB DEFAULT '[]'::jsonb
);

CREATE TABLE rfqs (
  id VARCHAR(50) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(100) NOT NULL,
  tower VARCHAR(100) NOT NULL,
  linked_pr VARCHAR(50),
  estimated_value NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  bid_due_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  vendors JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_by VARCHAR(100) NOT NULL,
  created_date DATE NOT NULL
);

CREATE TABLE rate_contracts (
  id VARCHAR(50) PRIMARY KEY,
  vendor VARCHAR(255) NOT NULL,
  vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  service_scope TEXT NOT NULL,
  category VARCHAR(100) NOT NULL,
  contract_value NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  billing_cycle VARCHAR(50) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  sla_kpis JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  utilization_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
  last_billing_date DATE,
  next_billing_date DATE
);

CREATE TABLE payment_proposals (
  id VARCHAR(50) PRIMARY KEY,
  vendor_name VARCHAR(255) NOT NULL,
  vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  invoices JSONB NOT NULL DEFAULT '[]'::jsonb,
  total_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  gst_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  retention_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  net_payable NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  due_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  created_by VARCHAR(100) NOT NULL,
  created_date DATE NOT NULL,
  current_approver VARCHAR(100),
  approval_level INTEGER NOT NULL DEFAULT 0,
  max_approval_level INTEGER NOT NULL DEFAULT 1
);

-- Support tables for import/export logs
CREATE TABLE import_logs (
  id SERIAL PRIMARY KEY,
  module VARCHAR(50) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(10) NOT NULL,
  status VARCHAR(20) NOT NULL, -- 'success', 'partial_success', 'failed'
  total_rows INTEGER NOT NULL DEFAULT 0,
  processed_rows INTEGER NOT NULL DEFAULT 0,
  failed_rows INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE export_logs (
  id SERIAL PRIMARY KEY,
  module VARCHAR(50) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(10) NOT NULL,
  filters JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE failed_import_rows (
  id SERIAL PRIMARY KEY,
  import_log_id INTEGER REFERENCES import_logs(id) ON DELETE CASCADE,
  row_index INTEGER NOT NULL,
  row_data JSONB NOT NULL,
  error_message TEXT NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(status);
CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
CREATE INDEX IF NOT EXISTS idx_budgets_fy ON budgets(fy);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_vendor ON purchase_orders(vendor);
CREATE INDEX IF NOT EXISTS idx_invoices_po ON invoices(po_id);
CREATE INDEX IF NOT EXISTS idx_rate_contracts_vendor ON rate_contracts(vendor_id);
CREATE INDEX IF NOT EXISTS idx_payment_proposals_status ON payment_proposals(status);
