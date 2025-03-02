import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator, Image } from 'react-native';
import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import Slider from '@react-native-community/slider';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useRouter } from 'expo-router';
import RouteMap from '../../../components/RouteMap';
import { SAMPLE_ROUTE_POINTS, ALTERNATIVE_ROUTE_POINTS, RoutePoint } from '../../../utils/mapUtils';

// Define the theme type with proper SF Symbol names
type ThemeItem = {
  name: string;
  icon: any; // Using any type to avoid type errors with SF Symbols
};

// Define the transportation mode type
type TransportMode = {
  name: string;
  icon: any; // Using any type to avoid type errors with SF Symbols
};

// Update the landmarkTransportation type
type LandmarkTransportation = {
  from: string;
  to: string;
  mode: any; // Using any type to avoid SF Symbols type errors
  label: string;
};

// Define the suggested route type
type SuggestedRoute = {
  id: string;
  name: string;
  description: string;
  distance: string;
  duration: string;
  cost: string;
  transportModes: string[];
  themes: string[];
  landmarks: {
    id: string;
    name: string;
    description: string;
  }[];
  // Add transportation between landmarks
  landmarkTransportation?: LandmarkTransportation[];
  // Add route points for the map
  routePoints: RoutePoint[];
};

export default function AddRouteScreen() {
  const [routeName, setRouteName] = useState('');
  const [isDistanceMode, setIsDistanceMode] = useState(true);
  const [distanceValue, setDistanceValue] = useState(5); // Default 5 miles
  const [timeValue, setTimeValue] = useState(60); // Default 60 minutes
  const [selectedTheme, setSelectedTheme] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [maxBudget, setMaxBudget] = useState(100); // Default maximum budget
  const [selectedTransportModes, setSelectedTransportModes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedRoutes, setSuggestedRoutes] = useState<SuggestedRoute[]>([]);
  const router = useRouter();

  // Predefined transportation modes with their corresponding Apple SF Symbols
  const transportModes: TransportMode[] = [
    { name: 'Walk', icon: 'figure.walk' },
    { name: 'Car', icon: 'car.fill' },
    { name: 'Public Transport', icon: 'bus.fill' },
    { name: 'Cycling', icon: 'bicycle' }
  ];

  // Predefined themes with their corresponding Apple SF Symbols
  const themes: ThemeItem[] = [
    { name: 'Parks', icon: 'leaf.fill' },
    { name: 'Landmarks', icon: 'building.columns.fill' },
    { name: 'Ancient Buildings', icon: 'building.2.fill' },
    { name: 'New Buildings', icon: 'building.fill' },
    { name: 'Movie Scenes', icon: 'film.fill' },
    { name: 'Historical Events', icon: 'clock.fill' }
  ];

  // Sample suggested routes
  const SUGGESTED_ROUTES: SuggestedRoute[] = [
    {
      id: '1',
      name: 'Historic Downtown Tour',
      description: 'Explore the rich history of downtown with this walking tour that takes you through historic landmarks and architectural marvels.',
      distance: '2.5 miles',
      duration: '1.5 hours',
      cost: 'Free',
      transportModes: ['Walking'],
      themes: ['History', 'Architecture'],
      landmarks: [
        { id: '1', name: 'City Hall', description: 'Historic government building from 1890' },
        { id: '2', name: 'Old Theater', description: 'Restored theater from the early 1900s' },
        { id: '3', name: 'Heritage Museum', description: 'Local history exhibits' },
        { id: '4', name: 'Founders Square', description: 'Central plaza with monuments' }
      ],
      landmarkTransportation: [
        { from: '1', to: '2', mode: 'figure.walk' as const, label: 'Walking' },
        { from: '2', to: '3', mode: 'figure.walk' as const, label: 'Walking' },
        { from: '3', to: '4', mode: 'figure.walk' as const, label: 'Walking' }
      ],
      routePoints: SAMPLE_ROUTE_POINTS
    },
    {
      id: '2',
      name: 'Urban Nature Escape',
      description: 'A perfect blend of urban exploration and natural beauty, this route takes you through city parks and green spaces.',
      distance: '4 miles',
      duration: '2 hours',
      cost: 'Free',
      transportModes: ['Walking', 'Cycling'],
      themes: ['Nature', 'Parks'],
      landmarks: [
        { id: '1', name: 'Central Park', description: 'Large urban park with walking trails' },
        { id: '2', name: 'Botanical Gardens', description: 'Diverse plant collections and exhibits' },
        { id: '3', name: 'Riverside Walk', description: 'Scenic path along the river' },
        { id: '4', name: 'Hilltop Viewpoint', description: 'Panoramic views of the city' }
      ],
      landmarkTransportation: [
        { from: '1', to: '2', mode: 'figure.walk' as const, label: 'Walking' },
        { from: '2', to: '3', mode: 'bicycle' as const, label: 'Cycling' },
        { from: '3', to: '4', mode: 'figure.walk' as const, label: 'Walking' }
      ],
      routePoints: ALTERNATIVE_ROUTE_POINTS
    },
    {
      id: '3',
      name: 'Riverside Walk',
      description: 'A relaxing walk along the river with beautiful water views and nature spots.',
      distance: '4.5 miles',
      duration: '1 hour 15 minutes',
      cost: '$5',
      transportModes: ['Walk', 'Cycling'],
      themes: ['Parks', 'Landmarks'],
      landmarks: [
        { id: 'A', name: 'Harbor View', description: 'Panoramic water views' },
        { id: 'B', name: 'Riverside Cafe', description: 'Popular local eatery' },
        { id: 'C', name: 'Nature Reserve', description: 'Protected wildlife area' }
      ],
      landmarkTransportation: [
        { from: 'A', to: 'B', mode: 'figure.walk' as const, label: 'Walking' },
        { from: 'B', to: 'C', mode: 'bicycle' as const, label: 'Cycling' }
      ],
      routePoints: []
    },
    {
      id: '4',
      name: 'Historical District Tour',
      description: 'Visit the most important historical sites and monuments in the city center.',
      distance: '3.7 miles',
      duration: '1 hour 30 minutes',
      cost: '$25',
      transportModes: ['Walk', 'Public Transport'],
      themes: ['Historical Events', 'Landmarks'],
      landmarks: [
        { id: 'A', name: 'Old Town Square', description: 'Historic gathering place' },
        { id: 'B', name: 'War Memorial', description: 'Commemorative monument' },
        { id: 'C', name: 'Ancient Church', description: 'Gothic architecture' }
      ],
      landmarkTransportation: [
        { from: 'A', to: 'B', mode: 'figure.walk' as const, label: 'Walking' },
        { from: 'B', to: 'C', mode: 'tram.fill' as const, label: 'Tram' }
      ],
      routePoints: []
    },
    {
      id: '5',
      name: 'Art Gallery Hop',
      description: 'A cultural route connecting the best art galleries and museums in town.',
      distance: '2.5 miles',
      duration: '2 hours',
      cost: '$30',
      transportModes: ['Walk', 'Car'],
      themes: ['Landmarks', 'New Buildings'],
      landmarks: [
        { id: 'A', name: 'Modern Art Museum', description: 'Contemporary exhibitions' },
        { id: 'B', name: 'Street Art Alley', description: 'Urban murals and graffiti' },
        { id: 'C', name: 'Gallery District', description: 'Collection of art spaces' }
      ],
      landmarkTransportation: [
        { from: 'A', to: 'B', mode: 'figure.walk' as const, label: 'Walking' },
        { from: 'B', to: 'C', mode: 'car.fill' as const, label: 'Car' }
      ],
      routePoints: []
    }
  ];

  const formatDistance = (value: number): string => {
    return `${value.toFixed(1)} miles`;
  };

  const formatTime = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} minutes`;
    } else {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return mins > 0 ? `${hours} hr ${mins} min` : `${hours} hours`;
    }
  };

  const formatBudget = (value: number): string => {
    return `$${value}`;
  };

  const handleMaxBudgetChange = (value: number) => {
    setMaxBudget(value);
  };

  const toggleTransportMode = (modeName: string) => {
    setSelectedTransportModes(prevModes => {
      if (prevModes.includes(modeName)) {
        return prevModes.filter(mode => mode !== modeName);
      } else {
        return [...prevModes, modeName];
      }
    });
  };

  const handleSubmit = () => {
    // Prepare the data based on the mode (distance or time)
    const routeData = {
      routeName,
      measurementType: isDistanceMode ? 'distance' : 'time',
      measurementValue: isDistanceMode ? distanceValue : timeValue,
      transportModes: selectedTransportModes,
      theme: selectedTheme,
      customPrompt: selectedTheme === 'Generate using Claude' ? customPrompt : '',
      budget: {
        max: maxBudget
      }
    };
    
    console.log('Route submitted:', routeData);
    
    // Show loading screen
    setIsLoading(true);
    setSuggestedRoutes([]);
    
    // Simulate API call with a 3-second delay
    setTimeout(() => {
      setIsLoading(false);
      setSuggestedRoutes(SUGGESTED_ROUTES);
    }, 3000);
  };

  const resetForm = () => {
    // Clear form and suggested routes
    setRouteName('');
    setIsDistanceMode(true);
    setDistanceValue(5);
    setTimeValue(60);
    setSelectedTransportModes([]);
    setSelectedTheme('');
    setCustomPrompt('');
    setMaxBudget(100);
    setSuggestedRoutes([]);
  };

  const selectRoute = (route: SuggestedRoute) => {
    console.log('Selected route:', route);
    
    // Prepare the data to pass to the navigation screen
    const landmarksParam = encodeURIComponent(JSON.stringify(route.landmarks));
    const transportationParam = encodeURIComponent(JSON.stringify(route.landmarkTransportation || []));
    
    // Navigate to the navigation screen with the route data
    router.push({
      pathname: '/navigation',
      params: {
        landmarks: landmarksParam,
        transportation: transportationParam,
        routeName: route.name
      }
    });
  };

  // Render loading screen
  if (isLoading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <StatusBar style="dark" />
        <ActivityIndicator size="large" color="#8900e1" />
        <Text style={styles.loadingText}>Generating routes based on your preferences...</Text>
        <Text style={styles.loadingSubText}>This may take a moment</Text>
      </SafeAreaView>
    );
  }

  // Render suggested routes if available
  if (suggestedRoutes.length > 0) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="dark" />
        <View style={styles.suggestedHeader}>
          <Text style={styles.suggestedTitle}>Suggested Routes</Text>
          <TouchableOpacity style={styles.backButton} onPress={resetForm}>
            <Text style={styles.backButtonText}>Back to Form</Text>
          </TouchableOpacity>
        </View>
        <ScrollView contentContainerStyle={styles.suggestedScrollContent}>
          {suggestedRoutes.map((route) => (
            <TouchableOpacity 
              key={route.id} 
              style={styles.routeCard}
              onPress={() => selectRoute(route)}
            >
              {/* Map View */}
              <View style={styles.mapPlaceholder}>
                <RouteMap points={route.routePoints} />
              </View>
              
              <View style={styles.routeInfo}>
                <Text style={styles.routeName}>{route.name}</Text>
                <Text style={styles.routeDescription}>{route.description}</Text>
                
                {/* Route Stats */}
                <View style={styles.routeStats}>
                  <View style={styles.routeStat}>
                    <IconSymbol size={16} name="ruler.fill" color="#666" />
                    <Text style={styles.routeStatText}>{route.distance}</Text>
                  </View>
                  <View style={styles.routeStat}>
                    <IconSymbol size={16} name="clock.fill" color="#666" />
                    <Text style={styles.routeStatText}>{route.duration}</Text>
                  </View>
                  <View style={styles.routeStat}>
                    <IconSymbol size={16} name="dollarsign.circle.fill" color="#666" />
                    <Text style={styles.routeStatText}>{route.cost}</Text>
                  </View>
                </View>
                
                {/* Transportation Modes */}
                <View style={styles.routeDetailSection}>
                  <Text style={styles.routeDetailTitle}>Transportation:</Text>
                  <View style={styles.routeDetailItems}>
                    {route.transportModes.map((mode, index) => (
                      <View key={index} style={styles.routeDetailItem}>
                        <IconSymbol 
                          size={14} 
                          name={transportModes.find(m => m.name === mode)?.icon || 'figure.walk'} 
                          color="#8900e1" 
                        />
                        <Text style={styles.routeDetailItemText}>{mode}</Text>
                      </View>
                    ))}
                  </View>
                </View>
                
                {/* Themes */}
                <View style={styles.routeDetailSection}>
                  <Text style={styles.routeDetailTitle}>Themes:</Text>
                  <View style={styles.routeDetailItems}>
                    {route.themes.map((theme, index) => (
                      <View key={index} style={styles.routeDetailItem}>
                        <IconSymbol 
                          size={14} 
                          name={themes.find(t => t.name === theme)?.icon || 'leaf.fill'} 
                          color="#8900e1" 
                        />
                        <Text style={styles.routeDetailItemText}>{theme}</Text>
                      </View>
                    ))}
                  </View>
                </View>
                
                {/* Landmarks */}
                <View style={styles.landmarksSection}>
                  <Text style={styles.routeDetailTitle}>Landmarks:</Text>
                  <View style={styles.landmarksContainer}>
                    {route.landmarks.map((landmark, index) => (
                      <View key={landmark.id} style={styles.landmarkItem}>
                        <View style={styles.landmarkConnector}>
                          <View style={styles.landmarkDot} />
                          {index < route.landmarks.length - 1 && <View style={styles.landmarkLine} />}
                        </View>
                        <View style={styles.landmarkContent}>
                          <Text style={styles.landmarkId}>{landmark.id}</Text>
                          <View style={styles.landmarkTextContainer}>
                            <Text style={styles.landmarkName}>{landmark.name}</Text>
                            <Text style={styles.landmarkDescription}>{landmark.description}</Text>
                          </View>
                        </View>
                        
                        {/* Transportation mode to the next landmark */}
                        {index < route.landmarks.length - 1 && route.landmarkTransportation && (
                          <View style={styles.transportationContainer}>
                            <View style={styles.transportationIconContainer}>
                              {route.landmarkTransportation.find(t => t.from === landmark.id && t.to === route.landmarks[index + 1].id) && (
                                <IconSymbol 
                                  size={18} 
                                  name={route.landmarkTransportation.find(t => t.from === landmark.id && t.to === route.landmarks[index + 1].id)?.mode || 'figure.walk'} 
                                  color="#8900e1" 
                                />
                              )}
                            </View>
                            <Text style={styles.transportationText}>
                              {route.landmarkTransportation.find(t => t.from === landmark.id && t.to === route.landmarks[index + 1].id)?.label || 'Walking'}
                            </Text>
                          </View>
                        )}
                      </View>
                    ))}
                  </View>
                </View>
              </View>
              
              {/* Action Button */}
              <View style={styles.routeActionButtons}>
                <TouchableOpacity 
                  style={styles.startNavigationButton}
                  onPress={() => selectRoute(route)}
                >
                  <Text style={styles.startNavigationButtonText}>Start Navigation</Text>
                </TouchableOpacity>
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Render the form
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.formContainer}>
          {/* Route Name Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Route Name</Text>
            <TextInput
              style={styles.input}
              value={routeName}
              onChangeText={setRouteName}
              placeholder="Enter route name"
            />
          </View>
          
          {/* Distance/Time Toggle */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Measurement Type</Text>
            <View style={styles.measurementToggle}>
              <TouchableOpacity
                style={[
                  styles.toggleButton,
                  isDistanceMode && styles.activeToggleButton
                ]}
                onPress={() => setIsDistanceMode(true)}
              >
                <IconSymbol size={20} name="ruler.fill" color={isDistanceMode ? 'white' : '#666'} />
                <Text style={[styles.toggleText, isDistanceMode && styles.activeToggleText]}>Distance</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.toggleButton,
                  !isDistanceMode && styles.activeToggleButton
                ]}
                onPress={() => setIsDistanceMode(false)}
              >
                <IconSymbol size={20} name="clock.fill" color={!isDistanceMode ? 'white' : '#666'} />
                <Text style={[styles.toggleText, !isDistanceMode && styles.activeToggleText]}>Time</Text>
              </TouchableOpacity>
            </View>
            
            {/* Distance Slider */}
            {isDistanceMode ? (
              <View style={styles.sliderContainer}>
                <Text style={styles.sliderValue}>{formatDistance(distanceValue)}</Text>
                <Slider
                  style={styles.slider}
                  minimumValue={1}
                  maximumValue={30}
                  step={0.1}
                  value={distanceValue}
                  onValueChange={setDistanceValue}
                  minimumTrackTintColor="#8900e1"
                  maximumTrackTintColor="#ddd"
                  thumbTintColor="#8900e1"
                />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>1 mile</Text>
                  <Text style={styles.sliderLabel}>30 miles</Text>
                </View>
              </View>
            ) : (
              /* Time Slider */
              <View style={styles.sliderContainer}>
                <Text style={styles.sliderValue}>{formatTime(timeValue)}</Text>
                <Slider
                  style={styles.slider}
                  minimumValue={30}
                  maximumValue={1440} // 24 hours in minutes
                  step={5}
                  value={timeValue}
                  onValueChange={setTimeValue}
                  minimumTrackTintColor="#8900e1"
                  maximumTrackTintColor="#ddd"
                  thumbTintColor="#8900e1"
                />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>30 min</Text>
                  <Text style={styles.sliderLabel}>24 hrs</Text>
                </View>
              </View>
            )}
          </View>
          
          {/* Budget Range Slider */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Maximum Budget</Text>
            <View style={styles.budgetContainer}>
              <View style={styles.budgetValues}>
                <Text style={styles.budgetValue}>Max: {formatBudget(maxBudget)}</Text>
              </View>
              
              {/* Maximum Budget Slider */}
              <View style={styles.sliderContainer}>
                <Slider
                  style={styles.slider}
                  minimumValue={0}
                  maximumValue={1000}
                  step={10}
                  value={maxBudget}
                  onValueChange={handleMaxBudgetChange}
                  minimumTrackTintColor="#8900e1"
                  maximumTrackTintColor="#ddd"
                  thumbTintColor="#8900e1"
                />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>$0</Text>
                  <Text style={styles.sliderLabel}>$1000</Text>
                </View>
              </View>
            </View>
          </View>
          
          {/* Transportation Modes Selection */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Preferred Modes of Transportation</Text>
            <View style={styles.transportContainer}>
              {transportModes.map((mode) => (
                <TouchableOpacity
                  key={mode.name}
                  style={[
                    styles.transportButton,
                    selectedTransportModes.includes(mode.name) && styles.selectedTransport
                  ]}
                  onPress={() => toggleTransportMode(mode.name)}
                >
                  <IconSymbol 
                    size={24} 
                    name={mode.icon} 
                    color={selectedTransportModes.includes(mode.name) ? '#8900e1' : '#666'} 
                  />
                  <Text 
                    style={[
                      styles.transportText,
                      selectedTransportModes.includes(mode.name) && styles.selectedTransportText
                    ]}
                  >
                    {mode.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          
          {/* Theme Selection */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Theme</Text>
            <View style={styles.themeContainer}>
              {themes.map((theme) => (
                <TouchableOpacity
                  key={theme.name}
                  style={[
                    styles.themeButton,
                    selectedTheme === theme.name && styles.selectedTheme
                  ]}
                  onPress={() => setSelectedTheme(theme.name)}
                >
                  <IconSymbol size={24} name={theme.icon} color={selectedTheme === theme.name ? '#8900e1' : '#666'} />
                  <Text 
                    style={[
                      styles.themeText,
                      selectedTheme === theme.name && styles.selectedThemeText
                    ]}
                  >
                    {theme.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            
            {/* Generate using Claude button (full width) */}
            <TouchableOpacity
              style={[
                styles.claudeButton,
                selectedTheme === 'Generate using Claude' && styles.selectedClaudeButton
              ]}
              onPress={() => setSelectedTheme('Generate using Claude')}
            >
              <IconSymbol size={24} name="wand.and.stars" color={selectedTheme === 'Generate using Claude' ? '#8900e1' : '#333'} />
              <Text 
                style={[
                  styles.claudeButtonText,
                  selectedTheme === 'Generate using Claude' && styles.selectedClaudeButtonText
                ]}
              >
                Generate using Claude
              </Text>
            </TouchableOpacity>
            
            {/* Custom Prompt Input */}
            {selectedTheme === 'Generate using Claude' && (
              <TextInput
                style={[styles.input, styles.textArea]}
                value={customPrompt}
                onChangeText={setCustomPrompt}
                placeholder="Describe what kind of route you want Claude to generate..."
                multiline
                numberOfLines={4}
              />
            )}
          </View>
          
          {/* Submit Button */}
          <TouchableOpacity 
            style={[
              styles.submitButton, 
              (!routeName || !selectedTheme || (selectedTheme === 'Generate using Claude' && !customPrompt)) && styles.disabledButton
            ]} 
            onPress={handleSubmit}
            disabled={!routeName || !selectedTheme || (selectedTheme === 'Generate using Claude' && !customPrompt)}
          >
            <Text style={styles.submitButtonText}>Generate Routes</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    flexGrow: 1,
    paddingVertical: 16,
  },
  formContainer: {
    padding: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
    marginTop: 12,
  },
  measurementToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  toggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 12,
    width: '48%',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  activeToggleButton: {
    backgroundColor: '#8900e1',
    borderColor: '#8900e1',
  },
  toggleText: {
    fontSize: 16,
    marginLeft: 8,
    color: '#666',
  },
  activeToggleText: {
    fontWeight: 'bold',
    color: 'white',
  },
  sliderContainer: {
    marginTop: 10,
  },
  slider: {
    width: '100%',
    height: 40,
  },
  sliderValue: {
    textAlign: 'center',
    fontSize: 18,
    fontWeight: 'bold',
    color: '#8900e1',
    marginBottom: 5,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 10,
  },
  sliderLabel: {
    fontSize: 12,
    color: '#666',
  },
  budgetContainer: {
    marginTop: 10,
  },
  budgetValues: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  budgetValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#8900e1',
  },
  transportContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  transportButton: {
    width: '48%',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ddd',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  transportText: {
    fontWeight: '500',
    marginLeft: 8,
    color: '#666',
  },
  selectedTransport: {
    backgroundColor: '#e6e0f0',
    borderColor: '#8900e1',
  },
  selectedTransportText: {
    color: '#8900e1',
    fontWeight: 'bold',
  },
  themeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  themeButton: {
    width: '48%',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ddd',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  themeText: {
    fontWeight: '500',
    marginLeft: 8,
  },
  selectedTheme: {
    backgroundColor: '#e6e0f0',
    borderColor: '#8900e1',
  },
  selectedThemeText: {
    color: '#8900e1',
    fontWeight: 'bold',
  },
  claudeButton: {
    width: '100%',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 10,
    backgroundColor: '#FFD700', // Gold color
    borderWidth: 1,
    borderColor: '#E6C200',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  selectedClaudeButton: {
    backgroundColor: '#FFECB3', // Lighter gold when selected
    borderColor: '#8900e1',
  },
  claudeButtonText: {
    fontWeight: '600',
    marginLeft: 8,
    color: '#333',
  },
  selectedClaudeButtonText: {
    color: '#8900e1',
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#8900e1',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledButton: {
    backgroundColor: '#cccccc',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  // Loading screen styles
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 20,
    textAlign: 'center',
  },
  loadingSubText: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  // Suggested routes styles
  suggestedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  suggestedTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    color: '#8900e1',
    fontWeight: '600',
  },
  suggestedScrollContent: {
    padding: 16,
  },
  routeCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  mapPlaceholder: {
    height: 150,
    width: '100%',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 10,
  },
  mapPlaceholderText: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
  },
  routeInfo: {
    padding: 16,
  },
  routeName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  routeDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  routeStats: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  routeStat: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  routeStatText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 4,
  },
  routeDetailSection: {
    marginBottom: 10,
  },
  routeDetailTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 6,
  },
  routeDetailItems: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  routeDetailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 6,
  },
  routeDetailItemText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  landmarksSection: {
    marginTop: 8,
  },
  landmarksContainer: {
    marginTop: 6,
  },
  landmarkItem: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-start',
  },
  landmarkConnector: {
    width: 20,
    alignItems: 'center',
    marginRight: 4,
    position: 'relative',
  },
  landmarkDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#8900e1',
    zIndex: 1,
  },
  landmarkLine: {
    width: 2,
    backgroundColor: '#8900e1',
    position: 'absolute',
    top: 12,
    bottom: -8,
    left: 9,
  },
  landmarkContent: {
    flexDirection: 'row',
    flex: 1,
  },
  landmarkId: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#f0f0f0',
    textAlign: 'center',
    lineHeight: 20,
    fontWeight: '600',
    color: '#8900e1',
    marginRight: 8,
    fontSize: 12,
  },
  landmarkTextContainer: {
    flex: 1,
  },
  landmarkName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  landmarkDescription: {
    fontSize: 12,
    color: '#666',
  },
  transportationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 'auto',
    paddingLeft: 12,
    paddingRight: 8,
  },
  transportationIconContainer: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  transportationText: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  },
  routeActionButtons: {
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  startNavigationButton: {
    backgroundColor: '#8900e1',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  startNavigationButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
}); 