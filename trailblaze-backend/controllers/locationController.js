const Location = require('../models/Location');
const supabase = require('../utils/supabaseClient');

// Get all locations
const getAllLocations = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;
    
    const locations = await Location.find()
      .sort({ times_visited: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Location.countDocuments();
    
    res.json({
      success: true,
      locations,
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

// Get location by ID
const getLocationById = async (req, res) => {
  try {
    const { locationId } = req.params;
    
    const location = await Location.findById(locationId);
    if (!location) {
      return res.status(404).json({ message: 'Location not found' });
    }
    
    res.json({
      success: true,
      location
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Search for locations
const searchLocations = async (req, res) => {
  try {
    const { query } = req.query;
    
    if (!query) {
      return res.status(400).json({ message: 'Search query is required' });
    }
    
    const locations = await Location.find({
      $text: { $search: query }
    })
      .sort({ score: { $meta: 'textScore' } })
      .limit(20);
    
    res.json({
      success: true,
      locations
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Upload a photo for a location
const uploadLocationPhoto = async (req, res) => {
  try {
    const { locationId } = req.params;
    const userId = req.user._id;
    const { caption } = req.body;
    
    // Check if location exists
    const location = await Location.findById(locationId);
    if (!location) {
      return res.status(404).json({ message: 'Location not found' });
    }
    
    // Ensure file was uploaded
    if (!req.file) {
      return res.status(400).json({ message: 'No image file provided' });
    }
    
    // Upload to Supabase storage
    const fileName = `${Date.now()}_${userId.toString()}`;
    const filePath = `locations/${locationId}/${fileName}`;
    
    const { data, error } = await supabase
      .storage
      .from('adventure_photos')
      .upload(filePath, req.file.buffer, {
        contentType: req.file.mimetype
      });
    
    if (error) {
      throw new Error(`Supabase storage error: ${error.message}`);
    }
    
    // Get public URL
    const { data: urlData } = supabase
      .storage
      .from('adventure_photos')
      .getPublicUrl(filePath);
    
    const photoUrl = urlData.publicUrl;
    
    // Add reference to location document
    location.photo_references.push({
      storage_path: filePath,
      user_id: userId,
      caption: caption || '',
      created_at: new Date()
    });
    
    // Increment location visit count
    location.times_visited += 1;
    
    await location.save();
    
    res.status(201).json({
      success: true,
      photo: {
        url: photoUrl,
        path: filePath,
        caption
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get all photos for a location
const getLocationPhotos = async (req, res) => {
  try {
    const { locationId } = req.params;
    
    // Get location data from MongoDB
    const location = await Location.findById(locationId);
    if (!location) {
      return res.status(404).json({ message: 'Location not found' });
    }
    
    // List files from Supabase for this location
    const { data, error } = await supabase
      .storage
      .from('adventure_photos')
      .list(`locations/${locationId}`);
      
    if (error) {
      throw new Error(`Supabase storage error: ${error.message}`);
    }
    
    // Map photo references to include URLs
    const photos = location.photo_references.map(ref => {
      const { data: urlData } = supabase
        .storage
        .from('adventure_photos')
        .getPublicUrl(ref.storage_path);
        
      return {
        id: ref._id,
        url: urlData.publicUrl,
        caption: ref.caption,
        user_id: ref.user_id,
        created_at: ref.created_at
      };
    });
    
    res.json({
      success: true,
      location: {
        name: location.name,
        address: location.address
      },
      photos
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

module.exports = {
  getAllLocations,
  getLocationById,
  searchLocations,
  uploadLocationPhoto,
  getLocationPhotos
};