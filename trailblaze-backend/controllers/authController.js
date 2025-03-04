const User = require('../models/User');
const jwt = require('jsonwebtoken');

// Register a new user
const register = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // Check if user already exists
    const existingEmail = await User.findOne({ email });
    if (existingEmail) {
      return res.status(400).json({ message: 'Email already in use' });
    }
    
    const existingUsername = await User.findOne({ username });
    if (existingUsername) {
      return res.status(400).json({ message: 'Username already in use' });
    }
    
    // Create new user
    const user = new User({
      username,
      email,
      password
    });
    
    await user.save();
    
    // Create JWT token
    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, {
      expiresIn: '30d'
    });
    
    res.status(201).json({
      success: true,
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Login user
const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Check if user exists
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    // Check password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    // Create JWT token
    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, {
      expiresIn: '30d'
    });
    
    // Update last login
    user.updated_at = Date.now();
    await user.save();
    
    res.json({
      success: true,
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get current user
const getCurrentUser = async (req, res) => {
  try {
    // User is already attached to req by auth middleware
    res.json({
      success: true,
      user: req.user
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

module.exports = {
  register,
  login,
  getCurrentUser
};