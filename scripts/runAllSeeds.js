require('dotenv').config({ path: require('path').join(__dirname, '../.env') });

async function runAll() {
  console.log('🌱 Running all seed scripts...');
  await require('./seedUser');
  await require('./seedBusinessData');
  console.log('✅ All seeds complete.');
  process.exit(0);
}

runAll().catch(err => {
  console.error('❌ Seed failed:', err);
  process.exit(1);
});
