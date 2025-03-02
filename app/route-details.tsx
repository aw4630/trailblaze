import { StyleSheet, Text, View, SafeAreaView, ScrollView, Image, TouchableOpacity, Dimensions, TextInput } from 'react-native';
import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { IconSymbol } from '@/components/ui/IconSymbol';
import RouteMap from '../components/RouteMap';
import { SAMPLE_ROUTE_POINTS, ALTERNATIVE_ROUTE_POINTS } from '../utils/mapUtils';

// Define a type for comments to ensure all have a rating
type Comment = {
  id: string;
  username: string;
  date: string;
  text: string;
  rating: number;
};

// Sample landmark data
const LANDMARKS = [
  { id: 'A', name: 'Starting Point', description: 'Begin your journey here' },
  { id: 'B', name: 'Scenic Viewpoint', description: 'Amazing panoramic views' },
  { id: 'C', name: 'Historic Monument', description: 'Learn about local history' },
  { id: 'D', name: 'Rest Area', description: 'Take a break and refuel' },
  { id: 'E', name: 'Destination', description: 'You made it!' },
];

// Transportation modes between landmarks
const TRANSPORTATION_MODES = [
  { from: 'A', to: 'B', mode: 'figure.walk' as const, label: 'Walking' },
  { from: 'B', to: 'C', mode: 'bicycle' as const, label: 'Cycling' },
  { from: 'C', to: 'D', mode: 'car.fill' as const, label: 'Driving' },
  { from: 'D', to: 'E', mode: 'figure.hiking' as const, label: 'Hiking' },
];

// Sample route data with additional fields for the details page
const ROUTES_DETAILS = {
  '1': {
    id: '1',
    name: 'Mountain Trail',
    overview: 'A breathtaking mountain trail with panoramic views of the Rocky Mountains. Perfect for experienced hikers looking for a challenge with rewarding scenery at every turn.',
    hours: 2.5,
    landmarks: 8,
    distance: 5.2,
    cost: 15,
    username: 'hikingfan23',
    userRoutes: 12,
    routeUsers: 342,
    city: 'Denver, CO',
    photos: [
      'https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000',
      'https://images.unsplash.com/photo-1527489377706-5bf97e608852?q=80&w=1000',
      'https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?q=80&w=1000',
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1000',
      'https://images.unsplash.com/photo-1606920301021-34e5a5c5a1c2?q=80&w=1000',
    ],
    likes: 128,
    completions: 87,
    rating: 4.7,
    description: 'This trail offers a moderate to difficult hike through the beautiful Rocky Mountains. You\'ll encounter diverse flora and fauna, several water crossings, and stunning viewpoints. The trail is well-maintained but can be challenging in some sections. Bring plenty of water and start early to avoid afternoon thunderstorms common in the area.',
    comments: [
      { id: '1', username: 'trailblazer42', date: '2023-10-15', text: 'Completed this trail last weekend. The views at the summit were absolutely worth the climb! Definitely bring extra water as suggested.', rating: 4.5 },
      { id: '2', username: 'mountaingoat', date: '2023-09-28', text: 'This was more challenging than I expected but totally worth it. The wildflowers were in full bloom and the wildlife sightings were amazing.', rating: 5 },
      { id: '3', username: 'natureseeker', date: '2023-09-10', text: 'Great trail but very crowded on weekends. I recommend going early morning on a weekday if possible.', rating: 4 },
    ]
  },
  '2': {
    id: '2',
    name: 'Coastal Path',
    overview: 'A relaxing coastal walk with stunning ocean views and beach access points. Ideal for families and casual walkers seeking a peaceful seaside experience.',
    hours: 1.5,
    landmarks: 5,
    distance: 3.8,
    cost: 10,
    username: 'beachlover',
    userRoutes: 8,
    routeUsers: 215,
    city: 'San Diego, CA',
    photos: [
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000',
      'https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1000',
      'https://images.unsplash.com/photo-1484821582734-6692f7262f72?q=80&w=1000',
      'https://images.unsplash.com/photo-1566024287286-457247b70310?q=80&w=1000',
      'https://images.unsplash.com/photo-1501950183564-3c8b840a33aa?q=80&w=1000',
    ],
    likes: 95,
    completions: 64,
    rating: 4.5,
    description: 'This scenic coastal path takes you along some of San Diego\'s most beautiful beaches. The trail is mostly flat and suitable for all fitness levels. Along the way, you\'ll find several spots to stop and enjoy the ocean, tide pools, and local wildlife. There are also cafes and restrooms at regular intervals.',
    comments: [
      { id: '1', username: 'citywanderer', date: '2023-10-12', text: 'Such a fun way to explore the city! I discovered shops and cafes I never knew existed despite living here for years.', rating: 5 },
      { id: '2', username: 'historybuff', date: '2023-10-05', text: 'The historical information provided was fascinating. I learned so much about the city\'s architecture and past.', rating: 4.5 },
      { id: '3', username: 'photosnapper', date: '2023-09-22', text: 'Perfect route for photography enthusiasts. So many great photo opportunities!', rating: 4 },
    ]
  },
  '3': {
    id: '3',
    name: 'Forest Loop',
    overview: 'An immersive forest experience with ancient trees and abundant wildlife. The trail offers a peaceful retreat into nature with educational opportunities about local ecosystems.',
    hours: 3.2,
    landmarks: 12,
    distance: 7.5,
    cost: 25,
    username: 'natureexplorer',
    userRoutes: 23,
    routeUsers: 189,
    city: 'Portland, OR',
    photos: [
      'https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000',
      'https://images.unsplash.com/photo-1511497584788-876760111969?q=80&w=1000',
      'https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=1000',
      'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?q=80&w=1000',
      'https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?q=80&w=1000',
    ],
    likes: 210,
    completions: 132,
    rating: 4.9,
    description: 'This loop trail takes you through old-growth forest with towering trees and lush undergrowth. The path is well-marked but can be muddy after rain. You\'ll cross several small streams and may spot local wildlife including deer, various bird species, and possibly elk. There are several interpretive signs along the route explaining the forest ecosystem.',
    comments: [
      { id: '1', username: 'beachlover', date: '2023-10-14', text: 'The coastal views are breathtaking! Make sure to bring a windbreaker as it can get quite breezy.', rating: 4.5 },
      { id: '2', username: 'sunseeker', date: '2023-10-01', text: 'I timed this walk to finish at sunset and it was magical. Highly recommend for a romantic evening.', rating: 5 },
      { id: '3', username: 'marinebiologist', date: '2023-09-18', text: 'Great opportunity for tidepooling if you time it right with low tide. Saw lots of interesting marine life!', rating: 4 },
    ]
  },
  '4': {
    id: '4',
    name: 'City Tour',
    overview: 'A cultural journey through the heart of New York City, showcasing iconic landmarks, hidden gems, and vibrant neighborhoods. Perfect for architecture enthusiasts and urban explorers.',
    hours: 1.0,
    landmarks: 15,
    distance: 2.1,
    cost: 20,
    username: 'urbanadventurer',
    userRoutes: 17,
    routeUsers: 421,
    city: 'New York, NY',
    photos: [
      'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?q=80&w=1000',
      'https://images.unsplash.com/photo-1522083165195-3424ed129620?q=80&w=1000',
      'https://images.unsplash.com/photo-1518391846015-55a9cc003b25?q=80&w=1000',
      'https://images.unsplash.com/photo-1534430480872-3498386e7856?q=80&w=1000',
      'https://images.unsplash.com/photo-1546436836-07a872a10c18?q=80&w=1000',
    ],
    likes: 87,
    completions: 56,
    rating: 4.3,
    description: 'This walking tour takes you through some of New York City\'s most famous landmarks and neighborhoods. You\'ll experience the hustle and bustle of Times Square, the tranquility of Central Park, and the historic architecture of various districts. The route includes opportunities to stop at cafes, museums, and shops along the way.',
    comments: [
      { id: '1', username: 'citywanderer', date: '2023-11-15', text: 'Great way to see the highlights of NYC! The route was well-planned with plenty of interesting stops and photo opportunities.' },
      { id: '2', username: 'architecturefan', date: '2023-10-22', text: 'Loved the mix of famous landmarks and hidden gems. The historical information provided context that I wouldn\'t have known otherwise.' },
      { id: '3', username: 'nycvisitor', date: '2023-09-05', text: 'Perfect introduction to the city for first-time visitors. Comfortable pace and the suggested cafe stops were excellent.' }
    ]
  },
};

// Full-screen photo carousel component
const FullCarousel = ({ photos }: { photos: string[] }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const screenWidth = Dimensions.get('window').width;
  
  return (
    <View style={styles.fullCarouselContainer}>
      <ScrollView
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(event) => {
          const newIndex = Math.round(event.nativeEvent.contentOffset.x / screenWidth);
          setActiveIndex(newIndex);
        }}
      >
        {photos.map((photo, index) => (
          <Image
            key={index}
            source={{ uri: photo }}
            style={[styles.fullCarouselImage, { width: screenWidth }]}
            resizeMode="cover"
          />
        ))}
      </ScrollView>
      
      {/* Pagination dots */}
      <View style={styles.paginationContainer}>
        {photos.map((_, index) => (
          <View
            key={index}
            style={[
              styles.paginationDot,
              index === activeIndex && styles.paginationDotActive
            ]}
          />
        ))}
      </View>
    </View>
  );
};

// Star rating component
const StarRating = ({ rating }: { rating: number }) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
  
  return (
    <View style={styles.starContainer}>
      {[...Array(fullStars)].map((_, i) => (
        <IconSymbol key={`full-${i}`} size={18} name="star.fill" color="#FFD700" />
      ))}
      {halfStar && <IconSymbol key="half" size={18} name="star.leadinghalf.filled" color="#FFD700" />}
      {[...Array(emptyStars)].map((_, i) => (
        <IconSymbol key={`empty-${i}`} size={18} name="star" color="#FFD700" />
      ))}
      <Text style={styles.ratingText}>{rating.toFixed(1)}</Text>
    </View>
  );
};

// Landmark path component
const LandmarkPath = () => {
  return (
    <View style={styles.landmarkPathContainer}>
      {LANDMARKS.map((landmark, index) => (
        <View key={landmark.id}>
          <View style={styles.landmarkItem}>
            <View style={styles.landmarkConnector}>
              <View style={styles.landmarkDot} />
              {index < LANDMARKS.length - 1 && <View style={styles.landmarkLine} />}
            </View>
            <View style={styles.landmarkContent}>
              <Text style={styles.landmarkId}>{landmark.id}</Text>
              <View style={styles.landmarkTextContainer}>
                <Text style={styles.landmarkName}>{landmark.name}</Text>
                <Text style={styles.landmarkDescription}>{landmark.description}</Text>
              </View>
            </View>
            
            {/* Transportation mode to the right of landmark */}
            {index < LANDMARKS.length - 1 && (
              <View style={styles.transportationContainer}>
                <View style={styles.transportationIconContainer}>
                  {TRANSPORTATION_MODES.find(t => t.from === landmark.id && t.to === LANDMARKS[index + 1].id) && (
                    <IconSymbol 
                      size={18} 
                      name={TRANSPORTATION_MODES.find(t => t.from === landmark.id && t.to === LANDMARKS[index + 1].id)?.mode || 'figure.walk'} 
                      color="#8900e1" 
                    />
                  )}
                </View>
                <Text style={styles.transportationText}>
                  {TRANSPORTATION_MODES.find(t => t.from === landmark.id && t.to === LANDMARKS[index + 1].id)?.label || 'Walking'}
                </Text>
              </View>
            )}
          </View>
        </View>
      ))}
    </View>
  );
};

// Comment component
const CommentItem = ({ username, date, text, rating }: Comment) => {
  return (
    <View style={styles.commentItem}>
      <View style={styles.commentHeader}>
        <View style={styles.commentUser}>
          <IconSymbol size={20} name="person.circle.fill" color="#666" />
          <Text style={styles.commentUsername}>{username}</Text>
        </View>
        <Text style={styles.commentDate}>{date}</Text>
      </View>
      <View style={styles.commentRatingContainer}>
        <StarRating rating={rating} />
      </View>
      <Text style={styles.commentText}>{text}</Text>
    </View>
  );
};

export default function RouteDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [commentText, setCommentText] = useState('');
  const [commentRating, setCommentRating] = useState(5);
  const [hasCompletedRoute, setHasCompletedRoute] = useState(false); // Track if user has completed the route
  
  // Get route details based on ID
  const route = ROUTES_DETAILS[id as keyof typeof ROUTES_DETAILS];
  
  // Use different sample data based on the route ID
  const routePoints = id === '2' ? ALTERNATIVE_ROUTE_POINTS : SAMPLE_ROUTE_POINTS;
  
  // Mock route data
  const routeData = {
    id: id || '1',
    title: id === '2' ? 'New York City Tour' : 'Bay Area Tour',
    description: id === '2' 
      ? 'Explore the vibrant neighborhoods of NYC' 
      : 'A scenic tour around the San Francisco Bay Area',
    distance: id === '2' ? '12.5 miles' : '25.3 miles',
    duration: id === '2' ? '2 hours' : '3.5 hours',
    difficulty: id === '2' ? 'Easy' : 'Moderate',
    createdBy: 'John Doe',
    createdAt: 'March 2, 2025',
  };

  // Function to handle comment submission
  const handleSubmit = () => {
    if (commentText.trim() === '') return;
    
    // In a real app, this would send the comment to a server
    console.log('Submitting comment:', {
      text: commentText,
      rating: commentRating,
      routeId: id
    });
    
    // Clear the input after submission
    setCommentText('');
    setCommentRating(5);
  };

  // Function to toggle route completion (for demo purposes)
  const toggleRouteCompletion = () => {
    setHasCompletedRoute(!hasCompletedRoute);
  };
  
  if (!route) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="dark" />
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Route not found</Text>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }
  
  return (
    <>
      <Stack.Screen 
        options={{
          title: routeData.title,
          headerBackTitle: 'Back',
        }} 
      />
      <SafeAreaView style={styles.container}>
        <StatusBar style="dark" />
        
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Full-screen photo carousel */}
          <FullCarousel photos={route.photos} />
          
          {/* Route name */}
          <View style={styles.headerContainer}>
            <View style={styles.routeNameContainer}>
              <Text style={styles.routeName}>{route.name}</Text>
              <TouchableOpacity style={styles.shareButton}>
                <IconSymbol size={20} name="square.and.arrow.up" color="#666" />
              </TouchableOpacity>
            </View>
            
            {/* AI-generated overview */}
            <Text style={styles.overviewText}>{route.overview}</Text>
          </View>
          
          {/* User info and stats */}
          <View style={styles.userInfoContainer}>
            <View style={styles.userInfo}>
              <IconSymbol size={24} name="person.circle.fill" color="#666" />
              <Text style={styles.username}>{route.username}</Text>
            </View>
            <View style={styles.userStats}>
              <Text style={styles.userStatsText}>{route.userRoutes} routes created</Text>
              <Text style={styles.userStatsText}>•</Text>
              <Text style={styles.userStatsText}>{route.routeUsers} users</Text>
            </View>
          </View>
          
          {/* Stats row */}
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <IconSymbol size={20} name="flame.fill" color="#FF6B00" />
              <Text style={styles.statText}>{route.likes} likes</Text>
            </View>
            
            <View style={styles.statItem}>
              <IconSymbol size={20} name="figure.walk" color="#8900e1" />
              <Text style={styles.statText}>{route.completions} completed</Text>
            </View>
            
            <View style={styles.statItem}>
              <StarRating rating={route.rating} />
            </View>
          </View>
          
          {/* Route stats */}
          <View style={styles.routeStatsContainer}>
            <View style={styles.routeStatItem}>
              <IconSymbol size={22} name="clock.fill" color="#8900e1" />
              <Text style={styles.routeStatValue}>{route.hours} hrs</Text>
              <Text style={styles.routeStatLabel}>Duration</Text>
            </View>
            
            <View style={styles.routeStatDivider} />
            
            <View style={styles.routeStatItem}>
              <IconSymbol size={22} name="mappin.and.ellipse" color="#8900e1" />
              <Text style={styles.routeStatValue}>{route.landmarks}</Text>
              <Text style={styles.routeStatLabel}>Landmarks</Text>
            </View>
            
            <View style={styles.routeStatDivider} />
            
            <View style={styles.routeStatItem}>
              <IconSymbol size={22} name="ruler.fill" color="#8900e1" />
              <Text style={styles.routeStatValue}>{route.distance} mi</Text>
              <Text style={styles.routeStatLabel}>Distance</Text>
            </View>
            
            <View style={styles.routeStatDivider} />
            
            <View style={styles.routeStatItem}>
              <IconSymbol size={22} name="dollarsign.circle.fill" color="#8900e1" />
              <Text style={styles.routeStatValue}>${route.cost}</Text>
              <Text style={styles.routeStatLabel}>Cost</Text>
            </View>
          </View>
          
          {/* Landmarks section */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Landmarks</Text>
            <LandmarkPath />
          </View>
          
          {/* Map section */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Route Map</Text>
            <RouteMap points={routePoints} />
          </View>
          
          {/* Description section */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Description</Text>
            <Text style={styles.descriptionText}>{route.description}</Text>
          </View>
          
          {/* Comments section */}
          <View style={styles.sectionContainer}>
            <View style={styles.sectionTitleContainer}>
              <Text style={styles.sectionTitle}>Comments</Text>
              <Text style={styles.commentInfo}>
                {hasCompletedRoute 
                  ? "You've completed this route! Share your experience below." 
                  : "Only users who completed this route can comment"}
              </Text>
            </View>
            
            {/* Comments list */}
            <View style={styles.commentsContainer}>
              {route.comments && route.comments.map((comment) => (
                <CommentItem 
                  key={comment.id}
                  {...comment}
                />
              ))}
            </View>
            
            {/* Comment input */}
            <View style={styles.commentInputContainer}>
              <View style={styles.ratingInputContainer}>
                <Text style={styles.ratingLabel}>Your Rating:</Text>
                <View style={styles.ratingStars}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <TouchableOpacity 
                      key={`star-${star}`} 
                      onPress={() => setCommentRating(star)}
                      disabled={!hasCompletedRoute} // Enable if user has completed route
                    >
                      <IconSymbol 
                        size={24} 
                        name={commentRating >= star ? "star.fill" : "star"} 
                        color="#FFD700" 
                        style={{ opacity: hasCompletedRoute ? 1 : 0.5 }} // Full opacity if enabled
                      />
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
              
              <View style={styles.textInputContainer}>
                <TextInput
                  style={[styles.commentInput, { opacity: hasCompletedRoute ? 1 : 0.7 }]}
                  placeholder={hasCompletedRoute 
                    ? "Share your experience..." 
                    : "Add your comment (only available after completing route)"}
                  multiline
                  value={commentText}
                  onChangeText={setCommentText}
                  editable={hasCompletedRoute} // Enable if user has completed route
                />
                <TouchableOpacity 
                  style={[styles.commentButton, { opacity: hasCompletedRoute && commentText.trim() !== '' ? 1 : 0.5 }]}
                  disabled={!hasCompletedRoute || commentText.trim() === ''}
                  onPress={handleSubmit}
                >
                  <IconSymbol size={20} name="paperplane.fill" color="white" />
                </TouchableOpacity>
              </View>
            </View>
          </View>
          
          {/* Start/Complete route button */}
          <TouchableOpacity 
            style={[styles.startButton, hasCompletedRoute ? styles.completedButton : {}]} 
            onPress={toggleRouteCompletion}
          >
            <IconSymbol size={24} name={hasCompletedRoute ? "checkmark.circle.fill" : "play.fill"} color="white" />
            <Text style={styles.startButtonText}>
              {hasCompletedRoute ? "Route Completed" : "Start Route"}
            </Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    paddingBottom: 30,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  backButton: {
    backgroundColor: '#8900e1',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  backButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  fullCarouselContainer: {
    height: 300,
    position: 'relative',
  },
  fullCarouselImage: {
    height: 300,
  },
  paginationContainer: {
    position: 'absolute',
    bottom: 15,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  paginationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.5)',
    marginHorizontal: 4,
  },
  paginationDotActive: {
    backgroundColor: 'white',
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  headerContainer: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  routeNameContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  routeName: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    flex: 1,
  },
  shareButton: {
    padding: 8,
  },
  overviewText: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
  },
  userInfoContainer: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  username: {
    fontWeight: '600',
    fontSize: 16,
    marginLeft: 8,
    color: '#333',
  },
  userStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userStatsText: {
    color: '#666',
    fontSize: 14,
    marginRight: 6,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    marginLeft: 6,
    color: '#666',
    fontWeight: '500',
  },
  starContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  routeStatsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  routeStatItem: {
    alignItems: 'center',
    flex: 1,
  },
  routeStatDivider: {
    width: 1,
    backgroundColor: '#e0e0e0',
    height: '80%',
    alignSelf: 'center',
  },
  routeStatValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginTop: 4,
    marginBottom: 2,
  },
  routeStatLabel: {
    fontSize: 12,
    color: '#666',
  },
  sectionContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  landmarkPathContainer: {
    paddingLeft: 8,
    paddingBottom: 10,
  },
  landmarkItem: {
    flexDirection: 'row',
    marginBottom: 30,
    alignItems: 'center',
  },
  landmarkConnector: {
    width: 24,
    alignItems: 'center',
    height: 50,
  },
  landmarkDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#8900e1',
    zIndex: 1,
  },
  landmarkLine: {
    width: 2,
    flex: 1,
    backgroundColor: '#8900e1',
    marginTop: 4,
    position: 'absolute',
    top: 16,
    bottom: -40,
    left: 11,
    height: 60,
  },
  landmarkContent: {
    flexDirection: 'row',
    flex: 1,
    marginLeft: 12,
  },
  landmarkId: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f0f0f0',
    textAlign: 'center',
    lineHeight: 24,
    fontWeight: '600',
    color: '#8900e1',
    marginRight: 12,
  },
  landmarkTextContainer: {
    flex: 1,
  },
  landmarkName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  landmarkDescription: {
    fontSize: 14,
    color: '#666',
  },
  mapPlaceholder: {
    height: 200,
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapPlaceholderText: {
    marginTop: 8,
    fontSize: 16,
    color: '#666',
  },
  descriptionText: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  startButton: {
    backgroundColor: '#8900e1',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    margin: 16,
    shadowColor: '#8900e1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  startButtonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 18,
    marginLeft: 8,
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  commentInfo: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
  commentsContainer: {
    marginBottom: 16,
  },
  commentItem: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  commentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  commentUser: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  commentUsername: {
    fontWeight: '600',
    fontSize: 14,
    marginLeft: 6,
    color: '#333',
  },
  commentDate: {
    fontSize: 12,
    color: '#888',
  },
  commentText: {
    fontSize: 14,
    color: '#444',
    lineHeight: 20,
  },
  commentInputContainer: {
    flexDirection: 'column',
    marginTop: 8,
  },
  textInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  commentInput: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 14,
    color: '#666',
    marginRight: 8,
    minHeight: 40,
  },
  commentRatingContainer: {
    marginVertical: 4,
  },
  ratingInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    width: '100%',
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 12,
  },
  ratingLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
    fontWeight: '500',
  },
  ratingStars: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  commentButton: {
    backgroundColor: '#8900e1',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
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
  completedButton: {
    backgroundColor: '#4CAF50',
  },
}); 