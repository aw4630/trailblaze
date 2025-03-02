import { Stack, Tabs, useRouter } from 'expo-router';
import React from 'react';
import { Platform, View, TouchableOpacity } from 'react-native';

import { IconSymbol } from '@/components/ui/IconSymbol';

export default function TabLayout() {
  const router = useRouter();
  
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#8900e1',
        headerShown: true,
        headerStyle: {
          backgroundColor: 'white',
          elevation: 0,
          shadowOpacity: 0,
          borderBottomWidth: 1,
          borderBottomColor: '#f0f0f0',
        },
        headerTitleStyle: {
          fontWeight: 'bold',
          fontSize: 18,
        },
        headerTitleAlign: 'center',
        headerLeft: () => (
          <TouchableOpacity 
            style={{ marginLeft: 15 }}
            onPress={() => router.push('/profile')}
          >
            <IconSymbol size={28} name="person.crop.circle.fill" color="#333" />
          </TouchableOpacity>
        ),
        headerRight: () => (
          <TouchableOpacity 
            style={{ marginRight: 15 }}
            onPress={() => router.push('/chat')}
          >
            <IconSymbol size={28} name="bubble.right.fill" color="#333" />
          </TouchableOpacity>
        ),
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopColor: '#f0f0f0',
          height: 60,
          ...Platform.select({
            ios: {
              shadowColor: '#000',
              shadowOffset: { width: 0, height: -2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
            },
            android: {
              elevation: 8,
            },
          }),
        },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          href: null, // This hides the tab from the bottom navigation
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          href: null, // This hides the tab from the bottom navigation
        }}
      />
      <Tabs.Screen
        name="home/index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => <IconSymbol size={24} name="house.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="routes/index"
        options={{
          title: 'Routes',
          tabBarIcon: ({ color }) => <IconSymbol size={24} name="map.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="camera/index"
        options={{
          title: '',
          headerTitle: 'Camera',
          tabBarIcon: () => (
            <View style={{
              width: 56,
              height: 56,
              backgroundColor: '#8900e1',
              borderRadius: 28,
              justifyContent: 'center',
              alignItems: 'center',
              marginBottom: 25,
              shadowColor: '#8900e1',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.5,
              shadowRadius: 4,
              elevation: 5,
            }}>
              <IconSymbol size={30} name="camera.fill" color="white" />
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="add-route/index"
        options={{
          title: 'Add Route',
          tabBarIcon: ({ color }) => <IconSymbol size={24} name="plus.circle.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="your-routes/index"
        options={{
          title: 'Your Routes',
          tabBarIcon: ({ color }) => <IconSymbol size={24} name="person.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}
