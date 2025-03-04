import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Switch, ScrollView, Alert } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useAuth } from '@/context/AuthContext';

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout, accessibilityEnabled, updateAccessibility } = useAuth();
  
  // Toggle accessibility setting
  const toggleAccessibility = () => {
    updateAccessibility(!accessibilityEnabled);
  };
  
  // Handle sign out
  const handleSignOut = () => {
    Alert.alert(
      "Sign Out",
      "Are you sure you want to sign out?",
      [
        {
          text: "Cancel",
          style: "cancel"
        },
        { 
          text: "Sign Out", 
          onPress: () => {
            logout();
            router.replace('/');
          },
          style: "destructive"
        }
      ]
    );
  };
  
  // Handle sign in (for demo purposes)
  const handleSignIn = () => {
    // In a real app, this would validate credentials
    router.replace('/');
  };
  
  return (
    <>
      <Stack.Screen 
        options={{
          title: 'Profile',
          headerShown: true,
          headerLeft: () => (
            <TouchableOpacity 
              style={{ marginLeft: 15 }}
              onPress={() => router.back()}
            >
              <IconSymbol size={28} name="chevron.left" color="#333" />
            </TouchableOpacity>
          ),
        }} 
      />
      
      <ScrollView style={styles.container}>
        {user ? (
          <>
            {/* Profile Header with Avatar */}
            <View style={styles.profileHeader}>
              <Image 
                source={{ uri: user.avatar }} 
                style={styles.avatar} 
              />
              <View style={styles.userInfo}>
                <Text style={styles.userName}>{user.name}</Text>
                <Text style={styles.userEmail}>{user.email}</Text>
              </View>
            </View>
            
            {/* Settings Section */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Settings</Text>
              
              {/* Accessibility Toggle */}
              <View style={styles.settingItem}>
                <View style={styles.settingTextContainer}>
                  <IconSymbol size={24} name="accessibility" color="#8900e1" />
                  <Text style={styles.settingText}>Accessibility</Text>
                </View>
                <Switch
                  trackColor={{ false: "#d9d9d9", true: "#c4a0e7" }}
                  thumbColor={accessibilityEnabled ? "#8900e1" : "#f4f3f4"}
                  ios_backgroundColor="#d9d9d9"
                  onValueChange={toggleAccessibility}
                  value={accessibilityEnabled}
                />
              </View>
              
              <Text style={styles.settingDescription}>
                When enabled, route suggestions will prioritize accessible paths and locations.
              </Text>
            </View>
            
            {/* Account Section */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Account</Text>
              
              <TouchableOpacity style={styles.button} onPress={handleSignOut}>
                <IconSymbol size={24} name="rectangle.portrait.and.arrow.right" color="#ff3b30" />
                <Text style={[styles.buttonText, styles.signOutText]}>Sign Out</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          // Login Screen
          <View style={styles.loginContainer}>
            <IconSymbol size={80} name="person.crop.circle" color="#8900e1" />
            <Text style={styles.loginTitle}>Sign In</Text>
            <Text style={styles.loginSubtitle}>Sign in to access your profile and saved routes</Text>
            
            <TouchableOpacity style={styles.signInButton} onPress={handleSignIn}>
              <Text style={styles.signInButtonText}>Sign In</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.createAccountButton}>
              <Text style={styles.createAccountText}>Create Account</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  profileHeader: {
    backgroundColor: 'white',
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#e0e0e0',
  },
  userInfo: {
    marginLeft: 20,
  },
  userName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
  },
  userEmail: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  section: {
    backgroundColor: 'white',
    padding: 20,
    marginTop: 20,
    borderRadius: 10,
    marginHorizontal: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
  },
  settingTextContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingText: {
    fontSize: 16,
    marginLeft: 10,
    color: '#333',
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
    marginBottom: 10,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  buttonText: {
    fontSize: 16,
    marginLeft: 10,
  },
  signOutText: {
    color: '#ff3b30',
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    marginTop: 100,
  },
  loginTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#333',
  },
  loginSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 30,
  },
  signInButton: {
    backgroundColor: '#8900e1',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 10,
    width: '100%',
    alignItems: 'center',
    marginBottom: 15,
  },
  signInButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  createAccountButton: {
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 10,
    width: '100%',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#8900e1',
  },
  createAccountText: {
    color: '#8900e1',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 