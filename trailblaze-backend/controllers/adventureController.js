const Adventure = require('../models/Adventure');
const Location = require('../models/Location');
const AdventureCompletion = require('../models/AdventureCompletion');
const User = require('../models/User');

// Create a new adventure
const createAdventure = async (req, res) => {
  try {
    const chatbotOutput = req.body;
    const userId = req.user._id;
    
    // Process locations first
    const locationPromises = chatbotOutput.itinerary.venues.map(async venue => {
      // Check if location already exists by place_id
      let location = await Location.findOne({ place_id: venue.place_id });
      
      // If not, create it
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
      }
      
      return location;
    });
    
    const locations = await Promise.all(locationPromises);
    
    // Create events with location references
    const events = chatbotOutput.itinerary.events.map((event, index) => {
      const matchingLocation = locations.find(loc => 
        loc.name === event.venue_name || 
        loc.place_id === chatbotOutput.itinerary.venues.find(v => v.name === event.venue_name)?.place_id
      );
      
      return {
        location_id: matchingLocation?._id,
        name: event.name,
        description: event.description,
        start_time: new Date(event.start_time),
        end_time: new Date(event.end_time),
        venue_name: event.venue_name,
        cost: event.cost,
        sequence_order: index + 1
      };
    });
    
    // Calculate total duration in minutes
    const startTime = new Date(chatbotOutput.itinerary.events[0].start_time);
    const endTime = new Date(chatbotOutput.itinerary.events[chatbotOutput.itinerary.events.length - 1].end_time);
    const totalDurationMinutes = Math.round((endTime - startTime) / (1000 * 60));
    
    // Calculate total distance
    const totalDistance = chatbotOutput.itinerary.routes.reduce(
      (total, route) => total + route.distance_meters, 0
    );
    
    // Create the adventure
    const adventure = new Adventure({
      creator_id: userId,
      title: chatbotOutput.itinerary.name,
      description: chatbotOutput.itinerary.description,
      category: "Custom",
      estimated_duration: totalDurationMinutes,
      total_distance: totalDistance,
      transport_mode: chatbotOutput.itinerary.routes[0]?.travel_mode || "mixed",
      events: events,
      routes: chatbotOutput.itinerary.routes,
      is_public: true
    });
    
    await adventure.save();
    
    // Update user stats
    await User.findByIdAndUpdate(userId, {
      $inc: { 'stats.total_routes_generated': 1 }
    });
    
    res.status(201).json({
      success: true,
      adventure
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get all public adventures
const getPublicAdventures = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const sortBy = req.query.sortBy || 'fire_score';
    
    let sort = {};
    if (sortBy === 'fire_score') {
      sort = { fire_score: -1 };
    } else if (sortBy === 'rating') {
      sort = { average_rating: -1 };
    } else if (sortBy === 'recent') {
      sort = { created_at: -1 };
    } else if (sortBy === 'popular') {
      sort = { times_completed: -1 };
    }
    
    const adventures = await Adventure.find({ is_public: true })
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .populate('creator_id', 'username profile.avatar_url');
    
    const total = await Adventure.countDocuments({ is_public: true });
    
    res.json({
      success: true,
      adventures,
      pagination: {
        total,
        page,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get adventure by ID
const getAdventureById = async (req, res) => {
  try {
    const { adventureId } = req.params;
    
    const adventure = await Adventure.findById(adventureId)
      .populate('creator_id', 'username profile.avatar_url')
      .populate('events.location_id');
    
    if (!adventure) {
      return res.status(404).json({ message: 'Adventure not found' });
    }
    
    // Check if the adventure is private and not owned by the requesting user
    if (!adventure.is_public && !req.user?._id.equals(adventure.creator_id._id)) {
      return res.status(403).json({ message: 'Not authorized to view this adventure' });
    }
    
    res.json({
      success: true,
      adventure
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Start an adventure
const startAdventure = async (req, res) => {
    try {
      const { adventureId } = req.params;
      const userId = req.user._id;
      
      // Check if adventure exists
      const adventure = await Adventure.findById(adventureId);
      if (!adventure) {
        return res.status(404).json({ message: 'Adventure not found' });
      }
      
      // Create check-ins for each location
      const checkIns = adventure.events.map(event => ({
        location_id: event.location_id,
        completed: false
      }));
      
      // Create a new completion record
      const completion = new AdventureCompletion({
        user_id: userId,
        adventure_id: adventureId,
        start_time: new Date(),
        completed: false,
        check_ins: checkIns
      });
      
      await completion.save();
      
      res.status(201).json({
        success: true,
        message: 'Adventure started',
        completion
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error', error: error.message });
    }
  };
  
  // Check in at a location
  const checkInLocation = async (req, res) => {
    try {
      const { completionId, locationId } = req.body;
      const userId = req.user._id;
      
      // Find the completion
      const completion = await AdventureCompletion.findOne({
        _id: completionId,
        user_id: userId
      });
      
      if (!completion) {
        return res.status(404).json({ message: 'Adventure completion not found' });
      }
      
      // Find the check-in for this location
      const checkInIndex = completion.check_ins.findIndex(
        checkIn => checkIn.location_id.toString() === locationId
      );
      
      if (checkInIndex === -1) {
        return res.status(404).json({ message: 'Location not part of this adventure' });
      }
      
      // Update check-in
      completion.check_ins[checkInIndex].arrival_time = new Date();
      completion.check_ins[checkInIndex].completed = true;
      
      // Check if all locations are completed
      const allCompleted = completion.check_ins.every(checkIn => checkIn.completed);
      if (allCompleted && !completion.completed) {
        completion.end_time = new Date();
        completion.completed = true;
        
        // Calculate distance and money spent
        const adventure = await Adventure.findById(completion.adventure_id);
        completion.distance_traveled = adventure.total_distance;
        completion.money_spent = adventure.events.reduce(
          (total, event) => total + (event.cost || 0), 0
        );
        
        // Update user stats
        await User.findByIdAndUpdate(userId, {
          $inc: {
            'stats.total_routes_completed': 1,
            'stats.total_locations_visited': completion.check_ins.length,
            'stats.total_distance_traveled': completion.distance_traveled,
            'stats.total_money_spent': completion.money_spent
          }
        });
        
        // Update adventure completion count
        await Adventure.findByIdAndUpdate(completion.adventure_id, {
          $inc: { times_completed: 1 }
        });
      }
      
      await completion.save();
      
      res.json({
        success: true,
        message: 'Check-in successful',
        completion,
        adventure_completed: allCompleted
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error', error: error.message });
    }
  };
  
  // Complete adventure
  const completeAdventure = async (req, res) => {
    try {
      const { completionId } = req.params;
      const userId = req.user._id;
      
      // Find the completion
      const completion = await AdventureCompletion.findOne({
        _id: completionId,
        user_id: userId
      });
      
      if (!completion) {
        return res.status(404).json({ message: 'Adventure completion not found' });
      }
      
      if (completion.completed) {
        return res.status(400).json({ message: 'Adventure already completed' });
      }
      
      // Mark adventure as completed
      completion.end_time = new Date();
      completion.completed = true;
      
      // Calculate distance and money spent
      const adventure = await Adventure.findById(completion.adventure_id);
      completion.distance_traveled = adventure.total_distance;
      completion.money_spent = adventure.events.reduce(
        (total, event) => total + (event.cost || 0), 0
      );
      
      await completion.save();
      
      // Update user stats
      await User.findByIdAndUpdate(userId, {
        $inc: {
          'stats.total_routes_completed': 1,
          'stats.total_locations_visited': completion.check_ins.filter(c => c.completed).length,
          'stats.total_distance_traveled': completion.distance_traveled,
          'stats.total_money_spent': completion.money_spent
        }
      });
      
      // Update adventure completion count
      await Adventure.findByIdAndUpdate(completion.adventure_id, {
        $inc: { times_completed: 1 }
      });
      
      res.json({
        success: true,
        message: 'Adventure completed successfully',
        completion
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error', error: error.message });
    }
  };
  
  module.exports = {
    createAdventure,
    getPublicAdventures,
    getAdventureById,
    startAdventure,
    checkInLocation,
    completeAdventure
  };