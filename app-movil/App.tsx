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
  const [loginMessage, setLoginMessage] = useState('');

  const handleLoginSuccess = (session: MobileAuthSession) => {
    setAuthSession(session);
    setLoginMessage('');
    setRoute('activities');
  };

  const handleSessionExpired = () => {
    setAuthSession(null);
    setLoginMessage('Tu sesión expiró. Ingresa nuevamente.');
    setRoute('login');
  };

  const handleLogout = async () => {
    try {
      await logoutMobileSession();
    } finally {
      setAuthSession(null);
      setLoginMessage('');
      setRoute('login');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      {route === 'login' ? (
        <LoginScreen
          noticeMessage={loginMessage}
          onLoginSuccess={handleLoginSuccess}
        />
      ) : (
        <ActivitiesScreen
          authSession={authSession}
          onLogout={handleLogout}
          onSessionExpired={handleSessionExpired}
        />
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
