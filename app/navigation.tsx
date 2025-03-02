import { StyleSheet, Text, View, SafeAreaView, ScrollView, TouchableOpacity, Alert, Image, ActivityIndicator } from 'react-native';
import React, { useState, useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { IconSymbol } from '@/components/ui/IconSymbol';
import * as Location from 'expo-location';
import { CameraView, useCameraPermissions, CameraCapturedPicture } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import ConfettiCannon from 'react-native-confetti-cannon';

// Define types
type Landmark = {
  id: string;
  name: string;
  description: string;
  // For now, all landmarks will have the same coordinates
  latitude: number;
  longitude: number;
};

type Transportation = {
  from: string;
  to: string;
  mode: any; // Using any type to avoid type errors with SF Symbols
  label: string;
};

export default function NavigationScreen() {
  const { landmarks, transportation, routeName } = useLocalSearchParams();
  const router = useRouter();
  const [currentLandmarkIndex, setCurrentLandmarkIndex] = useState(0);
  const [locationPermission, setLocationPermission] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImages, setCapturedImages] = useState<{[key: string]: string}>({});
  const [permission, requestCameraPermission] = useCameraPermissions();
  const [takingPicture, setTakingPicture] = useState(false);
  const [mediaLibraryPermission, requestMediaLibraryPermission] = MediaLibrary.usePermissions();
  const [cameraReady, setCameraReady] = useState(false);
  const cameraRef = useRef<any>(null);
  const [routeCompleted, setRouteCompleted] = useState(false);
  
  // Add these hooks at the component level, not inside conditional rendering
  const [confettiKey, setConfettiKey] = useState(0);
  
  // Function to trigger confetti again - defined at component level
  const triggerConfetti = () => {
    setConfettiKey(prevKey => prevKey + 1);
  };
  
  // Parse the landmarks and transportation data from URL params
  const parsedLandmarks: Landmark[] = landmarks ? 
    JSON.parse(decodeURIComponent(landmarks as string)).map((landmark: any) => ({
      ...landmark,
      // Hard-coding coordinates for all landmarks for now
      latitude: 40.7294658334865,
      longitude: -73.99721621734324
    })) : [];
    
  const parsedTransportation: Transportation[] = transportation ? 
    JSON.parse(decodeURIComponent(transportation as string)) : [];
  
  // Request permissions on component mount
  useEffect(() => {
    (async () => {
      // Request location permission
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(locationStatus === 'granted');
      
      // Request camera permission if not already requested
      if (!permission) {
        await requestCameraPermission();
      }
      
      // Request media library permission
      if (!mediaLibraryPermission?.granted) {
        await requestMediaLibraryPermission();
      }
    })();
  }, [permission, requestCameraPermission, mediaLibraryPermission, requestMediaLibraryPermission]);
  
  // Function to calculate distance between two coordinates in meters
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // Distance in meters
  };
  
  // Function to handle taking a photo
  const takePicture = async () => {
    try {
      if (showCamera && cameraReady && cameraRef.current) {
        setTakingPicture(true);
        
        try {
          // Use the actual camera to take a picture
          const photo = await cameraRef.current.takePictureAsync();
          console.log("Photo captured:", photo.uri);
          
          const currentLandmark = parsedLandmarks[currentLandmarkIndex];
          
          // Save the photo URI for this landmark
          setCapturedImages(prev => ({
            ...prev,
            [currentLandmark.id]: photo.uri
          }));
          
          // Hide camera after taking picture
          setShowCamera(false);
          
          // Move to next landmark if available
          if (currentLandmarkIndex < parsedLandmarks.length - 1) {
            setCurrentLandmarkIndex(currentLandmarkIndex + 1);
            Alert.alert('Success!', 'Photo captured. Navigate to the next landmark.');
          } else {
            // All landmarks have been visited and photographed
            setRouteCompleted(true);
          }
        } catch (error) {
          console.error('Error taking picture with camera:', error);
          
          // Fallback to using the local image if camera fails
          const currentLandmark = parsedLandmarks[currentLandmarkIndex];
          const fallbackUri = FileSystem.documentDirectory + 'captured-photo.jpg';
          
          // Copy our local asset to a location we can access
          await FileSystem.copyAsync({
            from: require('@/assets/images/captured-photo.jpg'),
            to: fallbackUri
          });
          
          setCapturedImages(prev => ({
            ...prev,
            [currentLandmark.id]: fallbackUri
          }));
          
          Alert.alert('Camera Issue', 'Using a sample photo instead. Your progress has been saved.');
          
          // Hide camera after taking picture
          setShowCamera(false);
          
          // Move to next landmark if available
          if (currentLandmarkIndex < parsedLandmarks.length - 1) {
            setCurrentLandmarkIndex(currentLandmarkIndex + 1);
          } else {
            // All landmarks have been visited and photographed
            setRouteCompleted(true);
          }
        } finally {
          setTakingPicture(false);
        }
      } else if (!cameraReady) {
        Alert.alert('Camera not ready', 'Please wait for the camera to initialize.');
      } else if (!cameraRef.current) {
        Alert.alert('Camera not available', 'Camera reference is not available.');
      }
    } catch (error) {
      console.error('Error in takePicture function:', error);
      Alert.alert('Error', 'Failed to take picture. Please try again.');
      setTakingPicture(false);
      setShowCamera(false);
    }
  };
  
  // Function to handle "I am here" button press
  const handleIAmHere = async () => {
    if (!locationPermission) {
      Alert.alert(
        "Permission Required",
        "Location permission is needed to verify your position.",
        [
          { text: "Cancel", style: "cancel" },
          { text: "Settings", onPress: () => Location.requestForegroundPermissionsAsync() }
        ]
      );
      return;
    }
    
    try {
      // Get current location
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Highest
      });
      
      const currentLandmark = parsedLandmarks[currentLandmarkIndex];
      const distance = calculateDistance(
        location.coords.latitude,
        location.coords.longitude,
        currentLandmark.latitude,
        currentLandmark.longitude
      );
      
      // Check if user is within 150 meters of the landmark
      if (distance <= 150) {
        // User is at the landmark
        if (!permission?.granted) {
          Alert.alert(
            "Permission Required",
            "Camera permission is needed to take a photo of the landmark.",
            [
              { text: "Cancel", style: "cancel" },
              { text: "Settings", onPress: requestCameraPermission }
            ]
          );
          return;
        }
        
        // Open camera
        setShowCamera(true);
      } else {
        // User is not at the landmark
        Alert.alert(
          "Not Close Enough",
          `You are ${Math.round(distance)} meters away from ${currentLandmark.name}. Please get closer (within 150 meters) to proceed.`
        );
      }
    } catch (error) {
      console.error("Error getting location:", error);
      Alert.alert("Error", "Failed to get your location. Please try again.");
    }
  };

  // Separate component for the congratulations screen
  const CongratsScreen = () => (
    <SafeAreaView style={styles.congratsContainer}>
      <StatusBar style="light" />
      <View style={styles.congratsContent}>
        <ConfettiCannon
          key={`confetti-left-${confettiKey}`}
          count={200}
          origin={{x: -10, y: 0}}
          autoStart={true}
          fadeOut={true}
          fallSpeed={3000}
          explosionSpeed={350}
          colors={['#8900e1', '#a347e8', '#b978ed', '#d2a9f3', '#e6d9f9', '#ffffff']}
        />
        <ConfettiCannon
          key={`confetti-right-${confettiKey}`}
          count={200}
          origin={{x: 400, y: 0}}
          autoStart={true}
          fadeOut={true}
          fallSpeed={3000}
          explosionSpeed={350}
          colors={['#8900e1', '#a347e8', '#b978ed', '#d2a9f3', '#e6d9f9', '#ffffff']}
        />
        
        <View style={styles.congratsBadge}>
          <Ionicons name="checkmark-circle" size={100} color="#8900e1" />
        </View>
        
        <Text style={styles.congratsTitle}>Congratulations!</Text>
        <Text style={styles.congratsText}>
          You've successfully completed the route "{routeName ? decodeURIComponent(routeName as string) : "Tour"}"
        </Text>
        <Text style={styles.congratsSubtext}>
          All your photos have been captured and saved.
        </Text>
        
        <View style={styles.photoGrid}>
          {Object.entries(capturedImages).map(([id, uri], index) => (
            <View key={id} style={styles.photoThumbnailContainer}>
              <Image 
                source={typeof uri === 'string' ? { uri } : uri}
                style={styles.photoThumbnail}
              />
              <Text style={styles.photoThumbnailLabel}>
                {parsedLandmarks.find(l => l.id === id)?.name || id}
              </Text>
            </View>
          ))}
        </View>
        
        <TouchableOpacity 
          style={styles.celebrateButton}
          onPress={triggerConfetti}
        >
          <Ionicons name="sparkles" size={24} color="#fff" />
          <Text style={styles.celebrateButtonText}>Celebrate Again!</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.homeButton}
          onPress={() => router.push('/')}
        >
          <Ionicons name="home" size={24} color="#fff" />
          <Text style={styles.homeButtonText}>Return to Home</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );

  // Camera view component
  const CameraScreenView = () => (
    <View style={styles.cameraContainer}>
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="back"
        onMountError={(error) => {
          console.error('Camera mount error:', error);
          Alert.alert('Camera Error', 'Failed to start camera. Please try again.');
          setShowCamera(false);
        }}
        onCameraReady={() => setCameraReady(true)}
      >
        <View style={styles.cameraControlsContainer}>
          <TouchableOpacity
            style={styles.closeCameraButton}
            onPress={() => setShowCamera(false)}
          >
            <Ionicons name="close-circle" size={32} color="white" />
          </TouchableOpacity>
          
          {takingPicture ? (
            <View style={styles.takingPictureContainer}>
              <ActivityIndicator size="large" color="#ffffff" />
              <Text style={styles.takingPictureText}>Taking picture...</Text>
            </View>
          ) : (
            <View style={styles.captureButtonContainer}>
              <TouchableOpacity
                style={styles.captureButton}
                onPress={takePicture}
                disabled={!cameraReady}
              >
                <View style={styles.captureButtonInner} />
              </TouchableOpacity>
            </View>
          )}
        </View>
      </CameraView>
    </View>
  );

  // Main navigation view
  const NavigationView = () => (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ 
        title: routeName ? decodeURIComponent(routeName as string) : "Active Navigation",
        headerStyle: {
          backgroundColor: '#8900e1',
        },
        headerTintColor: '#fff',
      }} />
      <StatusBar style="light" />
      
      <View style={styles.headerContainer}>
        <Text style={styles.headerTitle}>Follow Your Route</Text>
        <Text style={styles.headerSubtitle}>
          {currentLandmarkIndex + 1} of {parsedLandmarks.length} landmarks
        </Text>
      </View>
      
      <ScrollView style={styles.scrollView}>
        <View style={styles.landmarkPathContainer}>
          {parsedLandmarks.map((landmark, index) => {
            const isActive = index === currentLandmarkIndex;
            const isPast = index < currentLandmarkIndex;
            const isFuture = index > currentLandmarkIndex;
            const hasImage = capturedImages[landmark.id];
            
            return (
              <View key={landmark.id}>
                <View style={styles.landmarkItem}>
                  <View style={styles.landmarkConnector}>
                    <View style={[
                      styles.landmarkDot,
                      isPast && styles.landmarkDotPast,
                      isActive && styles.landmarkDotActive,
                      isFuture && styles.landmarkDotFuture
                    ]} />
                    {index < parsedLandmarks.length - 1 && (
                      <View style={[
                        styles.landmarkLine,
                        isPast && styles.landmarkLinePast,
                        isFuture && styles.landmarkLineFuture
                      ]} />
                    )}
                  </View>
                  <View style={[
                    styles.landmarkContent,
                    isActive && styles.landmarkContentActive
                  ]}>
                    <Text style={styles.landmarkId}>{landmark.id}</Text>
                    <View style={styles.landmarkTextContainer}>
                      <Text style={[
                        styles.landmarkName,
                        isActive && styles.landmarkNameActive
                      ]}>{landmark.name}</Text>
                      <Text style={styles.landmarkDescription}>{landmark.description}</Text>
                      
                      {/* Show captured image if available */}
                      {hasImage && (
                        <View>
                          <Image 
                            source={typeof hasImage === 'string' ? { uri: hasImage } : hasImage}
                            style={styles.landmarkImage}
                            onError={(e) => console.error("Image loading error:", e.nativeEvent.error)}
                          />
                          <Text style={styles.photoCaption}>Your photo of this landmark</Text>
                        </View>
                      )}
                    </View>
                  </View>
                  
                  {/* Transportation mode to the right of landmark */}
                  {index < parsedLandmarks.length - 1 && (
                    <View style={styles.transportationContainer}>
                      <View style={styles.transportationIconContainer}>
                        {parsedTransportation.find(t => t.from === landmark.id && t.to === parsedLandmarks[index + 1].id) && (
                          <IconSymbol 
                            size={18} 
                            name={parsedTransportation.find(t => t.from === landmark.id && t.to === parsedLandmarks[index + 1].id)?.mode || 'figure.walk'} 
                            color="#8900e1" 
                          />
                        )}
                      </View>
                      <Text style={styles.transportationText}>
                        {parsedTransportation.find(t => t.from === landmark.id && t.to === parsedLandmarks[index + 1].id)?.label || 'Walking'}
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>
      
      <View style={styles.bottomContainer}>
        <TouchableOpacity 
          style={styles.iAmHereButton}
          onPress={handleIAmHere}
        >
          <IconSymbol size={24} name="location.fill" color="#fff" />
          <Text style={styles.iAmHereButtonText}>I am here</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );

  // Render the appropriate screen based on state
  if (routeCompleted) {
    return <CongratsScreen />;
  }

  if (showCamera) {
    return <CameraScreenView />;
  }

  return <NavigationView />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f8f8',
  },
  headerContainer: {
    padding: 16,
    backgroundColor: '#8900e1',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  scrollView: {
    flex: 1,
  },
  landmarkPathContainer: {
    padding: 16,
  },
  landmarkItem: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  landmarkConnector: {
    width: 24,
    alignItems: 'center',
    marginRight: 12,
  },
  landmarkDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#ccc',
    zIndex: 1,
  },
  landmarkDotPast: {
    backgroundColor: '#8900e1',
  },
  landmarkDotActive: {
    backgroundColor: '#8900e1',
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 3,
    borderColor: '#f0e0ff',
  },
  landmarkDotFuture: {
    backgroundColor: '#ddd',
  },
  landmarkLine: {
    width: 2,
    flex: 1,
    backgroundColor: '#ddd',
    position: 'absolute',
    top: 16,
    bottom: -20,
    left: 11,
  },
  landmarkLinePast: {
    backgroundColor: '#8900e1',
  },
  landmarkLineFuture: {
    backgroundColor: '#ddd',
  },
  landmarkContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  landmarkContentActive: {
    borderWidth: 2,
    borderColor: '#8900e1',
    backgroundColor: '#f9f5ff',
  },
  landmarkId: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#8900e1',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 24,
    fontWeight: 'bold',
    marginRight: 12,
  },
  landmarkTextContainer: {
    flex: 1,
  },
  landmarkName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  landmarkNameActive: {
    color: '#8900e1',
  },
  landmarkDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  landmarkImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginTop: 8,
    resizeMode: 'cover',
    backgroundColor: '#f0f0f0', // Add a background color to make it visible even when loading
  },
  transportationContainer: {
    marginLeft: 12,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
  transportationIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0e0ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  transportationText: {
    fontSize: 12,
    color: '#8900e1',
    fontWeight: '500',
  },
  bottomContainer: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  iAmHereButton: {
    backgroundColor: '#8900e1',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iAmHereButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  // Camera styles
  cameraContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  cameraControlsContainer: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
  captureButtonContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 5,
    borderColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  captureButtonInner: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#fff',
  },
  closeCameraButton: {
    alignSelf: 'flex-start',
    margin: 20,
    marginTop: 50,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0,0,0,0.6)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  takingPictureContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  takingPictureText: {
    color: 'white',
    marginTop: 10,
    fontSize: 16,
  },
  photoCaption: {
    fontSize: 12,
    color: '#8900e1',
    fontStyle: 'italic',
    marginTop: 4,
    textAlign: 'center',
  },
  // Congratulations screen styles
  congratsContainer: {
    flex: 1,
    backgroundColor: '#f9f5ff',
  },
  congratsContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    overflow: 'hidden', // Ensure confetti doesn't cause scrolling
  },
  congratsBadge: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f0e0ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    shadowColor: '#8900e1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  congratsTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#8900e1',
    marginBottom: 16,
    textAlign: 'center',
    textShadowColor: 'rgba(137, 0, 225, 0.2)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  congratsText: {
    fontSize: 18,
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
    lineHeight: 24,
  },
  congratsSubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  photoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: 30,
  },
  photoThumbnailContainer: {
    margin: 8,
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  photoThumbnail: {
    width: 100,
    height: 100,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8900e1',
  },
  photoThumbnailLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
    maxWidth: 100,
  },
  celebrateButton: {
    backgroundColor: '#a347e8',
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    marginBottom: 12,
  },
  celebrateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  homeButton: {
    backgroundColor: '#8900e1',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    marginTop: 8,
  },
  homeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
}); 