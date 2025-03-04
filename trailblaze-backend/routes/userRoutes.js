const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');

// @route   GET /api/users/profile
// @desc    Get current user profile
// @access  Private
router.get('/profile', auth, userController.getUserProfile);

// @route   GET /api/users/:userId
// @desc    Get user profile by ID
// @access  Public
router.get('/:userId', userController.getUserProfile);

// @route   PUT /api/users/profile
// @desc    Update user profile
// @access  Private
router.put('/profile', auth, userController.updateUserProfile);

// @route   GET /api/users/adventures
// @desc    Get current user's created adventures
// @access  Private
router.get('/adventures', auth, userController.getUserAdventures);

// @route   GET /api/users/:userId/adventures
// @desc    Get a user's created adventures by ID
// @access  Public
router.get('/:userId/adventures', userController.getUserAdventures);

// @route   GET /api/users/completions
// @desc    Get current user's completed adventures
// @access  Private
router.get('/completions', auth, userController.getUserCompletions);

// @route   GET /api/users/:userId/completions
// @desc    Get a user's completed adventures by ID
// @access  Public
router.get('/:userId/completions', userController.getUserCompletions);

module.exports = router;