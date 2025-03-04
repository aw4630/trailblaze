import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView } from 'react-native';
import React from 'react';
import { StatusBar } from 'expo-status-bar';

export default function CameraScreen() {
  const handleTakePicture = () => {
    console.log('Take picture button pressed');
    // In a real app, we would implement camera functionality here
  };

  const handleFlipCamera = () => {
    console.log('Flip camera button pressed');
    // In a real app, we would flip the camera here
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.cameraPlaceholder}>
        <Text style={styles.placeholderText}>Camera Preview</Text>
        <Text style={styles.placeholderSubtext}>
          Camera functionality would be implemented here in a production app
        </Text>
      </View>
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.flipButton} onPress={handleFlipCamera}>
          <Text style={styles.buttonText}>Flip</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.captureButton} onPress={handleTakePicture}>
          <View style={styles.captureButtonInner} />
        </TouchableOpacity>
        <View style={styles.emptySpace} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  cameraPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  placeholderText: {
    color: '#333',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  placeholderSubtext: {
    color: '#666',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
  buttonContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 20,
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  flipButton: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 30,
    width: 60,
    height: 60,
  },
  emptySpace: {
    width: 60,
  },
  captureButton: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#8900e1',
    shadowColor: '#8900e1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  captureButtonInner: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#8900e1',
  },
  buttonText: {
    fontSize: 16,
    color: '#333',
  },
}); 