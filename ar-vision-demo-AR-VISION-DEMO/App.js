import React, { useState, useEffect, useRef } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  SafeAreaView, 
  Image,
  Animated,
  Platform,
  Alert,
  ScrollView,
  Modal,
  ActivityIndicator
} from 'react-native';
import { CameraView } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as Location from 'expo-location';
import { StatusBar } from 'expo-status-bar';
import * as FileSystem from 'expo-file-system';
import * as ImageManipulator from 'expo-image-manipulator';
import { createClient } from '@supabase/supabase-js';
import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { EXPO_PUBLIC_SUPABASE_URL, EXPO_PUBLIC_SUPABASE_ANON_KEY } from '@env';
import { Camera } from 'expo-camera';

// Initialize Supabase client
const supabaseUrl = EXPO_PUBLIC_SUPABASE_URL;
// Using service role key to bypass RLS policies
const supabaseKey = EXPO_PUBLIC_SUPABASE_ANON_KEY;

console.log('Using Supabase URL:', supabaseUrl);
console.log('Supabase key length:', supabaseKey?.length);

// Initialize the Supabase client directly without try/catch or fallbacks
const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  }
});

// Simulate a user ID (in a real app, this would come from authentication)
const userId = "user_" + Math.random().toString(36).substring(2, 10);

// Replace the hardcoded API key with an environment variable
const ANTHROPIC_API_KEY = process.env.EXPO_PUBLIC_ANTHROPIC_API_KEY;

export default function App() {
  const [cameraPermission, setCameraPermission] = useState(null);
  const [mediaLibraryPermission, setMediaLibraryPermission] = useState(true);
  const [locationPermission, setLocationPermission] = useState(true);
  const [showARScreen, setShowARScreen] = useState(false);
  const [location, setLocation] = useState(null);
  const [photoTaken, setPhotoTaken] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [cameraType, setCameraType] = useState('back');
  const [flashMode, setFlashMode] = useState('off');
  const [analyzeResults, setAnalyzeResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLandmark, setIsLandmark] = useState(false);
  const [landmarkDetails, setLandmarkDetails] = useState(null);
  const [showLandmarkModal, setShowLandmarkModal] = useState(false);
  const [landmarkName, setLandmarkName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isTakingPhoto, setIsTakingPhoto] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  
  const cameraRef = useRef(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Get location when component mounts
  useEffect(() => {
    const requestLocationPermission = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(status === 'granted');
      
      if (status === 'granted') {
        try {
          const location = await Location.getCurrentPositionAsync({});
          setLocation(location);
        } catch (error) {
          console.log('Error getting location even with permission:', error);
        }
      }
    };
    
    requestLocationPermission();
  }, []);

  useEffect(() => {
    if (showARScreen) {
      // Animate text when screen is shown
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }).start();
    }
  }, [showARScreen, fadeAnim]);

  // First, add a useEffect to check if the bucket exists on component mount
  useEffect(() => {
    // Set a flag to avoid excessive alerts during development
    let alertShown = false;
    
    // Check if the Supabase connection is working and the bucket exists
    const checkSupabaseConnection = async () => {
      try {
        console.log('Checking Supabase connection...');
        
        // Add a timeout to abort if it takes too long
        const connectionPromise = new Promise(async (resolve, reject) => {
          try {
            // First test a simple query to check database connection
            const { data: testData, error: testError } = await supabase
              .from('photos')
              .select('photo_id')
              .limit(1);
              
            if (testError) {
              console.error('Database connection test failed:', testError);
              reject(new Error(`Database connection failed: ${testError.message}`));
              return;
            }
            
            console.log('Database connection successful');
            
            // Then check if the bucket exists
            const { data: buckets, error: bucketsError } = await supabase
              .storage
              .listBuckets();
              
            if (bucketsError) {
              console.error('Could not list buckets:', bucketsError);
              reject(new Error(`Storage access failed: ${bucketsError.message}`));
              return;
            }
            
            console.log('Available buckets:', JSON.stringify(buckets));
            
            const photoBucketExists = buckets.some(bucket => bucket.name === 'photobucket');
            
            if (!photoBucketExists) {
              console.error('The photobucket does not exist!');
              reject(new Error('The required storage bucket does not exist'));
            } else {
              console.log('photobucket exists');
              resolve(true);
            }
          } catch (err) {
            reject(err);
          }
        });
        
        // Set a timeout of 5 seconds to avoid hanging the app startup
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Connection check timed out')), 5000)
        );
        
        // Race the connection check against the timeout
        await Promise.race([connectionPromise, timeoutPromise])
          .catch(error => {
            console.error('Supabase connection issue:', error.message);
            // Only show alert once to avoid spamming user
            if (!alertShown) {
              Alert.alert(
                'Connection Issue', 
                'There may be issues connecting to the cloud service. Some features like photo uploads may not work.',
                [{ text: 'OK' }]
              );
              alertShown = true;
            }
          });
          
      } catch (error) {
        console.error('Error checking Supabase connection:', error);
      }
    };
    
    // Don't block app startup - run the check after a short delay
    setTimeout(() => {
      checkSupabaseConnection();
    }, 2000);
  }, []);

  // Add this useEffect for camera permissions
  useEffect(() => {
    const getCameraPermission = async () => {
      try {
        const { status } = await Camera.requestCameraPermissionsAsync();
        console.log('Camera permission status:', status);
        setCameraPermission(status === 'granted');
        
        if (status !== 'granted') {
          Alert.alert(
            'Camera Permission Required',
            'Please grant camera access to use this feature.',
            [{ text: 'OK' }]
          );
        }
      } catch (error) {
        console.error('Error requesting camera permission:', error);
        Alert.alert('Error', 'Could not request camera permission');
      }
    };

    getCameraPermission();
  }, []);

  // First, update the uploadPhotoToSupabase function to properly format the base64 data
  const uploadPhotoToSupabase = async (photoUri, landmarkName) => {
    try {
      setIsUploading(true);
      
      // Generate a unique filename
      const fileName = `${userId}_${Date.now()}.jpg`;
      const filePath = `${userId}/${fileName}`;
      
      // Compress and resize the image first
      const resizedPhoto = await ImageManipulator.manipulateAsync(
        photoUri,
        [{ resize: { width: 600 } }], // Smaller size
        { format: ImageManipulator.SaveFormat.JPEG, compress: 0.4 } // More compression
      );
      
      console.log('Attempting upload to Supabase...');
      
      // Use fetch to upload the file as binary data
      const fileUri = resizedPhoto.uri;
      const fileBlob = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.onload = function() {
          resolve(xhr.response);
        };
        xhr.onerror = function(e) {
          reject(new TypeError('Network request failed'));
        };
        xhr.responseType = 'blob';
        xhr.open('GET', fileUri, true);
        xhr.send(null);
      });
      
      // Upload the blob to Supabase
      const response = await fetch(`${supabaseUrl}/storage/v1/object/photobucket/${filePath}`, {
        method: 'POST',
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'image/jpeg',
          'x-upsert': 'true'
        },
        body: fileBlob
      });
      
      console.log('Upload response status:', response.status);
      
      // Parse response
      let responseText;
      try {
        responseText = await response.text();
        console.log('Response text:', responseText);
      } catch (e) {
        console.log('Could not get response text:', e);
      }
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      // Get the public URL
      const publicUrl = `${supabaseUrl}/storage/v1/object/public/photobucket/${filePath}`;
      console.log('Public URL:', publicUrl);
      
      setUploadSuccess(true);
      Alert.alert('Success', 'Your photo has been saved!', [{ text: 'OK' }]);
      return true;
    } catch (err) {
      console.error('Error in upload process:', err);
      Alert.alert('Upload Issue', `Error: ${err.message}`, [{ text: 'OK' }]);
      return false;
    } finally {
      setIsUploading(false);
    }
  };

  // Function to check if the Claude response indicates a landmark was detected
  const checkIfLandmark = (text) => {
    // Common phrases used when no landmark is detected
    const negativeIndicators = [
      "not a recognizable landmark",
      "i don't see any famous landmark",
      "doesn't appear to be a landmark",
      "not a famous landmark",
      "cannot identify any landmark",
      "no notable landmark",
      "no famous landmark"
    ];
    
    // If any negative indicator is found, it's not a landmark
    return !negativeIndicators.some(phrase => 
      text.toLowerCase().includes(phrase.toLowerCase())
    );
  };

  // Extract landmark name from the analysis text
  const extractLandmarkName = (text) => {
    // Simple extraction, can be improved
    let name = text.split('.')[0];
    // Remove phrases like "This is" or "I can see"
    name = name.replace(/^(This is|I can see|This appears to be|This looks like)\s+/i, '');
    return name;
  };

  // Function to get detailed facts about a landmark
  const getDetailedFacts = async (landmarkName) => {
    try {
      // Get more detailed information about the landmark from Claude
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: "claude-3-haiku-20240307",
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: `Provide 5 interesting facts about ${landmarkName}. Include historical context, architectural details, and fun trivia. Format each fact as a separate paragraph.`
                }
              ]
            }
          ]
        })
      });
      
      const result = await response.json();
      
      if (result.error) {
        console.log('Claude API facts error:', result.error);
        return null;
      }
      
      if (result.content && result.content[0] && result.content[0].text) {
        return result.content[0].text;
      }
      
      return null;
    } catch (error) {
      console.log('Error getting landmark details:', error);
      return null;
    }
  };

  // Run image analysis in a way that doesn't block the app
  const analyzeImageWithClaude = async (imageUri) => {
    try {
      setIsAnalyzing(true);
      
      // Convert image to base64
      const base64 = await FileSystem.readAsStringAsync(imageUri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      
      // Show analyzing message to the user
      console.log('Analyzing image with Claude...');
      
      // Prepare the API request to Claude
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: "claude-3-haiku-20240307",
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "Analyze this image. Is this a famous landmark or location? If so, identify it and provide the name and location. If not, just say it's not a recognizable landmark."
                },
                {
                  type: "image",
                  source: {
                    type: "base64",
                    media_type: "image/jpeg",
                    data: base64
                  }
                }
              ]
            }
          ]
        })
      });
      
      const result = await response.json();
      
      if (result.error) {
        // Handle API error (like rate limit)
        console.log('Claude API error:', result.error);
        Alert.alert('Analysis Error', `API Error: ${result.error.message || 'Unknown error'}`);
        setIsAnalyzing(false);
        return;
      }
      
      if (result.content && result.content[0] && result.content[0].text) {
        const analysisText = result.content[0].text;
        setAnalyzeResults(analysisText);
        
        // Check if the image contains a landmark
        const containsLandmark = checkIfLandmark(analysisText);
        setIsLandmark(containsLandmark);
        
        if (containsLandmark) {
          // Save to media library since it's a landmark
          try {
            await MediaLibrary.saveToLibraryAsync(imageUri);
            console.log('Landmark photo saved to media library');
            
            // Extract landmark name from the analysis
            const extractedLandmarkName = extractLandmarkName(analysisText);
            setLandmarkName(extractedLandmarkName);
            
            // Show immediate feedback to user
            Alert.alert(
              'Landmark Detected',
              `Identified as ${extractedLandmarkName}.`,
              [
                {
                  text: 'Save to Collection',
                  onPress: () => {
                    // Upload in a separate thread to prevent UI blocking
                    setTimeout(() => {
                      try {
                        // Get facts while showing a loading state
                        setIsUploading(true);
                        
                        // Get facts in parallel with upload
                        getDetailedFacts(extractedLandmarkName)
                          .then(details => {
                            if (details) {
                              setLandmarkDetails(details);
                            }
                          })
                          .catch(error => console.log('Facts error:', error));
                        
                        // Start upload process with better error handling
                        uploadPhotoToSupabase(imageUri, extractedLandmarkName)
                          .then(success => {
                            setIsUploading(false);
                            if (success) {
                              setUploadSuccess(true);
                              if (landmarkDetails) {
                                // Show the details modal after successful upload
                                setTimeout(() => setShowLandmarkModal(true), 500);
                              }
                            }
                          })
                          .catch(error => {
                            console.error('Upload final error:', error);
                            setIsUploading(false);
                            Alert.alert('Upload Failed', 'Please try again later');
                          });
                      } catch (error) {
                        console.error('Error in Save to Collection:', error);
                        setIsUploading(false);
                        Alert.alert('Error', 'An unexpected error occurred');
                      }
                    }, 500);
                  }
                },
                { 
                  text: 'Cancel',
                  style: 'cancel'
                }
              ]
            );
          } catch (err) {
            console.log('Error saving to media library:', err);
            Alert.alert('Save Error', 'Could not save the landmark photo to your library.');
          }
        } else {
          // Not a landmark, inform the user
          Alert.alert(
            'Not a Landmark',
            'This doesn\'t appear to be a famous landmark. Only landmark photos are saved.',
            [{ text: 'OK' }]
          );
        }
      } else {
        console.log('Unexpected API response format:', result);
        Alert.alert('Analysis Error', 'Could not analyze the image properly.');
      }
    } catch (error) {
      console.log('Error analyzing image:', error);
      Alert.alert('Analysis Error', `Could not analyze the image: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Take a picture and handle asynchronous operations
  const takePicture = async () => {
    // Add camera ready check
    if (isTakingPhoto || !cameraRef.current || !isCameraReady) {
      Alert.alert('Camera Not Ready', 'Please wait for the camera to initialize.');
      return;
    }
    
    try {
      setIsTakingPhoto(true);
      
      // Take the picture with lower quality to avoid memory issues
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.5,
        skipProcessing: true,
        exif: false // Disable exif to save memory
      });
      
      console.log('Photo taken, uri length:', photo.uri?.length || 0);
      
      // Store the photo details first
      setCapturedPhoto(photo.uri);
      setPhotoTaken(true);
      
      // First transition from camera view to prevent unmounting issues
      setShowARScreen(false);
      
      // After we've safely exited the camera view, start analysis with a longer timeout
      setTimeout(() => {
        analyzeImageWithClaude(photo.uri)
          .catch(error => {
            console.log('Analysis error:', error);
          })
          .finally(() => {
            setIsTakingPhoto(false);
          });
      }, 1000); // Longer timeout to ensure clean exit from camera
      
    } catch (error) {
      console.log('Error taking picture:', error);
      Alert.alert('Camera Error', `Could not take picture: ${error.message}`);
      setIsTakingPhoto(false);
    }
  };

  const toggleCameraType = () => {
    setCameraType(current => current === 'back' ? 'front' : 'back');
  };

  const toggleFlash = () => {
    setFlashMode(current => current === 'off' ? 'on' : 'off');
  };

  // Landmark details modal
  const renderLandmarkModal = () => {
    return (
      <Modal
        animationType="slide"
        transparent={true}
        visible={showLandmarkModal}
        onRequestClose={() => setShowLandmarkModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{landmarkName || 'Landmark Details'}</Text>
            <ScrollView style={styles.modalScrollView}>
              {landmarkDetails ? (
                <Text style={styles.modalText}>{landmarkDetails}</Text>
              ) : (
                <Text style={styles.modalText}>Loading details or details unavailable...</Text>
              )}
            </ScrollView>
            <TouchableOpacity
              style={styles.modalCloseButton}
              onPress={() => setShowLandmarkModal(false)}
            >
              <Text style={styles.modalCloseButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    );
  };

  try {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />
        {showARScreen ? (
          <View style={styles.arContainer}>
            {cameraPermission ? (
              <CameraView
                ref={cameraRef}
                style={styles.camera}
                facing={cameraType}
                flashMode={flashMode}
                onCameraReady={() => {
                  console.log('Camera ready');
                  setIsCameraReady(true);
                }}
                onError={(error) => {
                  console.log('Camera error:', error);
                  setIsCameraReady(false);
                  Alert.alert('Camera Error', 'There was an issue with the camera: ' + error.message);
                }}
              >
                <View style={styles.topButtons}>
                  <TouchableOpacity 
                    style={styles.button} 
                    onPress={() => setShowARScreen(false)}
                    disabled={isTakingPhoto}
                  >
                    <Text style={styles.buttonText}>Back</Text>
                  </TouchableOpacity>

                  <TouchableOpacity 
                    style={styles.button} 
                    onPress={toggleFlash}
                    disabled={isTakingPhoto}
                  >
                    <Text style={styles.buttonText}>
                      {flashMode === 'off' ? '🔦 On' : '🔦 Off'}
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity 
                    style={styles.button} 
                    onPress={toggleCameraType}
                    disabled={isTakingPhoto}
                  >
                    <Text style={styles.buttonText}>📷 Flip</Text>
                  </TouchableOpacity>
                </View>
                
                {/* Location coordinates in bottom corner */}
                {location && (
                  <Animated.View 
                    style={[
                      styles.locationContainer,
                      { opacity: fadeAnim }
                    ]}
                  >
                    <Text style={styles.locationText}>
                      📍 {location.coords.latitude.toFixed(4)}, {location.coords.longitude.toFixed(4)}
                    </Text>
                  </Animated.View>
                )}
                
                <View style={styles.bottomButtons}>
                  <TouchableOpacity 
                    style={[
                      styles.captureButton, 
                      isTakingPhoto && styles.disabledButton
                    ]} 
                    onPress={takePicture}
                    disabled={isTakingPhoto}
                  >
                    {isTakingPhoto ? (
                      <ActivityIndicator size="large" color="#FFF" />
                    ) : (
                      <View style={styles.captureButtonInner} />
                    )}
                  </TouchableOpacity>
                </View>
              </CameraView>
            ) : (
              <View style={styles.cameraBackground}>
                <Text style={styles.permissionText}>Camera permission is required</Text>
                <TouchableOpacity
                  style={styles.permissionButton}
                  onPress={async () => {
                    const { status } = await Camera.requestCameraPermissionsAsync();
                    setCameraPermission(status === 'granted');
                  }}
                >
                  <Text style={styles.permissionButtonText}>Grant Permission</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        ) : (
          <ScrollView 
            contentContainerStyle={styles.scrollContainer}
            bounces={false}
          >
            <View style={styles.startContainer}>
              {capturedPhoto ? (
                <View style={styles.previewContainer}>
                  <Text style={styles.previewText}>
                    {isLandmark ? 'Landmark Detected!' : 'Landmark NOT Detected'}
                  </Text>
                  <Image 
                    source={{ uri: capturedPhoto }} 
                    style={styles.previewImage}
                    resizeMode="contain"
                  />
                  {isLandmark && analyzeResults && (
                    <View style={styles.analysisContainer}>
                      <Text style={styles.analysisText}>{analyzeResults}</Text>
                      {landmarkDetails && (
                        <TouchableOpacity 
                          style={styles.factsButton}
                          onPress={() => setShowLandmarkModal(true)}
                        >
                          <Text style={styles.factsButtonText}>View Fun Facts</Text>
                        </TouchableOpacity>
                      )}
                    </View>
                  )}
                  {!isLandmark && (
                    <View style={styles.analysisContainer}>
                      <Text style={styles.analysisText}>
                        No landmark was detected in this photo.
                      </Text>
                    </View>
                  )}
                </View>
              ) : null}
              <View style={styles.bottomContainer}>
                <Text style={styles.title}>Trailblaze</Text>
                <Text style={styles.subtitle}>Capture Your Journey</Text>
                <TouchableOpacity
                  style={styles.startButton}
                  onPress={() => setShowARScreen(true)}
                  disabled={isTakingPhoto}
                >
                  <Text style={styles.startButtonText}>Start Experience</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>
        )}
        
        {/* Render landmark details modal */}
        {renderLandmarkModal()}
      </SafeAreaView>
    );
  } catch (error) {
    // This will catch render errors
    console.error('FATAL APP ERROR:', error);
    return (
      <SafeAreaView style={[styles.container, {justifyContent: 'center', alignItems: 'center'}]}>
        <Text style={{color: 'white', fontSize: 18, textAlign: 'center', padding: 20}}>
          Something went wrong with the app. Please restart.
        </Text>
        <Text style={{color: '#FF3366', fontSize: 14, marginTop: 10}}>
          Error: {error.message}
        </Text>
      </SafeAreaView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A1A',
  },
  scrollContainer: {
    flexGrow: 1,
  },
  startContainer: {
    flex: 1,
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#0A0A1A',
    minHeight: '100%',
  },
  arContainer: {
    flex: 1,
    width: '100%',
  },
  camera: {
    flex: 1,
  },
  cameraBackground: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1A1A2E',
  },
  permissionText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    padding: 20,
    fontWeight: 'bold',
  },
  permissionButton: {
    backgroundColor: '#4361EE',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 10,
    marginTop: 15,
  },
  permissionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  previewContainer: {
    width: '100%',
    alignItems: 'center',
    marginVertical: 20,
  },
  previewText: {
    color: '#4361EE',
    fontSize: 18,
    marginBottom: 10,
    fontWeight: '600',
  },
  previewImage: {
    width: '100%',
    height: 300,
    borderRadius: 12,
    backgroundColor: '#1A1A2E',
    marginVertical: 10,
  },
  bottomContainer: {
    width: '100%',
    alignItems: 'center',
    paddingBottom: 20,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FF3366',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 20,
    color: '#B0B0D1',
    marginBottom: 30,
    textAlign: 'center',
  },
  startButton: {
    backgroundColor: '#4361EE',
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 12,
    marginTop: 10,
  },
  startButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  topButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: Platform.OS === 'android' ? 40 : 20,
  },
  button: {
    backgroundColor: 'rgba(10, 10, 26, 0.7)',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  locationContainer: {
    position: 'absolute',
    bottom: 100,
    right: 20,
    backgroundColor: 'rgba(10, 10, 26, 0.7)',
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(67, 97, 238, 0.5)',
  },
  locationText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  bottomButtons: {
    position: 'absolute',
    bottom: 30,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
  },
  captureButton: {
    width: 75,
    height: 75,
    borderRadius: 40,
    backgroundColor: 'rgba(67, 97, 238, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  disabledButton: {
    opacity: 0.5,
    backgroundColor: 'rgba(100, 100, 100, 0.3)',
  },
  captureButtonInner: {
    width: 65,
    height: 65,
    borderRadius: 35,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  analysisContainer: {
    width: '100%',
    padding: 15,
    backgroundColor: 'rgba(67, 97, 238, 0.2)',
    borderRadius: 8,
    marginTop: 10,
    alignItems: 'center',
  },
  analysisText: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'center',
  },
  factsButton: {
    backgroundColor: '#FF3366',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 8,
    marginTop: 10,
  },
  factsButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#0A0A1A',
    borderRadius: 15,
    padding: 20,
    width: '90%',
    maxHeight: '80%',
    borderWidth: 1,
    borderColor: '#4361EE',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FF3366',
    marginBottom: 15,
    textAlign: 'center',
  },
  modalScrollView: {
    width: '100%',
    marginBottom: 15,
  },
  modalText: {
    fontSize: 16,
    color: 'white',
    lineHeight: 22,
    marginBottom: 10,
  },
  modalCloseButton: {
    backgroundColor: '#4361EE',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
    marginTop: 5,
  },
  modalCloseButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
