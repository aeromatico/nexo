import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';

import { queryClient } from './src/services/queryClient';
import { useAuthStore } from './src/store/authStore';

// Navigation
import { DashboardScreen, InvoicesScreen, OrdersScreen, ProfileScreen, QRScannerScreen } from './src/screens';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        tabBarActiveTintColor: '#4472C4',
        tabBarInactiveTintColor: '#94A3B8',
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          title: 'Inicio',
          tabBarLabel: 'Inicio'
        }}
      />
      <Tab.Screen
        name="Invoices"
        component={InvoicesScreen}
        options={{
          title: 'Facturas',
          tabBarLabel: 'Facturas'
        }}
      />
      <Tab.Screen
        name="Orders"
        component={OrdersScreen}
        options={{
          title: 'Pedidos',
          tabBarLabel: 'Pedidos'
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          title: 'Perfil',
          tabBarLabel: 'Perfil'
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const { user, isInitializing, initializeAuth } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  if (isInitializing) {
    return null;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer>
        <Stack.Navigator>
          {user ? (
            <>
              <Stack.Screen
                name="Main"
                component={TabNavigator}
                options={{ headerShown: false }}
              />
              <Stack.Screen
                name="QRScanner"
                component={QRScannerScreen}
                options={{ title: 'Escanear QR' }}
              />
            </>
          ) : (
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ headerShown: false }}
            />
          )}
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar barStyle="light-content" />
    </QueryClientProvider>
  );
}
