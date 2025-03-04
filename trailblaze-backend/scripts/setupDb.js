const mongoose = require('mongoose');
const dotenv = require('dotenv');
const supabase = require('../utils/supabaseClient');

// Load environment variables
dotenv.config();

// Connect to MongoDB
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    console.log('MongoDB Connected');
    
    console.log('Setting up indexes...');
    const db = mongoose.connection;
    
    // Create indexes
    await db.collection('locations').createIndex({ name: 'text', description: 'text' });
    await db.collection('adventures').createIndex({ title: 'text', description: 'text' });
    await db.collection('locations').createIndex({ place_id: 1 }, { unique: true, sparse: true });
    await db.collection('locations').createIndex({ latitude: 1, longitude: 1 }, { name: "geospatial" });
    await db.collection('adventures').createIndex({ creator_id: 1 });
    await db.collection('adventures').createIndex({ is_public: 1, fire_score: -1 });
    await db.collection('ratings').createIndex({ adventure_id: 1 });
    await db.collection('likes').createIndex({ user_id: 1, adventure_id: 1 }, { unique: true });
    
    console.log('MongoDB indexes created');
    
    console.log('Setting up Supabase storage bucket...');
    
    // Check if bucket exists
    const { data: buckets, error: bucketsError } = await supabase
      .storage
      .listBuckets();
      
    if (bucketsError) {
      throw new Error(`Failed to list buckets: ${bucketsError.message}`);
    }
    
    if (!buckets.find(bucket => bucket.name === 'adventure_photos')) {
      // Create bucket
      const { data, error } = await supabase
        .storage
        .createBucket('adventure_photos', {
          public: true
        });
        
      if (error) {
        throw new Error(`Failed to create bucket: ${error.message}`);
      }
      
      console.log('Created adventure_photos bucket');
    } else {
      console.log('adventure_photos bucket already exists');
    }
    
    console.log('Setup complete!');
    process.exit(0);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
};

connectDB();