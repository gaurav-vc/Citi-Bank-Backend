const db = require('../db');

async function seedRbac() {
  try {
    console.log('Truncating RBAC tables...');
    await db.query('TRUNCATE TABLE app_modules, app_features, role_access_mappings, roles CASCADE');
    console.log('Seeding RBAC App Modules and Features...');
    
    // Seed Departments
    const deptResult = await db.query(`
      INSERT INTO departments (name, description) VALUES 
      ('IT', 'Information Technology'),
      ('HR', 'Human Resources'),
      ('Finance', 'Financial Department')
      ON CONFLICT (name) DO NOTHING
      RETURNING id;
    `);

    // Seed Roles
    const roleResult = await db.query(`
      INSERT INTO roles (role_name, description) VALUES 
      ('Admin', 'System Administrator'),
      ('Manager', 'Department Manager'),
      ('Staff', 'Regular Staff Member')
      ON CONFLICT (role_name) DO NOTHING
      RETURNING id;
    `);

    // Seed App Modules
    const modules = [
      { name: 'Core Features', order: 0 },
      { name: 'Procurement', order: 1 },
      { name: 'Finance', order: 2 }
    ];

    for (const mod of modules) {
      const res = await db.query(
        'INSERT INTO app_modules (name, module_order) VALUES ($1, $2) RETURNING id',
        [mod.name, mod.order]
      );
      const modId = res.rows[0].id;

      if (mod.name === 'Core Features') {
        await db.query(`
          INSERT INTO app_features (module_id, feature_key, label) VALUES
          ($1, 'core:dashboard', 'Dashboard'),
          ($1, 'core:users', 'User Management')
        `, [modId]);
      } else if (mod.name === 'Procurement') {
        await db.query(`
          INSERT INTO app_features (module_id, feature_key, label) VALUES
          ($1, 'procurement:rfqs', 'RFQs'),
          ($1, 'procurement:orders', 'Purchase Orders')
        `, [modId]);
      }
    }

    console.log('RBAC Seeding Completed!');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding RBAC:', error);
    process.exit(1);
  }
}

seedRbac();
