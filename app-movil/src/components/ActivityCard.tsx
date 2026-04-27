import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../styles/theme';
import type { Activity } from '../types/activity';

type ActivityCardProps = {
  activity: Activity;
  onPress?: (activity: Activity) => void;
};

export function ActivityCard({ activity, onPress }: ActivityCardProps) {
  const isDone = activity.status === 'done';

  return (
    <Pressable
      accessibilityHint="Abre el detalle de la actividad"
      accessibilityRole="button"
      onPress={() => onPress?.(activity)}
      style={({ pressed }) => [
        styles.card,
        isDone ? styles.doneCard : styles.pendingCard,
        pressed && styles.pressed,
      ]}
    >
      <View style={styles.header}>
        <Text style={styles.title}>{activity.title}</Text>
        <View style={[styles.badge, isDone ? styles.doneBadge : styles.pendingBadge]}>
          <Text style={[styles.badgeText, isDone ? styles.doneText : styles.pendingText]}>
            {isDone ? 'Realizada' : 'Pendiente'}
          </Text>
        </View>
      </View>

      <Text style={styles.meta}>{activity.dateLabel} · {activity.timeLabel}</Text>
      {activity.categoryLabel || activity.emoji ? (
        <View style={styles.categoryRow}>
          {activity.emoji ? (
            <Text style={styles.emojiBadge}>{activity.emoji}</Text>
          ) : null}
          <Text style={styles.category}>
            {activity.categoryLabel ?? 'Sin categoria'}
          </Text>
        </View>
      ) : null}
      <Text style={styles.place}>{activity.place}</Text>
    </Pressable>
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
  pressed: {
    opacity: 0.82,
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
  categoryRow: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  emojiBadge: {
    backgroundColor: colors.accentSoft,
    borderColor: '#f7c7bd',
    borderRadius: radius.sm,
    borderWidth: 1,
    fontSize: 16,
    minWidth: 30,
    overflow: 'hidden',
    paddingHorizontal: 5,
    paddingVertical: 2,
    textAlign: 'center',
  },
  category: {
    color: colors.accentStrong,
    fontSize: 13,
    fontWeight: '700',
  },
});
