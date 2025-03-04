# Trailblaze Backend

This is the backend API for the Trailblaze mobile application, a platform for creating, sharing, and discovering adventure itineraries.

## Technology Stack

- **Node.js & Express**: Server framework
- **MongoDB**: Database for storing user data, adventures, locations, and more
- **Mongoose**: ODM (Object Data Modeling) for MongoDB
- **JWT**: Authentication
- **Supabase**: For file storage

## Features

- User authentication and profiles
- Adventure creation and management
- Location data with geospatial queries
- Rating and like system for adventures
- Database utilities and testing scripts

## Project Structure

```
trailblaze-backend/
├── config/              # Configuration files
├── controllers/         # Controller logic
├── middleware/          # Express middleware
├── models/              # Mongoose models
├── routes/              # Express routes
├── scripts/             # Utility scripts
├── utils/               # Utility functions
├── .env                 # Environment variables (not in repo)
├── .gitignore           # Git ignore file
├── package.json         # Package manifest
├── package-lock.json    # Package lock
└── server.js            # Main server file
```

## API Endpoints

- **Auth:** /api/auth/register, /api/auth/login
- **Users:** /api/users
- **Adventures:** /api/adventures
- **Locations:** /api/locations
- **Ratings:** /api/ratings

## Getting Started

### Prerequisites

- Node.js (v14+)
- MongoDB Atlas account or local MongoDB installation
- Supabase account (for file storage)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with the following variables:
   ```
   PORT=3000
   JWT_SECRET=your_jwt_secret
   MONGODB_URI=your_mongodb_connection_string
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```
4. Start the server:
   ```
   npm start
   ```

### Database Scripts

- Test connection: `node scripts/test-db-connection.js`
- Insert sample data: `node scripts/insert-sample-itinerary.js`
- Verify sample data: `node scripts/verify-sample-itinerary.js` 