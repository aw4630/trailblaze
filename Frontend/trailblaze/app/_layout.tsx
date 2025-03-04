import { DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from '@/context/AuthContext';

export default function RootLayout() {
  // Force light theme
  const lightTheme = {
    ...DefaultTheme,
    colors: {
      ...DefaultTheme.colors,
      background: 'white',
      text: '#333333',
      primary: '#8900e1',
    },
  };

  return (
    <AuthProvider>
      <ThemeProvider value={lightTheme}>
        <StatusBar style="dark" />
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="profile" options={{ headerShown: false }} />
        </Stack>
      </ThemeProvider>
    </AuthProvider>
  );
}
