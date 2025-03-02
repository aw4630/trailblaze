import React, { useState, useEffect } from 'react';
import { StyleSheet, View, TouchableOpacity, Text, Platform, Image } from 'react-native';
import { RoutePoint, GOOGLE_MAPS_API_KEY, getRegionForPoints, openInGoogleMaps } from '../utils/mapUtils';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

// Only import MapView components if not in Expo Go
let MapView: any = null;
let Marker: any = null;
let PROVIDER_GOOGLE: any = null;
let MapViewDirections: any = null;

// We need to check if we're in Expo Go before importing these components
const isExpoGo = Constants.appOwnership === 'expo';

if (!isExpoGo) {
  // Only import these if not in Expo Go
  const MapImports = require('react-native-maps');
  MapView = MapImports.default;
  Marker = MapImports.Marker;
  PROVIDER_GOOGLE = MapImports.PROVIDER_GOOGLE;
  MapViewDirections = require('react-native-maps-directions').default;
}

interface RouteMapProps {
  points: RoutePoint[];
  editable?: boolean;
  onPointPress?: (point: RoutePoint) => void;
  onMapPress?: (event: { nativeEvent: { coordinate: { latitude: number; longitude: number } } }) => void;
}

const RouteMap: React.FC<RouteMapProps> = ({ 
  points, 
  editable = false,
  onPointPress,
  onMapPress
}) => {
  const [mapReady, setMapReady] = useState(false);
  
  const initialRegion = getRegionForPoints(points) || {
    latitude: 37.78825,
    longitude: -122.4324,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  };

  const handleOpenInMaps = () => {
    openInGoogleMaps(points);
  };

  // Generate a static map URL for the fallback
  const getStaticMapUrl = () => {
    if (!points || points.length < 2) return null;
    
    // Base URL for Google Static Maps API
    let url = `https://maps.googleapis.com/maps/api/staticmap?size=600x300&scale=2`;
    
    // Add markers for each point
    points.forEach((point, index) => {
      const color = index === 0 ? 'green' : index === points.length - 1 ? 'red' : 'blue';
      url += `&markers=color:${color}|label:${index + 1}|${point.latitude},${point.longitude}`;
    });
    
    // Add path between points - linear path, not a loop
    const path = points.map(point => `${point.latitude},${point.longitude}`).join('|');
    url += `&path=color:0x6200eeCC|weight:5|${path}`;
    
    // Add API key
    url += `&key=${GOOGLE_MAPS_API_KEY}`;
    
    return url;
  };

  // Enhanced fallback component with static map image
  const MapFallback = () => {
    const staticMapUrl = getStaticMapUrl();
    
    return (
      <View style={styles.fallbackContainer}>
        {staticMapUrl ? (
          <Image 
            source={{ uri: staticMapUrl }} 
            style={styles.staticMap}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.noMapContainer}>
            <Ionicons name="map" size={50} color="#8900e1" />
            <Text style={styles.fallbackTitle}>Map Preview</Text>
          </View>
        )}
        
        <View style={styles.routeInfoContainer}>
          <Text style={styles.fallbackTitle}>
            {points.length > 0 ? 'Route Preview' : 'No Route Available'}
          </Text>
          
          <Text style={styles.fallbackText}>
            {points.length > 0 
              ? `${points.length} points from ${points[0].title} to ${points[points.length - 1].title}`
              : 'No route points available'}
          </Text>
          
          {points.length >= 2 && (
            <TouchableOpacity style={styles.openButton} onPress={handleOpenInMaps}>
              <Ionicons name="navigate" size={20} color="white" />
              <Text style={styles.openButtonText}>Open in Maps</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  // Always use fallback in Expo Go
  if (isExpoGo) {
    return <MapFallback />;
  }

  // If we're not in Expo Go but the map components didn't load
  if (!MapView || !Marker || !PROVIDER_GOOGLE || !MapViewDirections) {
    return <MapFallback />;
  }

  // Only render the actual map if we're not in Expo Go
  return (
    <View style={styles.container}>
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        initialRegion={initialRegion}
        onMapReady={() => setMapReady(true)}
        onPress={editable ? onMapPress : undefined}
      >
        {mapReady && points.map((point, index) => (
          <Marker
            key={point.id}
            coordinate={{
              latitude: point.latitude,
              longitude: point.longitude
            }}
            title={point.title}
            description={point.description}
            pinColor={index === 0 ? 'green' : index === points.length - 1 ? 'red' : 'blue'}
            onPress={() => onPointPress && onPointPress(point)}
          />
        ))}
        
        {mapReady && points.length >= 2 && (
          <MapViewDirections
            origin={{
              latitude: points[0].latitude,
              longitude: points[0].longitude
            }}
            destination={{
              latitude: points[points.length - 1].latitude,
              longitude: points[points.length - 1].longitude
            }}
            waypoints={points.slice(1, points.length - 1).map(point => ({
              latitude: point.latitude,
              longitude: point.longitude
            }))}
            apikey={GOOGLE_MAPS_API_KEY}
            strokeWidth={4}
            strokeColor="#6200ee"
            optimizeWaypoints={true}
          />
        )}
      </MapView>
      
      {points.length >= 2 && (
        <TouchableOpacity style={styles.openButton} onPress={handleOpenInMaps}>
          <Ionicons name="navigate" size={20} color="white" />
          <Text style={styles.openButtonText}>Open in Maps</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 300,
    width: '100%',
    borderRadius: 12,
    overflow: 'hidden',
    marginVertical: 10,
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  openButton: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    backgroundColor: '#6200ee',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  openButtonText: {
    color: 'white',
    marginLeft: 8,
    fontWeight: '600',
  },
  fallbackContainer: {
    height: 300,
    width: '100%',
    borderRadius: 12,
    overflow: 'hidden',
    marginVertical: 10,
    backgroundColor: '#f5f5f5',
  },
  staticMap: {
    width: '100%',
    height: 200,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  noMapContainer: {
    height: 200,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e0e0e0',
  },
  routeInfoContainer: {
    padding: 16,
    backgroundColor: '#f5f5f5',
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  fallbackTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  fallbackText: {
    fontSize: 14,
    textAlign: 'center',
    color: '#666',
    marginBottom: 12,
  },
});

export default RouteMap; 