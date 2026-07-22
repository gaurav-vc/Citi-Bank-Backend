const fs = require('fs');
const path = require('path');
const db = require('../db');

async function run() {
  console.log('Running database migrations...');
  
  const migrationFiles = [
    '001_users.sql',
    '002_business_tables.sql',
    '003_remaining_tables.sql',
    '004_rbac_architecture.sql',
    '005_enterprise_hierarchy.sql',
    '006_workflow_sla.sql'
  ];

  try {
    for (const file of migrationFiles) {
      const filePath = path.join(__dirname, '../migrations', file);
      if (fs.existsSync(filePath)) {
        console.log(`Executing ${file}...`);
        const sql = fs.readFileSync(filePath, 'utf8');
        await db.query(sql);
        console.log(`${file} executed successfully.`);
      } else {
        console.warn(`Warning: migration file ${file} does not exist at ${filePath}`);
      }
    }

    console.log('All migrations completed successfully.');
    process.exit(0);
  } catch (err) {
    console.error('Migration failed:', err);
    process.exit(1);
  }
}

run();
