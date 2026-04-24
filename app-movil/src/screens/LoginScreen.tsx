import { StyleSheet, Text, TextInput, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { colors, radius, spacing } from '../styles/theme';

type LoginScreenProps = {
  onEnterDemo: () => void;
};

export function LoginScreen({ onEnterDemo }: LoginScreenProps) {
  return (
    <View style={styles.screen}>
      <View style={styles.brandBlock}>
        <View style={styles.logoMark}>
          <Text style={styles.logoText}>AA</Text>
        </View>
        <Text style={styles.kicker}>Agenda Abril Movil</Text>
        <Text style={styles.title}>Ingreso a Agenda Abril</Text>
        <Text style={styles.subtitle}>
          Primera version movil con flujo visual y datos locales de ejemplo.
        </Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>RUT</Text>
        <TextInput
          editable={false}
          placeholder="12.345.678-5"
          placeholderTextColor={colors.muted}
          style={styles.input}
          value="12.345.678-5"
        />
        <Text style={styles.helper}>Login mock: aun no valida credenciales ni consulta API.</Text>
        <PrimaryButton onPress={onEnterDemo}>Entrar a demo</PrimaryButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  brandBlock: {
    marginBottom: spacing.xl,
  },
  logoMark: {
    alignItems: 'center',
    backgroundColor: colors.accentSoft,
    borderColor: '#f7c7bd',
    borderRadius: radius.md,
    borderWidth: 1,
    height: 56,
    justifyContent: 'center',
    marginBottom: spacing.md,
    width: 56,
  },
  logoText: {
    color: colors.accentStrong,
    fontSize: 18,
    fontWeight: '800',
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
    fontSize: 32,
    fontWeight: '800',
    lineHeight: 38,
  },
  subtitle: {
    color: colors.muted,
    fontSize: 16,
    lineHeight: 23,
    marginTop: spacing.sm,
  },
  form: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.lg,
    borderWidth: 1,
    gap: spacing.sm,
    padding: spacing.md,
  },
  label: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '700',
  },
  input: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.text,
    fontSize: 16,
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  helper: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
    marginBottom: spacing.sm,
  },
});
