-- 004_rbac_architecture.sql

-- Departments (equivalent to Zones)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- App Modules
CREATE TABLE IF NOT EXISTS app_modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    module_order INT DEFAULT 0
);

-- App Features
CREATE TABLE IF NOT EXISTS app_features (
    id SERIAL PRIMARY KEY,
    module_id INT REFERENCES app_modules(id) ON DELETE CASCADE,
    feature_key VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL
);

-- Role Access Mapping (Links a role and a department to granular JSON permissions)
CREATE TABLE IF NOT EXISTS role_access_mappings (
    id SERIAL PRIMARY KEY,
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{}'::jsonb,
    UNIQUE(role_id, department_id)
);

-- User Profiles (Extends existing users table)
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    role_name VARCHAR(100),
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    phone_number VARCHAR(50),
    profile_picture TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
