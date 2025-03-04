const Rating = require('../models/Rating');
const Like = require('../models/Like');
const Adventure = require('../models/Adventure');

// Rate an adventure
const rateAdventure = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const { rating, review } = req.body;
    const userId = req.user._id;
    
    // Validate rating
    if (rating < 1 || rating > 5) {
      return res.status(400).json({ message: 'Rating must be between 1 and 5' });
    }
    
    // Check if adventure exists
    const adventure = await Adventure.findById(adventureId);
    if (!adventure) {
      return res.status(404).json({ message: 'Adventure not found' });
    }
    
    // Check if user already rated this adventure
    let existingRating = await Rating.findOne({
      user_id: userId,
      adventure_id: adventureId
    });
    
    if (existingRating) {
      // Update existing rating
      existingRating.rating = rating;
      if (review !== undefined) {
        existingRating.review_text = review;
      }
      await existingRating.save();
    } else {
      // Create new rating
      existingRating = new Rating({
        user_id: userId,
        adventure_id: adventureId,
        rating,
        review_text: review || ''
      });
      await existingRating.save();
    }
    
    // Update adventure average rating
    const allRatings = await Rating.find({ adventure_id: adventureId });
    const averageRating = allRatings.reduce((sum, r) => sum + r.rating, 0) / allRatings.length;
    
    await Adventure.findByIdAndUpdate(adventureId, {
      average_rating: parseFloat(averageRating.toFixed(2))
    });
    
    res.json({
      success: true,
      message: 'Rating submitted successfully',
      rating: existingRating,
      average_rating: parseFloat(averageRating.toFixed(2))
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get all ratings for an adventure
const getAdventureRatings = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    // Check if adventure exists
    const adventure = await Adventure.findById(adventureId);
    if (!adventure) {
      return res.status(404).json({ message: 'Adventure not found' });
    }
    
    const ratings = await Rating.find({ adventure_id: adventureId })
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit)
      .populate('user_id', 'username profile.avatar_url');
    
    const total = await Rating.countDocuments({ adventure_id: adventureId });
    
    res.json({
      success: true,
      ratings,
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

// Like an adventure
const likeAdventure = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const userId = req.user._id;
    
    // Check if adventure exists
    const adventure = await Adventure.findById(adventureId);
    if (!adventure) {
      return res.status(404).json({ message: 'Adventure not found' });
    }
    
    // Check if user already liked this adventure
    const existingLike = await Like.findOne({
      user_id: userId,
      adventure_id: adventureId
    });
    
    if (existingLike) {
      // User already liked this adventure, so unlike it
      await Like.deleteOne({ _id: existingLike._id });
      
      // Update adventure fire score
      await Adventure.findByIdAndUpdate(adventureId, {
        $inc: { fire_score: -1 }
      });
      
      return res.json({
        success: true,
        message: 'Adventure unliked',
        liked: false
      });
    }
    
    // Create new like
    const like = new Like({
      user_id: userId,
      adventure_id: adventureId
    });
    
    await like.save();
    
    // Update adventure fire score
    await Adventure.findByIdAndUpdate(adventureId, {
      $inc: { fire_score: 1 }
    });
    
    res.json({
      success: true,
      message: 'Adventure liked',
      liked: true
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Check if user liked an adventure
const checkLikeStatus = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const userId = req.user._id;
    
    const like = await Like.findOne({
      user_id: userId,
      adventure_id: adventureId
    });
    
    res.json({
      success: true,
      liked: !!like
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

module.exports = {
  rateAdventure,
  getAdventureRatings,
  likeAdventure,
  checkLikeStatus
};