require('dotenv').config();
const mongoose = require('mongoose');

async function testDbConnection() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Successfully connected to MongoDB');
    
    // List all collections
    const collections = await mongoose.connection.db.listCollections().toArray();
    console.log('Available collections:');
    collections.forEach(collection => console.log(`- ${collection.name}`));
    
    // Test Supabase connection if you're using it
    if (process.env.SUPABASE_URL && process.env.SUPABASE_KEY) {
      const { createClient } = require('@supabase/supabase-js');
      const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);
      
      // Simple test query
      const { data, error } = await supabase.from('your_table_name').select('*').limit(1);
      
      if (error) throw error;
      console.log('✅ Successfully connected to Supabase');
    }
  } catch (error) {
    console.error('❌ Database connection error:', error);
  } finally {
    // Close the connection
    await mongoose.connection.close();
    console.log('Database connection closed');
    process.exit(0);
  }
}

testDbConnection(); 