import { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, TextInput, View } from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { loginWithRut } from '../services/authService';
import { colors, radius, spacing } from '../styles/theme';
import type { MobileAuthSession } from '../types/auth';

type LoginScreenProps = {
  onLoginSuccess: (session: MobileAuthSession) => void;
};

export function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const [rut, setRut] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setErrorMessage('');
    setIsLoading(true);

    try {
      const session = await loginWithRut(rut);
      onLoginSuccess(session);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible iniciar sesion en este momento.',
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.screen}
    >
      <View style={styles.brandBlock}>
        <View style={styles.logoMark}>
          <Text style={styles.logoText}>AA</Text>
        </View>
        <Text style={styles.kicker}>Agenda Abril Movil</Text>
        <Text style={styles.title}>Ingreso a Agenda Abril</Text>
        <Text style={styles.subtitle}>
          Ingresa con tu RUT para crear una sesion real en el backend.
        </Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>RUT</Text>
        <TextInput
          autoCapitalize="characters"
          editable={!isLoading}
          keyboardType="default"
          onChangeText={setRut}
          onSubmitEditing={handleSubmit}
          placeholder="12.345.678-5"
          placeholderTextColor={colors.muted}
          returnKeyType="send"
          style={styles.input}
          value={rut}
        />
        <Text style={styles.helper}>
          La app usa el backend configurado para Expo Go; las actividades siguen siendo mock.
        </Text>
        {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}
        <PrimaryButton disabled={isLoading || !rut.trim()} onPress={handleSubmit}>
          {isLoading ? 'Validando...' : 'Validar ingreso'}
        </PrimaryButton>
      </View>
    </KeyboardAvoidingView>
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
  error: {
    backgroundColor: '#fde8e8',
    borderColor: '#f4b4b4',
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.danger,
    fontSize: 13,
    lineHeight: 19,
    marginBottom: spacing.sm,
    padding: spacing.sm,
  },
});
