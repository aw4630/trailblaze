const mongoose = require('mongoose');

const RatingSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  adventure_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Adventure',
    required: true
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  review_text: String,
  created_at: {
    type: Date,
    default: Date.now
  }
});

// Create a compound index to ensure one rating per user per adventure
RatingSchema.index({ user_id: 1, adventure_id: 1 }, { unique: true });

module.exports = mongoose.model('Rating', RatingSchema);