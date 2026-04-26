import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';

import { ActivitiesScreen } from './src/screens/ActivitiesScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { logoutMobileSession } from './src/services/authService';
import { colors } from './src/styles/theme';
import type { MobileAuthSession } from './src/types/auth';

type AppRoute = 'login' | 'activities';

export default function App() {
  const [route, setRoute] = useState<AppRoute>('login');
  const [authSession, setAuthSession] = useState<MobileAuthSession | null>(null);

  const handleLoginSuccess = (session: MobileAuthSession) => {
    setAuthSession(session);
    setRoute('activities');
  };

  const handleLogout = async () => {
    try {
      await logoutMobileSession();
    } finally {
      setAuthSession(null);
      setRoute('login');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      {route === 'login' ? (
        <LoginScreen onLoginSuccess={handleLoginSuccess} />
      ) : (
        <ActivitiesScreen authSession={authSession} onLogout={handleLogout} />
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
