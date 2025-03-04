const mongoose = require('mongoose');

const PhotoReferenceSchema = new mongoose.Schema({
  storage_path: String,
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  caption: String,
  created_at: {
    type: Date,
    default: Date.now
  }
});

const LocationSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  description: String,
  address: String,
  latitude: {
    type: Number,
    required: true
  },
  longitude: {
    type: Number,
    required: true
  },
  place_id: {
    type: String,
    unique: true,
    sparse: true // Allows null values
  },
  category: String,
  opening_hours: String,
  times_visited: {
    type: Number,
    default: 0
  },
  entrance_fee: {
    type: Number,
    default: 0
  },
  estimated_time_minutes: {
    type: Number,
    default: 60
  },
  photo_references: [PhotoReferenceSchema],
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Location', LocationSchema);