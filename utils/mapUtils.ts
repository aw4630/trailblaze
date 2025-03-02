import { Linking, Platform } from 'react-native';

// Google Maps API key
export const GOOGLE_MAPS_API_KEY = 'AIzaSyArWxtJ37sM3qBogEo9pG-e4Omv3gDKttw';

export interface RoutePoint {
  id: string;
  title: string;
  description: string;
  latitude: number;
  longitude: number;
}

// Sample route points for demonstration
export const SAMPLE_ROUTE_POINTS: RoutePoint[] = [
  {
    id: '1',
    latitude: 37.7749,
    longitude: -122.4194,
    title: 'San Francisco',
    description: 'Starting point'
  },
  {
    id: '2',
    latitude: 37.8044,
    longitude: -122.2711,
    title: 'Oakland',
    description: 'Second stop'
  },
  {
    id: '3',
    latitude: 37.8715,
    longitude: -122.2730,
    title: 'Berkeley',
    description: 'Third stop'
  },
  {
    id: '4',
    latitude: 37.7575,
    longitude: -122.4369,
    title: 'Golden Gate Park',
    description: 'End point'
  }
];

// Alternative route for variety
export const ALTERNATIVE_ROUTE_POINTS: RoutePoint[] = [
  {
    id: '1',
    latitude: 40.7128,
    longitude: -74.0060,
    title: 'New York',
    description: 'Starting point'
  },
  {
    id: '2',
    latitude: 40.7282,
    longitude: -73.7949,
    title: 'Queens',
    description: 'Second stop'
  },
  {
    id: '3',
    latitude: 40.6782,
    longitude: -73.9442,
    title: 'Brooklyn',
    description: 'Third stop'
  },
  {
    id: '4',
    latitude: 40.7831,
    longitude: -73.9712,
    title: 'Central Park',
    description: 'End point'
  }
];

// Calculate the region for a set of points (for map display)
export const getRegionForPoints = (points: RoutePoint[]) => {
  if (!points || points.length === 0) {
    return null;
  }

  let minLat = points[0].latitude;
  let maxLat = points[0].latitude;
  let minLng = points[0].longitude;
  let maxLng = points[0].longitude;

  // Find the min and max of lat and lng
  points.forEach(point => {
    minLat = Math.min(minLat, point.latitude);
    maxLat = Math.max(maxLat, point.latitude);
    minLng = Math.min(minLng, point.longitude);
    maxLng = Math.max(maxLng, point.longitude);
  });

  const midLat = (minLat + maxLat) / 2;
  const midLng = (minLng + maxLng) / 2;

  // Add some padding
  const latDelta = (maxLat - minLat) * 1.5;
  const lngDelta = (maxLng - minLng) * 1.5;

  return {
    latitude: midLat,
    longitude: midLng,
    latitudeDelta: latDelta || 0.01, // Prevent zero delta
    longitudeDelta: lngDelta || 0.01, // Prevent zero delta
  };
};

// Open the route in Google Maps or Apple Maps
export const openInGoogleMaps = (points: RoutePoint[]) => {
  if (!points || points.length < 2) {
    console.warn('Cannot open maps: Need at least 2 points for a route');
    return;
  }

  // Get origin, destination and waypoints
  const origin = points[0];
  const destination = points[points.length - 1];
  const waypoints = points.slice(1, points.length - 1);

  let url = '';

  if (Platform.OS === 'ios') {
    // Format for iOS (Apple Maps or Google Maps)
    // First try Google Maps
    url = `comgooglemaps://?saddr=${origin.latitude},${origin.longitude}&daddr=${destination.latitude},${destination.longitude}`;
    
    // Add waypoints if any
    if (waypoints.length > 0) {
      const waypointsString = waypoints
        .map(point => `${point.latitude},${point.longitude}`)
        .join('|');
      url += `&waypoints=${waypointsString}`;
    }
    
    url += '&directionsmode=driving';

    // Check if Google Maps is installed, otherwise use Apple Maps
    Linking.canOpenURL(url).then(supported => {
      if (!supported) {
        // Fall back to Apple Maps
        let appleMapsUrl = `http://maps.apple.com/?saddr=${origin.latitude},${origin.longitude}&daddr=${destination.latitude},${destination.longitude}`;
        
        // Apple Maps doesn't support waypoints in the same way, so we'll just add the first one if it exists
        if (waypoints.length > 0) {
          appleMapsUrl += `&daddr=${waypoints[0].latitude},${waypoints[0].longitude}`;
        }
        
        Linking.openURL(appleMapsUrl).catch(err => {
          console.error('Error opening Apple Maps:', err);
        });
      } else {
        Linking.openURL(url).catch(err => {
          console.error('Error opening Google Maps:', err);
        });
      }
    }).catch(err => {
      console.error('Error checking if can open URL:', err);
    });
  } else {
    // Format for Android (Google Maps)
    url = `https://www.google.com/maps/dir/?api=1&origin=${origin.latitude},${origin.longitude}&destination=${destination.latitude},${destination.longitude}`;
    
    // Add waypoints if any
    if (waypoints.length > 0) {
      const waypointsString = waypoints
        .map(point => `${point.latitude},${point.longitude}`)
        .join('|');
      url += `&waypoints=${waypointsString}`;
    }
    
    url += '&travelmode=driving';
    
    // Add API key
    url += `&key=${GOOGLE_MAPS_API_KEY}`;
    
    Linking.openURL(url).catch(err => {
      console.error('Error opening Google Maps:', err);
    });
  }
}; 