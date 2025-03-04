import { StyleSheet, Text, View, SafeAreaView, FlatList, Image, TouchableOpacity, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useRouter } from 'expo-router';

// Sample data for user's routes with more detailed information
const MY_ROUTES_DATA = [
  { 
    id: '1', 
    name: 'Mountain Trail', 
    hours: 2.5, 
    landmarks: 8, 
    distance: 5.2, 
    cost: 15,
    username: 'hikingfan23', 
    city: 'Denver, CO',
    photos: [
      'https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000',
      'https://images.unsplash.com/photo-1527489377706-5bf97e608852?q=80&w=1000',
      'https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?q=80&w=1000',
    ],
    likes: 128,
    comments: 24,
    rating: 4.7
  },
  { 
    id: '2', 
    name: 'Coastal Path', 
    hours: 1.5, 
    landmarks: 5, 
    distance: 3.8, 
    cost: 10,
    username: 'beachlover', 
    city: 'San Diego, CA',
    photos: [
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000',
      'https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1000',
      'https://images.unsplash.com/photo-1484821582734-6692f7262f72?q=80&w=1000',
    ],
    likes: 95,
    comments: 12,
    rating: 4.2
  },
  { 
    id: '3', 
    name: 'Forest Loop', 
    hours: 3.2, 
    landmarks: 12, 
    distance: 7.5, 
    cost: 25,
    username: 'natureexplorer', 
    city: 'Portland, OR',
    photos: [
      'https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000',
      'https://images.unsplash.com/photo-1511497584788-876760111969?q=80&w=1000',
      'https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=1000',
    ],
    likes: 210,
    comments: 32,
    rating: 4.9
  },
];

type RouteItemProps = {
  id: string;
  name: string;
  hours: number;
  landmarks: number;
  distance: number;
  cost: number;
  username: string;
  city: string;
  photos: string[];
  likes: number;
  comments: number;
  rating: number;
  onPress: (id: string) => void;
  onDelete: (id: string) => void;
};

const PhotoCarousel = ({ photos }: { photos: string[] }) => {
  return (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.carouselContainer}
    >
      {photos.map((photo, index) => (
        <Image 
          key={index} 
          source={{ uri: photo }} 
          style={styles.carouselImage} 
          resizeMode="cover"
        />
      ))}
    </ScrollView>
  );
};

const RouteItem = ({ 
  id,
  name, 
  hours, 
  landmarks, 
  distance, 
  cost,
  username, 
  city, 
  photos, 
  likes, 
  comments,
  rating,
  onPress,
  onDelete
}: RouteItemProps) => {
  // Generate stars based on rating
  const renderStars = () => {
    // Return just one full star
    return [
      <IconSymbol key="full-star" size={16} name="star.fill" color="#FFD700" />
    ];
  };

  return (
    <TouchableOpacity 
      style={styles.routeItem}
      onPress={() => onPress(id)}
      activeOpacity={0.7}
    >
      <View style={styles.routeHeader}>
        <Text style={styles.routeName}>{name}</Text>
        <TouchableOpacity 
          style={styles.deleteButton} 
          onPress={() => onDelete(id)}
        >
          <IconSymbol size={20} name="trash.fill" color="white" />
        </TouchableOpacity>
      </View>
      
      {/* Stats row with icons */}
      <View style={styles.statsRow}>
        <View style={styles.statItem}>
          <IconSymbol size={18} name="clock.fill" color="#8900e1" />
          <Text style={styles.statText}>{hours} hrs</Text>
        </View>
        <View style={styles.statItem}>
          <IconSymbol size={18} name="mappin.and.ellipse" color="#8900e1" />
          <Text style={styles.statText}>{landmarks} landmarks</Text>
        </View>
        <View style={styles.statItem}>
          <IconSymbol size={18} name="ruler.fill" color="#8900e1" />
          <Text style={styles.statText}>{distance} miles</Text>
        </View>
        <View style={styles.statItem}>
          <IconSymbol size={18} name="dollarsign.circle.fill" color="#8900e1" />
          <Text style={styles.statText}>${cost}</Text>
        </View>
      </View>
      
      {/* User info */}
      <View style={styles.userInfo}>
        <IconSymbol size={20} name="person.circle.fill" color="#666" />
        <Text style={styles.username}>{username}</Text>
        <Text style={styles.city}>{city}</Text>
      </View>
      
      {/* Photo carousel */}
      <PhotoCarousel photos={photos} />
      
      {/* Interaction buttons */}
      <View style={styles.interactionRow}>
        <TouchableOpacity style={styles.interactionButton}>
          <IconSymbol size={20} name="flame.fill" color="#FF6B00" />
          <Text style={styles.interactionText}>{likes}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.interactionButton}>
          <IconSymbol size={20} name="text.bubble.fill" color="#666" />
          <Text style={styles.interactionText}>{comments}</Text>
        </TouchableOpacity>
        
        {/* Rating display */}
        <View style={styles.ratingContainer}>
          <View style={styles.starsRow}>
            {renderStars()}
          </View>
          <Text style={styles.ratingText}>{rating.toFixed(1)}</Text>
        </View>
        
        <TouchableOpacity style={styles.startButton}>
          <IconSymbol size={18} name="play.fill" color="white" />
          <Text style={styles.startButtonText}>Start Route</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
};

export default function YourRoutesScreen() {
  const router = useRouter();
  const [routes, setRoutes] = useState(MY_ROUTES_DATA);
  
  const handleRoutePress = (id: string) => {
    router.push({
      pathname: '/route-details',
      params: { id }
    });
  };
  
  const handleDeleteRoute = (id: string) => {
    setRoutes(currentRoutes => currentRoutes.filter(route => route.id !== id));
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      {routes.length > 0 ? (
        <FlatList
          data={routes}
          renderItem={({ item }) => (
            <RouteItem 
              id={item.id}
              name={item.name} 
              hours={item.hours} 
              landmarks={item.landmarks} 
              distance={item.distance} 
              cost={item.cost}
              username={item.username} 
              city={item.city} 
              photos={item.photos} 
              likes={item.likes} 
              comments={item.comments}
              rating={item.rating}
              onPress={handleRoutePress}
              onDelete={handleDeleteRoute}
            />
          )}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContent}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>You haven't added any routes yet.</Text>
          <Text style={styles.emptySubtext}>Your saved routes will appear here.</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  listContent: {
    padding: 16,
  },
  routeItem: {
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  routeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  routeName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  deleteButton: {
    backgroundColor: '#f44336',
    padding: 8,
    borderRadius: 8,
    marginLeft: 10,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    marginLeft: 6,
    color: '#555',
    fontWeight: '500',
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  username: {
    fontWeight: '600',
    marginLeft: 8,
    marginRight: 6,
    color: '#333',
  },
  city: {
    color: '#666',
    fontSize: 14,
  },
  carouselContainer: {
    paddingVertical: 8,
  },
  carouselImage: {
    width: 200,
    height: 150,
    borderRadius: 8,
    marginRight: 8,
  },
  interactionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  interactionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  interactionText: {
    marginLeft: 6,
    color: '#666',
    fontWeight: '500',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  starsRow: {
    flexDirection: 'row',
    marginRight: 6,
  },
  ratingText: {
    color: '#666',
    fontWeight: '500',
  },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8900e1',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  startButtonText: {
    color: 'white',
    fontWeight: '600',
    marginLeft: 6,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '500',
    marginBottom: 8,
    textAlign: 'center',
    color: '#333',
  },
  emptySubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});