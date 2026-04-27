import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';

import { colors, radius, spacing } from '../styles/theme';

type PrimaryButtonProps = {
  children: ReactNode;
  disabled?: boolean;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
};

export function PrimaryButton({
  children,
  disabled = false,
  onPress,
  variant = 'primary',
}: PrimaryButtonProps) {
  const isPrimary = variant === 'primary';
  const isDanger = variant === 'danger';

  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        isPrimary ? styles.primary : isDanger ? styles.danger : styles.secondary,
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
    >
      <Text
        style={[
          styles.label,
          isPrimary || isDanger ? styles.primaryLabel : styles.secondaryLabel,
        ]}
      >
        {children}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: 'center',
    borderRadius: radius.sm,
    justifyContent: 'center',
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  primary: {
    backgroundColor: colors.accent,
  },
  secondary: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderWidth: 1,
  },
  danger: {
    backgroundColor: colors.danger,
  },
  pressed: {
    opacity: 0.82,
  },
  disabled: {
    opacity: 0.58,
  },
  label: {
    fontSize: 16,
    fontWeight: '700',
  },
  primaryLabel: {
    color: '#ffffff',
  },
  secondaryLabel: {
    color: colors.text,
  },
});
