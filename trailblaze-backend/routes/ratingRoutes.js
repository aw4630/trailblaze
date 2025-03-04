const express = require('express');
const router = express.Router();
const ratingController = require('../controllers/ratingController');
const auth = require('../middleware/auth');

// @route   POST /api/ratings/:adventureId
// @desc    Rate an adventure
// @access  Private
router.post('/:adventureId', auth, ratingController.rateAdventure);

// @route   GET /api/ratings/:adventureId
// @desc    Get all ratings for an adventure
// @access  Public
router.get('/:adventureId', ratingController.getAdventureRatings);

// @route   POST /api/ratings/:adventureId/like
// @desc    Like an adventure
// @access  Private
router.post('/:adventureId/like', auth, ratingController.likeAdventure);

// @route   GET /api/ratings/:adventureId/like
// @desc    Check if user liked an adventure
// @access  Private
router.get('/:adventureId/like', auth, ratingController.checkLikeStatus);

module.exports = router;