import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors, radius, spacing } from '../styles/theme';
import type { Activity, ActivityStatus } from '../types/activity';

type ActivityDetailScreenProps = {
  activity: Activity;
  onBack: () => void;
  onDelete: (activityId: string) => Promise<void>;
  onEdit: (activity: Activity) => void;
  onStatusChange: (activityId: string, nextStatus: ActivityStatus) => Promise<void>;
};

export function ActivityDetailScreen({
  activity,
  onBack,
  onDelete,
  onEdit,
  onStatusChange,
}: ActivityDetailScreenProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const isDone = activity.status === 'done';
  const nextStatus: ActivityStatus = isDone ? 'pending' : 'done';

  async function handleStatusChange() {
    setIsUpdating(true);
    setErrorMessage('');

    try {
      await onStatusChange(activity.id, nextStatus);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible actualizar la actividad.',
      );
    } finally {
      setIsUpdating(false);
    }
  }

  function handleDeletePress() {
    Alert.alert(
      'Eliminar actividad',
      `Se eliminara "${activity.title}". Esta accion no se puede deshacer.`,
      [
        {
          text: 'Cancelar',
          style: 'cancel',
        },
        {
          text: 'Eliminar',
          onPress: handleDeleteConfirm,
          style: 'destructive',
        },
      ],
    );
  }

  async function handleDeleteConfirm() {
    setIsDeleting(true);
    setErrorMessage('');

    try {
      await onDelete(activity.id);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible eliminar la actividad.',
      );
    } finally {
      setIsDeleting(false);
    }
  }

  const actionsDisabled = isUpdating || isDeleting;

  return (
    <View style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>Detalle de actividad</Text>
        <Text style={styles.title}>{activity.title}</Text>

        <View style={[styles.statusBadge, isDone ? styles.doneBadge : styles.pendingBadge]}>
          <Text style={[styles.statusText, isDone ? styles.doneText : styles.pendingText]}>
            {isDone ? 'Realizada' : 'Pendiente'}
          </Text>
        </View>

        <View style={styles.card}>
          <DetailRow label="Descripcion" value={activity.description || 'Sin descripcion'} />
          <DetailRow label="Fecha" value={activity.dateLabel} />
          <DetailRow label="Hora inicio" value={activity.timeLabel} />
          <DetailRow label="Hora fin" value={activity.endTimeLabel} />
          <DetailRow label="Categoria" value={activity.categoryLabel || 'Sin categoria'} />
          <DetailRow label="Emoji" value={activity.emoji || 'Sin emoji'} />
          <DetailRow label="Lugar" value={activity.place} />
          <DetailRow label="ID actividad" value={activity.id} />
        </View>
      </ScrollView>

      <View style={styles.footer}>
        {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        <PrimaryButton disabled={actionsDisabled} onPress={() => onEdit(activity)} variant="secondary">
          Editar actividad
        </PrimaryButton>
        <PrimaryButton disabled={actionsDisabled} onPress={handleStatusChange}>
          {isUpdating
            ? 'Actualizando...'
            : isDone
              ? 'Marcar como pendiente'
              : 'Marcar como realizada'}
        </PrimaryButton>
        <PrimaryButton disabled={actionsDisabled} onPress={handleDeletePress} variant="danger">
          {isDeleting ? 'Eliminando...' : 'Eliminar actividad'}
        </PrimaryButton>
        <PrimaryButton disabled={actionsDisabled} onPress={onBack} variant="secondary">
          Volver a la lista
        </PrimaryButton>
      </View>
    </View>
  );
}

type DetailRowProps = {
  label: string;
  value: string;
};

function DetailRow({ label, value }: DetailRowProps) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  content: {
    paddingBottom: spacing.lg,
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
  statusBadge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    marginTop: spacing.md,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  pendingBadge: {
    backgroundColor: colors.accentSoft,
  },
  doneBadge: {
    backgroundColor: colors.successSoft,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  pendingText: {
    color: colors.accentStrong,
  },
  doneText: {
    color: colors.success,
  },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    marginTop: spacing.md,
    padding: spacing.md,
  },
  row: {
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    paddingVertical: spacing.sm,
  },
  rowLabel: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '800',
    marginBottom: 2,
    textTransform: 'uppercase',
  },
  rowValue: {
    color: colors.text,
    fontSize: 15,
    lineHeight: 22,
  },
  footer: {
    borderColor: colors.border,
    borderTopWidth: 1,
    gap: spacing.sm,
    paddingBottom: spacing.xl,
    paddingTop: spacing.md,
  },
  errorText: {
    color: colors.danger,
    fontSize: 14,
    lineHeight: 20,
    textAlign: 'center',
  },
});
