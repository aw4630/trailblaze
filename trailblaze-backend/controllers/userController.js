const User = require('../models/User');
const Adventure = require('../models/Adventure');
const AdventureCompletion = require('../models/AdventureCompletion');

// Get user profile
const getUserProfile = async (req, res) => {
  try {
    const userId = req.params.userId || req.user._id;
    
    const user = await User.findById(userId).select('-password');
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Get user stats
    const adventuresCreated = await Adventure.countDocuments({ creator_id: userId });
    const adventuresCompleted = await AdventureCompletion.countDocuments({ 
      user_id: userId,
      completed: true
    });
    
    res.json({
      success: true,
      user,
      stats: {
        ...user.stats,
        adventures_created: adventuresCreated,
        adventures_completed: adventuresCompleted
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Update user profile
const updateUserProfile = async (req, res) => {
  try {
    const { username, email, bio, avatar_url } = req.body;
    
    // Find user
    const user = await User.findById(req.user._id);
    
    // Check if username is being changed and if it's available
    if (username && username !== user.username) {
      const existingUsername = await User.findOne({ username });
      if (existingUsername) {
        return res.status(400).json({ message: 'Username already in use' });
      }
      user.username = username;
    }
    
    // Check if email is being changed and if it's available
    if (email && email !== user.email) {
      const existingEmail = await User.findOne({ email });
      if (existingEmail) {
        return res.status(400).json({ message: 'Email already in use' });
      }
      user.email = email;
    }
    
    // Update other fields
    if (bio !== undefined) user.profile.bio = bio;
    if (avatar_url) user.profile.avatar_url = avatar_url;
    
    user.updated_at = Date.now();
    await user.save();
    
    res.json({
      success: true,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        profile: user.profile
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get user's created adventures
const getUserAdventures = async (req, res) => {
  try {
    const userId = req.params.userId || req.user._id;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const adventures = await Adventure.find({ creator_id: userId })
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit)
      .populate('creator_id', 'username profile.avatar_url');
    
    const total = await Adventure.countDocuments({ creator_id: userId });
    
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

// Get user's completed adventures
const getUserCompletions = async (req, res) => {
  try {
    const userId = req.params.userId || req.user._id;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const completions = await AdventureCompletion.find({ 
      user_id: userId,
      completed: true
    })
      .sort({ end_time: -1 })
      .skip(skip)
      .limit(limit)
      .populate({
        path: 'adventure_id',
        select: 'title description category',
        populate: {
          path: 'creator_id',
          select: 'username profile.avatar_url'
        }
      });
    
    const total = await AdventureCompletion.countDocuments({ 
      user_id: userId,
      completed: true
    });
    
    res.json({
      success: true,
      completions,
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

module.exports = {
  getUserProfile,
  updateUserProfile,
  getUserAdventures,
  getUserCompletions
};