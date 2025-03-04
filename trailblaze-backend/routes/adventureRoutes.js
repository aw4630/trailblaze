const express = require('express');
const router = express.Router();
const adventureController = require('../controllers/adventureController');
const auth = require('../middleware/auth');

// @route   POST /api/adventures
// @desc    Create a new adventure
// @access  Private
router.post('/', auth, adventureController.createAdventure);

// @route   GET /api/adventures
// @desc    Get all public adventures
// @access  Public
router.get('/', adventureController.getPublicAdventures);

// @route   GET /api/adventures/:adventureId
// @desc    Get adventure by ID
// @access  Public/Private (depends if adventure is public)
router.get('/:adventureId', adventureController.getAdventureById);

// @route   POST /api/adventures/:adventureId/start
// @desc    Start an adventure
// @access  Private
router.post('/:adventureId/start', auth, adventureController.startAdventure);

// @route   POST /api/adventures/check-in
// @desc    Check in at a location
// @access  Private
router.post('/check-in', auth, adventureController.checkInLocation);

// @route   PUT /api/adventures/completions/:completionId
// @desc    Complete an adventure
// @access  Private
router.put('/completions/:completionId', auth, adventureController.completeAdventure);

module.exports = router;