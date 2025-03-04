# Routes App

A React Native mobile application built with Expo for tracking and sharing routes.

## Features

- **Home Screen**: Welcome screen with app information
- **Routes Screen**: Browse available routes
- **Camera**: Take photos during your routes (placeholder implementation)
- **Add Route**: Create and save new routes
- **Your Routes**: View and manage your saved routes

## Getting Started

### Prerequisites

- Node.js (v14 or newer)
- npm or yarn
- Expo CLI

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd RoutesApp
```

2. Install dependencies
```bash
npm install
# or
yarn install
```

3. Start the development server
```bash
npx expo start
```

4. Run on a device or emulator
   - Scan the QR code with the Expo Go app on your mobile device
   - Press 'a' to run on an Android emulator
   - Press 'i' to run on an iOS simulator

## Project Structure

```
RoutesApp/
├── app/
│   ├── (tabs)/
│   │   ├── home/
│   │   ├── routes/
│   │   ├── camera/
│   │   ├── add-route/
│   │   ├── your-routes/
│   │   └── _layout.tsx
│   ├── _layout.tsx
│   └── +not-found.tsx
├── assets/
├── components/
├── constants/
└── hooks/
```

## Technologies Used

- React Native
- Expo
- TypeScript
- React Navigation (Bottom Tabs)

## Future Enhancements

- Implement actual camera functionality
- Add map integration for route visualization
- User authentication and profile management
- Social sharing features
- Route tracking with GPS

## License

This project is licensed under the MIT License - see the LICENSE file for details.
