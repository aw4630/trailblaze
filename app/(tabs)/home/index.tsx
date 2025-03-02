import { StyleSheet, Text, View, SafeAreaView, ScrollView } from 'react-native';
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { IconSymbol } from '@/components/ui/IconSymbol';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export default function HomeScreen() {
  // Mock data for dashboard stats
  const dashboardStats = {
    locationsVisited: 12,
    routesCreated: 8,
    firesGot: 24,
    moneySpent: 145,
    routesCompleted: 7,
    distanceCrossed: 42.5, // in kilometers
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Dashboard</Text>
          <Text style={styles.subtitle}>Your route statistics</Text>
        </View>
        
        <View style={styles.statsContainer}>
          {/* First row */}
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <MaterialIcons name="location-on" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>{dashboardStats.locationsVisited}</Text>
              <Text style={styles.statLabel}>Locations Visited</Text>
            </View>
            
            <View style={styles.statCard}>
              <MaterialIcons name="map" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>{dashboardStats.routesCreated}</Text>
              <Text style={styles.statLabel}>Routes Created</Text>
            </View>
          </View>
          
          {/* Second row */}
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <MaterialIcons name="local-fire-department" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>{dashboardStats.firesGot}</Text>
              <Text style={styles.statLabel}>Fires Got</Text>
            </View>
            
            <View style={styles.statCard}>
              <MaterialIcons name="attach-money" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>${dashboardStats.moneySpent}</Text>
              <Text style={styles.statLabel}>Money Spent</Text>
            </View>
          </View>
          
          {/* Third row */}
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <MaterialIcons name="check-circle" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>{dashboardStats.routesCompleted}</Text>
              <Text style={styles.statLabel}>Routes Completed</Text>
            </View>
            
            <View style={styles.statCard}>
              <MaterialIcons name="directions-walk" size={28} color="#8900e1" style={styles.iconStyle} />
              <Text style={styles.statValue}>{dashboardStats.distanceCrossed} km</Text>
              <Text style={styles.statLabel}>Distance Crossed</Text>
            </View>
          </View>
        </View>
        
        <View style={styles.recentActivity}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <View style={styles.activityCard}>
            <Text style={styles.activityText}>You completed "Mountain Trail" route</Text>
            <Text style={styles.activityDate}>2 days ago</Text>
          </View>
          <View style={styles.activityCard}>
            <Text style={styles.activityText}>You created a new route "City Center"</Text>
            <Text style={styles.activityDate}>5 days ago</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingTop: 30,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  statsContainer: {
    padding: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    width: '48%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  iconStyle: {
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 4,
  },
  recentActivity: {
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  activityCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 1,
  },
  activityText: {
    fontSize: 16,
    color: '#333',
  },
  activityDate: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
}); 