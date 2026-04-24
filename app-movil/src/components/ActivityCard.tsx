import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../styles/theme';
import type { Activity } from '../types/activity';

type ActivityCardProps = {
  activity: Activity;
};

export function ActivityCard({ activity }: ActivityCardProps) {
  const isDone = activity.status === 'done';

  return (
    <View style={[styles.card, isDone ? styles.doneCard : styles.pendingCard]}>
      <View style={styles.header}>
        <Text style={styles.title}>{activity.title}</Text>
        <View style={[styles.badge, isDone ? styles.doneBadge : styles.pendingBadge]}>
          <Text style={[styles.badgeText, isDone ? styles.doneText : styles.pendingText]}>
            {isDone ? 'Realizada' : 'Pendiente'}
          </Text>
        </View>
      </View>

      <Text style={styles.meta}>{activity.dateLabel} · {activity.timeLabel}</Text>
      <Text style={styles.place}>{activity.place}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderLeftWidth: 4,
    borderRadius: radius.md,
    borderWidth: 1,
    padding: spacing.md,
  },
  pendingCard: {
    borderLeftColor: colors.accent,
  },
  doneCard: {
    borderLeftColor: colors.success,
  },
  header: {
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  title: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '700',
    lineHeight: 24,
  },
  badge: {
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  pendingBadge: {
    backgroundColor: colors.accentSoft,
  },
  doneBadge: {
    backgroundColor: colors.successSoft,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  pendingText: {
    color: colors.accentStrong,
  },
  doneText: {
    color: colors.success,
  },
  meta: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '600',
    marginTop: spacing.md,
  },
  place: {
    color: colors.muted,
    fontSize: 14,
    marginTop: spacing.xs,
  },
});
