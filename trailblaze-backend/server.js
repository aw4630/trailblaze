const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const connectDB = require('./config/db');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Connect to MongoDB
connectDB();

// Initialize Express
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/users', require('./routes/userRoutes'));
app.use('/api/adventures', require('./routes/adventureRoutes'));
app.use('/api/locations', require('./routes/locationRoutes'));
app.use('/api/ratings', require('./routes/ratingRoutes'));

// Default route
app.get('/', (req, res) => {
  res.send('Adventure App API is running');
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send({ message: 'Something went wrong!', error: err.message });
});

// Start server
const PORT = process.env.PORT || 3000; // Permanently using port 3000
const server = app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});