<<<<<<< HEAD
=======
# arvisiondemo
ar vision camera part of Trailblaze (buildathon 2025)

>>>>>>> 1aaf6bc3bfcdbca027b7916f4518de47bc4a8c48
# Trailblaze - AR Landmark Recognition App

A React Native application built with Expo that captures photos, detects landmarks using Claude AI, and stores verified landmarks in Supabase.

## Features

- Camera integration with permission handling
- Location-based photo captures
- Landmark recognition using Claude AI
- Verified landmark storage in Supabase
- Modern, intuitive user interface
- Cross-platform (iOS and Android)

## How It Works

1. User takes a photo of a landmark using the app
2. Claude AI analyzes the image to identify the landmark or location
3. If a landmark is recognized, it's saved to Supabase with location data
4. The photo gallery displays all verified landmarks with their information

## Requirements

- iOS device with iOS 13.0+
- Android device with Android 6.0+
- Expo Go app installed on your device
- Claude AI API key
- Supabase account and project setup

## Supabase Setup

1. Create a new Supabase project at https://supabase.io
2. Create a storage bucket named `landmarks`
3. Create a table named `landmark_records` with the following structure:
   ```sql
   CREATE TABLE landmark_records (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     image_url TEXT NOT NULL,
     landmark_name TEXT NOT NULL,
     latitude NUMERIC,
     longitude NUMERIC,
     captured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```
4. Set up appropriate storage and database policies
5. Update the `environment.js` file with your Supabase URL and anon key

## Claude AI Setup

1. Sign up for Claude API access at https://anthropic.com
2. Generate an API key
3. Add your API key to the `environment.js` file

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Configure API keys in `environment.js`
4. Start the Expo development server:
   ```
   npx expo start
   ```
5. Scan the QR code with your iOS/Android device using the Expo Go app

## Usage

1. Launch the app
2. Tap "Start Experience" button
3. Point your camera at a landmark
4. Tap the capture button to take a photo
5. Wait for Claude AI to analyze the landmark
6. View verified landmarks in your gallery

## Technologies Used

- React Native
- Expo
- Expo Camera
- Expo Location
- Claude AI API for image analysis
- Supabase for storage and database
- React Native Animations

## Development Notes

This project demonstrates how AI-based image recognition can be integrated with mobile applications to create engaging user experiences. The landmark verification process could be extended with:

- Custom landmark databases for specific regions
- User-contributed landmark information
- AR overlays with historical information
- Social sharing capabilities
- Map views of all captured landmarks

## License

<<<<<<< HEAD
MIT 
=======
MIT 
>>>>>>> 1aaf6bc3bfcdbca027b7916f4518de47bc4a8c48
