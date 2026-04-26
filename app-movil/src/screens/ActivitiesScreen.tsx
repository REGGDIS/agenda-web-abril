import { useCallback, useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';

import { ActivityCard } from '../components/ActivityCard';
import { PrimaryButton } from '../components/PrimaryButton';
import { isBackendConfigured } from '../config/environment';
import { listAprilActivities, updateActivityStatus } from '../services/activitiesService';
import { ActivityDetailScreen } from './ActivityDetailScreen';
import { colors, radius, spacing } from '../styles/theme';
import type { Activity, ActivityStatus } from '../types/activity';
import type { MobileAuthSession } from '../types/auth';

type ActivitiesScreenProps = {
  authSession: MobileAuthSession | null;
  onLogout: () => Promise<void>;
};

export function ActivitiesScreen({ authSession, onLogout }: ActivitiesScreenProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const loadActivities = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const loadedActivities = await listAprilActivities();
      setActivities(loadedActivities);
    } catch (error) {
      setActivities([]);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible cargar las actividades.',
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  const handleActivityStatusChange = useCallback(
    async (activityId: string, nextStatus: ActivityStatus) => {
      const updatedStatus = await updateActivityStatus(activityId, nextStatus);

      setActivities((currentActivities) =>
        currentActivities.map((activity) =>
          activity.id === activityId
            ? { ...activity, status: updatedStatus }
            : activity,
        ),
      );
      setSelectedActivity((currentActivity) =>
        currentActivity?.id === activityId
          ? { ...currentActivity, status: updatedStatus }
          : currentActivity,
      );
    },
    [],
  );

  const handleLogoutPress = useCallback(async () => {
    setIsLoggingOut(true);
    await onLogout();
  }, [onLogout]);

  const pendingCount = activities.filter((activity) => activity.status === 'pending').length;

  if (selectedActivity) {
    return (
      <ActivityDetailScreen
        activity={selectedActivity}
        onBack={() => setSelectedActivity(null)}
        onStatusChange={handleActivityStatusChange}
      />
    );
  }

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.kicker}>Abril</Text>
          <Text style={styles.title}>Mis actividades de abril</Text>
          <Text style={styles.subtitle}>
            {authSession
              ? `Sesion iniciada como ${authSession.usuario.nombre} (${authSession.rutNormalizado}).`
              : 'Inicia sesion para cargar tus actividades reales.'}
          </Text>
        </View>
      </View>

      <View style={styles.summary}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{activities.length}</Text>
          <Text style={styles.summaryLabel}>Total</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{pendingCount}</Text>
          <Text style={styles.summaryLabel}>Pendientes</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{isBackendConfigured ? 'API' : 'Local'}</Text>
          <Text style={styles.summaryLabel}>Origen</Text>
        </View>
      </View>

      {isLoading ? (
        <View style={styles.stateBox}>
          <Text style={styles.stateTitle}>Cargando actividades...</Text>
          <Text style={styles.stateText}>Buscando el listado visible para esta sesion.</Text>
        </View>
      ) : errorMessage ? (
        <View style={styles.stateBox}>
          <Text style={styles.errorTitle}>No fue posible cargar</Text>
          <Text style={styles.stateText}>{errorMessage}</Text>
          <PrimaryButton onPress={loadActivities} variant="secondary">Reintentar</PrimaryButton>
        </View>
      ) : activities.length === 0 ? (
        <View style={styles.stateBox}>
          <Text style={styles.stateTitle}>Sin actividades</Text>
          <Text style={styles.stateText}>
            No hay actividades visibles para esta sesion durante abril.
          </Text>
        </View>
      ) : (
        <FlatList
          contentContainerStyle={styles.listContent}
          data={activities}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ActivityCard activity={item} onPress={setSelectedActivity} />
          )}
        />
      )}

      <View style={styles.footer}>
        <PrimaryButton disabled={isLoggingOut} onPress={handleLogoutPress} variant="secondary">
          {isLoggingOut ? 'Cerrando...' : 'Cerrar sesión'}
        </PrimaryButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  header: {
    marginBottom: spacing.md,
  },
  kicker: {
    color: colors.accentStrong,
    fontSize: 13,
    fontWeight: '800',
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: '800',
    lineHeight: 34,
  },
  subtitle: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 22,
    marginTop: spacing.xs,
  },
  summary: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.md,
    padding: spacing.md,
  },
  summaryItem: {
    flex: 1,
  },
  summaryValue: {
    color: colors.text,
    fontSize: 20,
    fontWeight: '800',
  },
  summaryLabel: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '700',
    marginTop: 2,
    textTransform: 'uppercase',
  },
  listContent: {
    gap: spacing.md,
    paddingBottom: spacing.lg,
  },
  stateBox: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.sm,
    padding: spacing.md,
  },
  stateTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '800',
  },
  errorTitle: {
    color: colors.danger,
    fontSize: 16,
    fontWeight: '800',
  },
  stateText: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
  footer: {
    borderColor: colors.border,
    borderTopWidth: 1,
    paddingBottom: spacing.xl,
    paddingTop: spacing.md,
  },
});
