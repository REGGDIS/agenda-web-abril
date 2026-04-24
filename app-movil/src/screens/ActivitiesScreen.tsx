import { FlatList, StyleSheet, Text, View } from 'react-native';

import { ActivityCard } from '../components/ActivityCard';
import { PrimaryButton } from '../components/PrimaryButton';
import { mockActivities } from '../data/mockActivities';
import { isBackendConfigured } from '../config/environment';
import { colors, radius, spacing } from '../styles/theme';
import type { MobileAuthSession } from '../types/auth';

type ActivitiesScreenProps = {
  authSession: MobileAuthSession | null;
  onLogout: () => void;
};

export function ActivitiesScreen({ authSession, onLogout }: ActivitiesScreenProps) {
  const pendingCount = mockActivities.filter((activity) => activity.status === 'pending').length;

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.kicker}>Abril</Text>
          <Text style={styles.title}>Mis actividades de abril</Text>
          <Text style={styles.subtitle}>
            {authSession
              ? `Sesion iniciada como ${authSession.usuario.nombre} (${authSession.rutNormalizado}).`
              : 'Datos mock locales para validar la base movil.'}
          </Text>
        </View>
      </View>

      <View style={styles.summary}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{mockActivities.length}</Text>
          <Text style={styles.summaryLabel}>Total</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{pendingCount}</Text>
          <Text style={styles.summaryLabel}>Pendientes</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{isBackendConfigured ? 'API' : 'Mock'}</Text>
          <Text style={styles.summaryLabel}>Origen</Text>
        </View>
      </View>

      <FlatList
        contentContainerStyle={styles.listContent}
        data={mockActivities}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ActivityCard activity={item} />}
      />

      <View style={styles.footer}>
        <PrimaryButton onPress={onLogout} variant="secondary">Salir de demo</PrimaryButton>
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
    paddingBottom: spacing.md,
  },
  footer: {
    borderColor: colors.border,
    borderTopWidth: 1,
    paddingVertical: spacing.md,
  },
});
