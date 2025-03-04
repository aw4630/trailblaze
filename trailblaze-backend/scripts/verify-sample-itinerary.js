const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

// Import models
const Adventure = require('../models/Adventure');
const Location = require('../models/Location');
const User = require('../models/User');

const verifyItinerary = async () => {
  try {
    // Connect to MongoDB
    console.log('Connecting to MongoDB...');
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('Connected to MongoDB');

    // Find the test user
    const testUser = await User.findOne({ email: 'test@example.com' });
    if (!testUser) {
      console.error('Test user not found!');
      await mongoose.connection.close();
      return;
    }
    
    console.log(`Found test user: ${testUser.username} (${testUser._id})`);

    // Find the adventure
    const adventure = await Adventure.findOne({ 
      title: 'NYC Landmarks Adventure',
      creator_id: testUser._id
    });
    
    if (!adventure) {
      console.error('Adventure not found!');
      await mongoose.connection.close();
      return;
    }
    
    console.log('\n=== ADVENTURE DETAILS ===');
    console.log(`ID: ${adventure._id}`);
    console.log(`Title: ${adventure.title}`);
    console.log(`Description: ${adventure.description}`);
    console.log(`Creator ID: ${adventure.creator_id}`);
    console.log(`Estimated Duration: ${adventure.estimated_duration} minutes`);
    console.log(`Total Distance: ${adventure.total_distance} meters`);
    console.log(`Public: ${adventure.is_public}`);
    console.log(`Created: ${adventure.created_at}`);
    
    // Print events
    console.log('\n=== EVENTS ===');
    if (adventure.events && adventure.events.length > 0) {
      adventure.events.forEach((event, index) => {
        console.log(`\nEvent #${index + 1}: ${event.name}`);
        console.log(`Description: ${event.description}`);
        console.log(`Time: ${event.start_time} to ${event.end_time}`);
        console.log(`Venue: ${event.venue_name}`);
        console.log(`Cost: $${event.cost}`);
      });
    } else {
      console.log('No events found');
    }
    
    // Print routes
    console.log('\n=== ROUTES ===');
    if (adventure.routes && adventure.routes.length > 0) {
      adventure.routes.forEach((route, index) => {
        console.log(`\nRoute #${index + 1}: ${route.from} → ${route.to}`);
        console.log(`Travel Mode: ${route.travel_mode}`);
        console.log(`Distance: ${route.distance_meters} meters`);
        console.log(`Duration: ${route.duration_seconds} seconds (${Math.round(route.duration_seconds / 60)} minutes)`);
      });
    } else {
      console.log('No routes found');
    }
    
    // Find locations
    console.log('\n=== LOCATIONS ===');
    const venueNames = adventure.events.map(event => event.venue_name);
    const uniqueVenueNames = [...new Set(venueNames)];
    
    for (const venueName of uniqueVenueNames) {
      const location = await Location.findOne({ name: venueName });
      if (location) {
        console.log(`\nLocation: ${location.name}`);
        console.log(`Address: ${location.address}`);
        console.log(`Coordinates: ${location.latitude}, ${location.longitude}`);
        console.log(`Opening Hours: ${location.opening_hours}`);
        console.log(`Place ID: ${location.place_id}`);
      } else {
        console.log(`\nWarning: Location '${venueName}' not found in database`);
      }
    }
    
    console.log('\nVerification completed successfully!');
    
    // Close the connection
    await mongoose.connection.close();
    console.log('Database connection closed');
    
  } catch (error) {
    console.error('Error verifying itinerary:', error);
    await mongoose.connection.close();
    process.exit(1);
  }
};

// Run the verification function
verifyItinerary(); 