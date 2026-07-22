-- Drop existing tables for remaining modules if they exist
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS material_issues CASCADE;
DROP TABLE IF EXISTS scrap_disposals CASCADE;
DROP TABLE IF EXISTS stock_transfers CASCADE;
DROP TABLE IF EXISTS grns CASCADE;
DROP TABLE IF EXISTS indents CASCADE;

-- Create indents table
CREATE TABLE indents (
  id VARCHAR(50) PRIMARY KEY,
  type VARCHAR(50) NOT NULL,
  tower VARCHAR(50) NOT NULL,
  floor VARCHAR(50) NOT NULL,
  category VARCHAR(100) NOT NULL,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  estimated_cost NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  required_date DATE NOT NULL,
  budget_head VARCHAR(50) NOT NULL,
  justification TEXT,
  attachments JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(50) NOT NULL DEFAULT 'submitted',
  created_by VARCHAR(100) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  approvals JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- Create grns table
CREATE TABLE grns (
  id VARCHAR(50) PRIMARY KEY,
  po_id VARCHAR(50) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  received_date DATE NOT NULL,
  received_by VARCHAR(100) NOT NULL,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(50) NOT NULL DEFAULT 'received',
  invoice_status VARCHAR(50) NOT NULL DEFAULT 'pending'
);

-- Create stock_transfers table
CREATE TABLE stock_transfers (
  id VARCHAR(50) PRIMARY KEY,
  from_location VARCHAR(100) NOT NULL,
  to_location VARCHAR(100) NOT NULL,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  requested_by VARCHAR(100) NOT NULL,
  requested_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  approved_by VARCHAR(100),
  transfer_date DATE
);

-- Create scrap_disposals table
CREATE TABLE scrap_disposals (
  id VARCHAR(50) PRIMARY KEY,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  total_value NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  disposal_date DATE NOT NULL,
  buyer VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  gate_pass_no VARCHAR(50),
  recovered_value NUMERIC(15, 2) DEFAULT 0.00
);

-- Create material_issues table
CREATE TABLE material_issues (
  id VARCHAR(50) PRIMARY KEY,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  issued_to VARCHAR(100) NOT NULL,
  issued_date DATE NOT NULL,
  tower VARCHAR(50) NOT NULL,
  floor VARCHAR(50) NOT NULL,
  purpose TEXT NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'issued',
  department VARCHAR(100),
  work_order_ref VARCHAR(50),
  issued_by VARCHAR(100)
);

-- Create expenses table
CREATE TABLE expenses (
  id VARCHAR(50) PRIMARY KEY,
  category VARCHAR(100) NOT NULL,
  amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
  date DATE NOT NULL,
  payment_mode VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  description TEXT,
  approved_by VARCHAR(100)
);
