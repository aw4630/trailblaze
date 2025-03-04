const mongoose = require('mongoose');

const CheckInSchema = new mongoose.Schema({
  location_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Location'
  },
  arrival_time: Date,
  departure_time: Date,
  completed: {
    type: Boolean,
    default: false
  },
  photo_references: [String] // Supabase storage paths
});

const AdventureCompletionSchema = new mongoose.Schema({
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
  start_time: Date,
  end_time: Date,
  completed: {
    type: Boolean,
    default: false
  },
  distance_traveled: {
    type: Number,
    default: 0
  },
  money_spent: {
    type: Number,
    default: 0
  },
  check_ins: [CheckInSchema],
  created_at: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('AdventureCompletion', AdventureCompletionSchema);