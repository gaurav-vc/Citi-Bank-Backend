-- 006_workflow_sla.sql

-- Workflow Rules (Criteria determining who approves what based on value & department)
CREATE TABLE IF NOT EXISTS workflow_rules (
    id SERIAL PRIMARY KEY,
    module VARCHAR(100) NOT NULL, -- e.g. 'indents', 'payments'
    min_amount NUMERIC(15, 2) DEFAULT 0.00,
    max_amount NUMERIC(15, 2) DEFAULT 999999999.99,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    required_role_name VARCHAR(100) NOT NULL, -- e.g. 'facility_manager'
    step_sequence INT NOT NULL, -- e.g. 1, 2, 3
    sla_hours INT DEFAULT 24, -- SLA time limit for this step
    conditional_type VARCHAR(100) DEFAULT 'always', -- 'always', 'capex_only', 'opex_only'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Instances (Tracks active approval lifecycles for entities)
CREATE TABLE IF NOT EXISTS workflow_instances (
    id SERIAL PRIMARY KEY,
    module VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL, -- e.g. 'IND-2024-001'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module, entity_id)
);

-- Workflow Steps (Specific instances of steps generated from rules)
CREATE TABLE IF NOT EXISTS workflow_steps (
    id SERIAL PRIMARY KEY,
    instance_id INT REFERENCES workflow_instances(id) ON DELETE CASCADE,
    step_sequence INT NOT NULL,
    assigned_role_name VARCHAR(100) NOT NULL,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'escalated'
    sla_hours INT DEFAULT 24,
    due_at TIMESTAMP NOT NULL,
    actioned_at TIMESTAMP,
    actioned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    comments TEXT,
    escalated_to_role VARCHAR(100)
);

-- Create index for query performance
CREATE INDEX IF NOT EXISTS idx_workflow_steps_instance ON workflow_steps(instance_id);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_status ON workflow_steps(status);
