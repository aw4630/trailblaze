const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

const testConnection = async () => {
  try {
    console.log('Attempting to connect to MongoDB...');
    console.log(`Connection string: ${process.env.MONGODB_URI?.substring(0, 20)}...`);
    
    const conn = await mongoose.connect(process.env.MONGODB_URI);
    
    console.log(`MongoDB Connected Successfully!`);
    console.log(`Host: ${conn.connection.host}`);
    console.log(`Database Name: ${conn.connection.name}`);
    
    // List collections
    const collections = await conn.connection.db.listCollections().toArray();
    console.log('Available collections:');
    collections.forEach(collection => {
      console.log(`- ${collection.name}`);
    });
    
    // Close the connection
    await mongoose.connection.close();
    console.log('Connection closed successfully');
    
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error.message}`);
    if (error.name === 'MongoParseError') {
      console.error('Please check your MongoDB connection string format');
    } else if (error.name === 'MongoNetworkError') {
      console.error('Network error - please check your internet connection and MongoDB server status');
    }
  }
};

testConnection(); 