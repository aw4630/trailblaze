const mongoose = require('mongoose');

const StepSchema = new mongoose.Schema({
  instruction: String,
  distance_meters: Number,
  duration_seconds: Number
});

const RouteSchema = new mongoose.Schema({
  from: String,
  to: String,
  travel_mode: String,
  distance_meters: Number,
  duration_seconds: Number,
  polyline: String,
  steps: [StepSchema]
});

const EventSchema = new mongoose.Schema({
  location_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Location'
  },
  name: String,
  description: String,
  start_time: Date,
  end_time: Date,
  venue_name: String,
  cost: Number,
  sequence_order: Number
});

const AdventureSchema = new mongoose.Schema({
  creator_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: String,
  category: String,
  estimated_duration: Number, // in minutes
  total_distance: Number,
  transport_mode: String,
  times_completed: {
    type: Number,
    default: 0
  },
  fire_score: {
    type: Number,
    default: 0
  },
  average_rating: {
    type: Number,
    default: 0
  },
  events: [EventSchema],
  routes: [RouteSchema],
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  },
  is_public: {
    type: Boolean,
    default: true
  }
});

module.exports = mongoose.model('Adventure', AdventureSchema);