require('dotenv').config({
  path: require('path').join(__dirname, '../.env')
});
const bcrypt = require('bcrypt');
const db = require('../db');

async function seed() {
  const users = [
    { email: 'admin@test.com',      password: 'admin123',  name: 'Admin User',      role: 'procurement_manager', department: 'Procurement' },
    { email: 'cxo@test.com',        password: 'admin123',  name: 'Ramesh Agarwal',  role: 'cxo',                 department: 'Management' },
    { email: 'finance@test.com',    password: 'admin123',  name: 'Vikram Singh',    role: 'finance_manager',     department: 'Finance' },
    { email: 'engineer@test.com',   password: 'admin123',  name: 'Rajesh Kumar',    role: 'site_engineer',       department: 'Engineering' },
    { email: 'storekeeper@test.com',password: 'admin123',  name: 'Suresh Patel',    role: 'store_keeper',        department: 'Stores' },
    { email: 'vendor@test.com',     password: 'admin123',  name: 'ABC Facilities',  role: 'vendor',              department: 'External' },
  ];

  for (const u of users) {
    const hash = await bcrypt.hash(u.password, 12);
    await db.query(
      `INSERT INTO users (email, password, name, role, department)
       VALUES ($1,$2,$3,$4,$5)
       ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password, name = EXCLUDED.name`,
      [u.email, hash, u.name, u.role, u.department]
    );
    console.log(`✅ Seeded: ${u.email} / ${u.role}`);
  }

  console.log('\nAll users seeded. Password for all: admin123');
  process.exit(0);
}

seed().catch(err => { console.error(err); process.exit(1); });
