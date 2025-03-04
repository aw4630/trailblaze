const mongoose = require('mongoose');

const LikeSchema = new mongoose.Schema({
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
  created_at: {
    type: Date,
    default: Date.now
  }
});

// Create a compound index to ensure one like per user per adventure
LikeSchema.index({ user_id: 1, adventure_id: 1 }, { unique: true });

module.exports = mongoose.model('Like', LikeSchema);