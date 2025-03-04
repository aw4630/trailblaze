const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

// Import models
const Adventure = require('../models/Adventure');
const Location = require('../models/Location');
const User = require('../models/User');

// Sample itinerary data
const sampleItinerary = {
  "itinerary": {
    "name": "NYC Landmarks Adventure",
    "description": "A journey through iconic New York City landmarks",
    "events": [
      {
        "id": "event1",
        "name": "Empire State Building",
        "description": "Visit the iconic Empire State Building observation deck",
        "start_time": "2023-08-15T10:00:00",
        "end_time": "2023-08-15T11:30:00",
        "venue_name": "Empire State Building",
        "cost": 45.0
      },
      {
        "id": "event2",
        "name": "Times Square Exploration",
        "description": "Explore the vibrant Times Square area",
        "start_time": "2023-08-15T12:00:00",
        "end_time": "2023-08-15T13:00:00",
        "venue_name": "Times Square",
        "cost": 0.0
      },
      {
        "id": "event3",
        "name": "Lunch at Bubba Gump",
        "description": "Enjoy seafood at Bubba Gump Shrimp Co.",
        "start_time": "2023-08-15T13:15:00",
        "end_time": "2023-08-15T14:30:00",
        "venue_name": "Bubba Gump Shrimp Co.",
        "cost": 35.0
      },
      {
        "id": "event4",
        "name": "Statue of Liberty & Ellis Island",
        "description": "Ferry to visit the Statue of Liberty and Ellis Island",
        "start_time": "2023-08-15T15:00:00",
        "end_time": "2023-08-15T17:00:00",
        "venue_name": "Statue of Liberty",
        "cost": 25.0
      }
    ],
    "venues": [
      {
        "name": "Empire State Building",
        "address": "20 W 34th St, New York, NY 10001",
        "latitude": 40.7484,
        "longitude": -73.9857,
        "opening_hours": "9:00 AM - 11:00 PM",
        "place_id": "ChIJaXQRs6lZwokRY6EFpJnhNNE"
      },
      {
        "name": "Times Square",
        "address": "Manhattan, NY 10036",
        "latitude": 40.758,
        "longitude": -73.9855,
        "opening_hours": "24 hours",
        "place_id": "ChIJmQJIxlVYwokRLgeuocVOGVU"
      },
      {
        "name": "Bubba Gump Shrimp Co.",
        "address": "1501 Broadway, New York, NY 10036",
        "latitude": 40.757,
        "longitude": -73.9865,
        "opening_hours": "11:00 AM - 10:00 PM",
        "place_id": "ChIJdZRfXlRYwokR9QD2W2Kbumw"
      },
      {
        "name": "Statue of Liberty",
        "address": "New York, NY 10004",
        "latitude": 40.6892,
        "longitude": -74.0445,
        "opening_hours": "9:30 AM - 5:00 PM",
        "place_id": "ChIJPTacEpBQwokRKwIlDXelxkA"
      }
    ],
    "routes": [
      {
        "from": "Empire State Building",
        "to": "Times Square",
        "travel_mode": "walking",
        "verified": true,
        "distance_meters": 1067,
        "duration_seconds": 762,
        "polyline": "mock_polyline_data",
        "steps": [
          {
            "instruction": "Travel from origin to destination via walking",
            "distance_meters": 1067,
            "duration_seconds": 762
          }
        ]
      },
      {
        "from": "Times Square",
        "to": "Bubba Gump Shrimp Co.",
        "travel_mode": "walking",
        "verified": true,
        "distance_meters": 139,
        "duration_seconds": 99,
        "polyline": "mock_polyline_data",
        "steps": [
          {
            "instruction": "Travel from origin to destination via walking",
            "distance_meters": 139,
            "duration_seconds": 99
          }
        ]
      },
      {
        "from": "Bubba Gump Shrimp Co.",
        "to": "Statue of Liberty",
        "travel_mode": "transit",
        "verified": true,
        "distance_meters": 8984,
        "duration_seconds": 1082,
        "polyline": "mock_polyline_data",
        "steps": [
          {
            "instruction": "Travel from origin to destination via transit",
            "distance_meters": 8984,
            "duration_seconds": 1082
          }
        ]
      }
    ]
  },
  "verification": {
    "is_feasible": true,
    "total_issues": 0,
    "all_issues": [],
    "details": {
      "venue_hours": {
        "is_feasible": true,
        "issues": []
      },
      "travel_times": {
        "is_feasible": true,
        "issues": []
      },
      "activity_durations": {
        "is_feasible": true,
        "issues": []
      },
      "buffer_times": {
        "is_feasible": true,
        "issues": []
      },
      "overall_timing": {
        "is_feasible": true,
        "issues": []
      }
    }
  },
  "using_mock_data": true
};

const insertSampleItinerary = async () => {
  try {
    // Connect to MongoDB
    console.log('Connecting to MongoDB...');
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('Connected to MongoDB');

    // Check if we have a test user, create one if not
    console.log('Setting up test user...');
    let testUser = await User.findOne({ email: 'test@example.com' });
    
    if (!testUser) {
      testUser = new User({
        username: 'test_user',
        email: 'test@example.com',
        password: 'password123' // This will be hashed by the pre-save hook
      });
      await testUser.save();
      console.log('Created test user');
    } else {
      console.log('Using existing test user');
    }

    // Step 1: Insert venue locations
    console.log('Creating locations...');
    const locationMap = {};
    
    for (const venue of sampleItinerary.itinerary.venues) {
      // Check if location already exists by place_id
      let location = await Location.findOne({ place_id: venue.place_id });
      
      if (!location) {
        location = new Location({
          name: venue.name,
          address: venue.address,
          latitude: venue.latitude,
          longitude: venue.longitude,
          place_id: venue.place_id,
          opening_hours: venue.opening_hours
        });
        await location.save();
        console.log(`Created location: ${venue.name}`);
      } else {
        console.log(`Using existing location: ${venue.name}`);
      }
      
      locationMap[venue.name] = location._id;
    }

    // Step 2: Create the adventure with events and routes
    console.log('Creating adventure...');
    
    // Check if adventure already exists
    let existingAdventure = await Adventure.findOne({ 
      title: sampleItinerary.itinerary.name,
      creator_id: testUser._id
    });
    
    if (existingAdventure) {
      console.log('Adventure already exists, deleting it to recreate...');
      await Adventure.deleteOne({ _id: existingAdventure._id });
    }
    
    // Map events to the Adventure schema format
    const events = sampleItinerary.itinerary.events.map((event, index) => {
      return {
        name: event.name,
        description: event.description,
        start_time: new Date(event.start_time),
        end_time: new Date(event.end_time),
        venue_name: event.venue_name,
        cost: event.cost,
        sequence_order: index
      };
    });
    
    // Map routes to the Adventure schema format
    const routes = sampleItinerary.itinerary.routes.map(route => {
      return {
        from: route.from,
        to: route.to,
        travel_mode: route.travel_mode,
        distance_meters: route.distance_meters,
        duration_seconds: route.duration_seconds,
        polyline: route.polyline,
        steps: route.steps.map(step => ({
          instruction: step.instruction,
          distance_meters: step.distance_meters,
          duration_seconds: step.duration_seconds
        }))
      };
    });
    
    // Calculate total distance from all routes
    const totalDistance = routes.reduce((sum, route) => sum + route.distance_meters, 0);
    
    // Calculate estimated duration in minutes from events and routes
    const eventsDuration = events.reduce((sum, event) => {
      const start = new Date(event.start_time);
      const end = new Date(event.end_time);
      return sum + ((end - start) / (1000 * 60)); // Convert to minutes
    }, 0);
    
    const routesDuration = routes.reduce((sum, route) => {
      return sum + (route.duration_seconds / 60); // Convert to minutes
    }, 0);
    
    const estimatedDuration = eventsDuration + routesDuration;
    
    // Create the adventure
    const adventure = new Adventure({
      creator_id: testUser._id,
      title: sampleItinerary.itinerary.name,
      description: sampleItinerary.itinerary.description,
      category: 'sightseeing',
      estimated_duration: Math.round(estimatedDuration),
      total_distance: totalDistance,
      events: events,
      routes: routes,
      is_public: true
    });
    
    await adventure.save();
    console.log(`Created adventure: ${adventure.title}`);
    
    console.log('Sample itinerary inserted successfully!');
    console.log(`Adventure ID: ${adventure._id}`);
    
    // Close the connection
    await mongoose.connection.close();
    console.log('Database connection closed');
    
  } catch (error) {
    console.error('Error inserting sample itinerary:', error);
    await mongoose.connection.close();
    process.exit(1);
  }
};

// Run the insertion function
insertSampleItinerary(); 