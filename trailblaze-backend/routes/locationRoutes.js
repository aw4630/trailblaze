const express = require('express');
const router = express.Router();
const locationController = require('../controllers/locationController');
const auth = require('../middleware/auth');
const upload = require('../middleware/upload');

// @route   GET /api/locations
// @desc    Get all locations
// @access  Public
router.get('/', locationController.getAllLocations);

// @route   GET /api/locations/search
// @desc    Search for locations
// @access  Public
router.get('/search', locationController.searchLocations);

// @route   GET /api/locations/:locationId
// @desc    Get location by ID
// @access  Public
router.get('/:locationId', locationController.getLocationById);

// @route   POST /api/locations/:locationId/photos
// @desc    Upload a photo for a location
// @access  Private
router.post('/:locationId/photos', auth, upload.single('photo'), locationController.uploadLocationPhoto);

// @route   GET /api/locations/:locationId/photos
// @desc    Get all photos for a location
// @access  Public
router.get('/:locationId/photos', locationController.getLocationPhotos);

module.exports = router;