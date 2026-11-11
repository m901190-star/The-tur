import { Ionicons } from '@expo/vector-icons';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { ActivityIndicator, I18nManager, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { RootStackParamList, TabParamList } from './src/navigation';
import { PlantDetailScreen } from './src/screens/PlantDetailScreen';
import { PlantFormScreen } from './src/screens/PlantFormScreen';
import { PlantsScreen } from './src/screens/PlantsScreen';
import { SettingsScreen } from './src/screens/SettingsScreen';
import { TodayScreen } from './src/screens/TodayScreen';
import { PlantsProvider, usePlants } from './src/state/PlantsContext';
import { colors } from './src/theme';

// Every row in this app is laid out with an explicit `row-reverse` and
// textAlign:'right', which already reads right-to-left. If the OS flipped the
// layout as well — which it does by itself on a Hebrew device — the two would
// cancel out and the UI would come back left-to-right. Pin the direction.
I18nManager.allowRTL(false);
I18nManager.forceRTL(false);

const Tabs = createBottomTabNavigator<TabParamList>();
const Stack = createNativeStackNavigator<RootStackParamList>();

const TAB_ICONS: Record<keyof TabParamList, keyof typeof Ionicons.glyphMap> = {
  Today: 'water-outline',
  Plants: 'leaf-outline',
  Settings: 'settings-outline',
};

function TabsNavigator() {
  return (
    <Tabs.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarIcon: ({ color, size }) => (
          <Ionicons name={TAB_ICONS[route.name]} size={size} color={color} />
        ),
      })}
    >
      <Tabs.Screen name="Today" component={TodayScreen} options={{ title: 'היום' }} />
      <Tabs.Screen name="Plants" component={PlantsScreen} options={{ title: 'העציצים' }} />
      <Tabs.Screen name="Settings" component={SettingsScreen} options={{ title: 'הגדרות' }} />
    </Tabs.Navigator>
  );
}

function RootNavigator() {
  const { ready } = usePlants();

  if (!ready) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.primary} size="large" />
      </View>
    );
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.background },
        headerTintColor: colors.text,
        headerTitleAlign: 'center',
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen
        name="Tabs"
        component={TabsNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="PlantForm"
        component={PlantFormScreen}
        options={({ route }) => ({
          title: route.params?.plantId ? 'עריכת עציץ' : 'עציץ חדש',
        })}
      />
      <Stack.Screen
        name="PlantDetail"
        component={PlantDetailScreen}
        options={{ title: 'העציץ' }}
      />
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <PlantsProvider>
        <StatusBar style="dark" />
        <NavigationContainer>
          <RootNavigator />
        </NavigationContainer>
      </PlantsProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
  },
});
