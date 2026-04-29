import { useState } from 'react';
import {
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { loginWithRut } from '../services/authService';
import { colors, radius, spacing } from '../styles/theme';
import type { MobileAuthSession } from '../types/auth';

const agendaAbrilLogo = require('../../assets/branding/agenda-abril-logo.png');

type LoginScreenProps = {
  noticeMessage?: string;
  onLoginSuccess: (session: MobileAuthSession) => void;
};

export function LoginScreen({
  noticeMessage = '',
  onLoginSuccess,
}: LoginScreenProps) {
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
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.screen}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.brandBlock}>
          <View style={styles.logoMark}>
            <Image
              accessibilityLabel="Logo de Agenda Abril"
              resizeMode="contain"
              source={agendaAbrilLogo}
              style={styles.logoImage}
            />
          </View>
          <Text style={styles.kicker}>AGENDA ABRIL MÓVIL</Text>
          <Text style={styles.title}>Ingreso a Agenda Abril</Text>
          <Text style={styles.subtitle}>
            Ingresa con tu RUT para acceder a tus actividades de abril desde la app móvil.
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
            El sistema validará tu acceso y cargará tus actividades.
          </Text>
          {noticeMessage ? <Text style={styles.notice}>{noticeMessage}</Text> : null}
          {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}
          <PrimaryButton disabled={isLoading || !rut.trim()} onPress={handleSubmit}>
            {isLoading ? 'Validando...' : 'Ingresar'}
          </PrimaryButton>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.lg,
    paddingBottom: spacing.xl,
  },
  brandBlock: {
    marginBottom: spacing.xl,
  },
  logoMark: {
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.lg,
    borderWidth: 1,
    height: 76,
    justifyContent: 'center',
    marginBottom: spacing.lg,
    padding: spacing.sm,
    width: 76,
  },
  logoImage: {
    height: '100%',
    width: '100%',
  },
  kicker: {
    color: colors.accentStrong,
    fontSize: 12,
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
  notice: {
    backgroundColor: colors.accentSoft,
    borderColor: '#f7c7bd',
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.accentStrong,
    fontSize: 13,
    fontWeight: '700',
    lineHeight: 19,
    marginBottom: spacing.sm,
    padding: spacing.sm,
  },
});
