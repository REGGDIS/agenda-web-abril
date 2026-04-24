import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';

import { ActivitiesScreen } from './src/screens/ActivitiesScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { colors } from './src/styles/theme';

type AppRoute = 'login' | 'activities';

export default function App() {
  const [route, setRoute] = useState<AppRoute>('login');

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      {route === 'login' ? (
        <LoginScreen onEnterDemo={() => setRoute('activities')} />
      ) : (
        <ActivitiesScreen onLogout={() => setRoute('login')} />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
});
