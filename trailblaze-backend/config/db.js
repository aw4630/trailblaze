const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI);
    
    console.log(`MongoDB Connected: ${conn.connection.host}`);
    
    // Create indexes
    const db = mongoose.connection;
    
    // Create text indexes for search
    await db.collection('locations').createIndex({ name: 'text', description: 'text' });
    await db.collection('adventures').createIndex({ title: 'text', description: 'text' });
    
    // Create geospatial index for locations
    await db.collection('locations').createIndex({ latitude: 1, longitude: 1 }, { name: "geospatial" });
    
    // Create other indexes for performance
    await db.collection('adventures').createIndex({ creator_id: 1 });
    await db.collection('adventures').createIndex({ is_public: 1, fire_score: -1 });
    await db.collection('ratings').createIndex({ adventure_id: 1 });
    await db.collection('likes').createIndex({ user_id: 1, adventure_id: 1 }, { unique: true });
    
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB;