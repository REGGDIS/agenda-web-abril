import { useCallback, useEffect, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';

import { PrimaryButton } from '../components/PrimaryButton';
import { isMobileSessionExpiredError } from '../services/apiClient';
import { listActivityCategories } from '../services/activitiesService';
import { registerMobileSessionActivity } from '../services/authService';
import { colors, radius, spacing } from '../styles/theme';
import type {
  Activity,
  ActivityCategory,
  CreateActivityPayload,
} from '../types/activity';
import type { MobileAuthSession } from '../types/auth';

type CreateActivityScreenProps = {
  authSession: MobileAuthSession | null;
  initialActivity?: Activity;
  mode?: 'create' | 'edit';
  onCancel: () => void;
  onCreate: (payload: CreateActivityPayload) => Promise<void>;
  onSessionExpired: () => void;
};

type FormState = Omit<CreateActivityPayload, 'id_usuario' | 'realizada'>;
type TextFieldName = keyof FormState;

const initialForm: FormState = {
  titulo: '',
  descripcion: '',
  fecha_actividad: '2026-04-01',
  hora_inicio: '09:00',
  hora_fin: '10:00',
  id_categoria: '',
  emoji: '',
  lugar: '',
};

const emojiSuggestions = ['📌', '💊', '📚', '🤝', '🎉', '🏃', '🗓️', '✅'];

export function CreateActivityScreen({
  authSession,
  initialActivity,
  mode = 'create',
  onCancel,
  onCreate,
  onSessionExpired,
}: CreateActivityScreenProps) {
  const isEditing = mode === 'edit';
  const [form, setForm] = useState<FormState>(() => buildInitialForm(initialActivity));
  const [realizada, setRealizada] = useState(initialActivity?.status === 'done');
  const [categories, setCategories] = useState<ActivityCategory[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const loadCategories = useCallback(async () => {
    setIsLoadingCategories(true);
    setErrorMessage('');

    try {
      const loadedCategories = await listActivityCategories();
      setCategories(loadedCategories);
      setForm((currentForm) => ({
        ...currentForm,
        id_categoria:
          currentForm.id_categoria ||
          initialActivity?.categoryId ||
          String(loadedCategories[0]?.id_categoria ?? ''),
      }));
    } catch (error) {
      if (isMobileSessionExpiredError(error)) {
        onSessionExpired();
        return;
      }

      setCategories([]);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible cargar las categorias.',
      );
    } finally {
      setIsLoadingCategories(false);
    }
  }, [initialActivity?.categoryId, onSessionExpired]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  function updateField(field: TextFieldName, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit() {
    const localValidationError = validateForm(form);
    if (localValidationError) {
      setErrorMessage(localValidationError);
      return;
    }

    setIsSaving(true);
    setErrorMessage('');

    try {
      await registerMobileSessionActivity();
      await onCreate({
        ...form,
        id_usuario:
          initialActivity?.userId ||
          (authSession?.usuario.id_usuario ? String(authSession.usuario.id_usuario) : ''),
        realizada,
      });
    } catch (error) {
      if (isMobileSessionExpiredError(error)) {
        onSessionExpired();
        return;
      }

      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'No fue posible guardar la actividad.',
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <View style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>{isEditing ? 'Edicion' : 'Nueva actividad'}</Text>
        <Text style={styles.title}>
          {isEditing ? 'Editar actividad de abril' : 'Crear actividad de abril'}
        </Text>
        <Text style={styles.subtitle}>
          {isEditing
            ? 'Ajusta los datos necesarios. El backend validara permisos, fecha y horario.'
            : 'Completa los datos basicos. El backend validara permisos, fecha y horario.'}
        </Text>

        <View style={styles.formCard}>
          <FieldLabel label="Titulo" />
          <TextInput
            autoCapitalize="sentences"
            onChangeText={(value) => updateField('titulo', value)}
            placeholder="Ej: Reunion de seguimiento"
            style={styles.input}
            value={form.titulo}
          />

          <FieldLabel label="Descripcion" />
          <TextInput
            multiline
            onChangeText={(value) => updateField('descripcion', value)}
            placeholder="Detalle breve de la actividad"
            style={[styles.input, styles.textArea]}
            textAlignVertical="top"
            value={form.descripcion}
          />

          <View style={styles.twoColumns}>
            <View style={styles.column}>
              <FieldLabel label="Fecha" />
              <TextInput
                keyboardType="numbers-and-punctuation"
                onChangeText={(value) => updateField('fecha_actividad', value)}
                placeholder="2026-04-20"
                style={styles.input}
                value={form.fecha_actividad}
              />
            </View>
            <View style={styles.column}>
              <FieldLabel label="Emoji" />
              <TextInput
                maxLength={8}
                onChangeText={(value) => updateField('emoji', value)}
                placeholder="📌"
                style={styles.input}
                value={form.emoji}
              />
            </View>
          </View>

          <ScrollView
            contentContainerStyle={styles.emojiList}
            horizontal
            showsHorizontalScrollIndicator={false}
          >
            {emojiSuggestions.map((emoji) => (
              <Pressable
                accessibilityRole="button"
                key={emoji}
                onPress={() => updateField('emoji', emoji)}
                style={[
                  styles.emojiChip,
                  form.emoji === emoji && styles.emojiChipSelected,
                ]}
              >
                <Text style={styles.emojiChipText}>{emoji}</Text>
              </Pressable>
            ))}
          </ScrollView>

          <View style={styles.twoColumns}>
            <View style={styles.column}>
              <FieldLabel label="Inicio" />
              <TextInput
                keyboardType="numbers-and-punctuation"
                onChangeText={(value) => updateField('hora_inicio', value)}
                placeholder="09:00"
                style={styles.input}
                value={form.hora_inicio}
              />
            </View>
            <View style={styles.column}>
              <FieldLabel label="Fin" />
              <TextInput
                keyboardType="numbers-and-punctuation"
                onChangeText={(value) => updateField('hora_fin', value)}
                placeholder="10:00"
                style={styles.input}
                value={form.hora_fin}
              />
            </View>
          </View>

          <FieldLabel label="Lugar" />
          <TextInput
            autoCapitalize="sentences"
            onChangeText={(value) => updateField('lugar', value)}
            placeholder="Ej: Sala 1"
            style={styles.input}
            value={form.lugar}
          />

          <FieldLabel label="Categoria" />
          {isLoadingCategories ? (
            <Text style={styles.helperText}>Cargando categorias...</Text>
          ) : categories.length === 0 ? (
            <View style={styles.emptyCategories}>
              <Text style={styles.helperText}>No hay categorias disponibles.</Text>
              <PrimaryButton onPress={loadCategories} variant="secondary">
                Reintentar
              </PrimaryButton>
            </View>
          ) : (
            <ScrollView
              contentContainerStyle={styles.categoryList}
              horizontal
              showsHorizontalScrollIndicator={false}
            >
              {categories.map((category) => {
                const value = String(category.id_categoria);
                const isSelected = form.id_categoria === value;

                return (
                  <Pressable
                    accessibilityRole="button"
                    key={category.id_categoria}
                    onPress={() => updateField('id_categoria', value)}
                    style={[
                      styles.categoryChip,
                      isSelected && styles.categoryChipSelected,
                    ]}
                  >
                    <Text
                      style={[
                        styles.categoryChipText,
                        isSelected && styles.categoryChipTextSelected,
                      ]}
                    >
                      {category.nombre_categoria}
                    </Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          )}

          <View style={styles.switchRow}>
            <View style={styles.switchCopy}>
              <Text style={styles.switchTitle}>Marcar como realizada</Text>
              <Text style={styles.switchText}>Opcional para esta version inicial.</Text>
            </View>
            <Switch
              onValueChange={setRealizada}
              thumbColor="#ffffff"
              trackColor={{ false: colors.border, true: colors.success }}
              value={realizada}
            />
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        <PrimaryButton
          disabled={isSaving || isLoadingCategories || categories.length === 0}
          onPress={handleSubmit}
        >
          {isSaving ? 'Guardando...' : 'Guardar actividad'}
        </PrimaryButton>
        <PrimaryButton disabled={isSaving} onPress={onCancel} variant="secondary">
          {isEditing ? 'Volver al detalle' : 'Volver a la lista'}
        </PrimaryButton>
      </View>
    </View>
  );
}

function FieldLabel({ label }: { label: string }) {
  return <Text style={styles.label}>{label}</Text>;
}

function buildInitialForm(activity?: Activity): FormState {
  if (!activity) {
    return initialForm;
  }

  return {
    titulo: activity.title,
    descripcion: activity.description || '',
    fecha_actividad: activity.date,
    hora_inicio: activity.startTime,
    hora_fin: activity.endTime,
    id_categoria: activity.categoryId,
    emoji: activity.emoji || '',
    lugar: activity.placeValue,
  };
}

function validateForm(form: FormState) {
  if (!form.titulo.trim()) {
    return 'El titulo es obligatorio.';
  }

  if (!isAprilDate(form.fecha_actividad)) {
    return 'La fecha debe estar entre el 1 y el 30 de abril.';
  }

  if (!isTime(form.hora_inicio) || !isTime(form.hora_fin)) {
    return 'Ingresa los horarios con formato HH:MM.';
  }

  if (form.hora_inicio >= form.hora_fin) {
    return 'La hora de fin debe ser posterior a la de inicio.';
  }

  if (!form.id_categoria) {
    return 'Debes seleccionar una categoria.';
  }

  return '';
}

function isAprilDate(rawDate: string) {
  const [year, month, day] = rawDate.split('-').map(Number);
  return Boolean(year && month === 4 && day >= 1 && day <= 30);
}

function isTime(rawTime: string) {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(rawTime);
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
  subtitle: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 22,
    marginTop: spacing.xs,
  },
  formCard: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    marginTop: spacing.md,
    padding: spacing.md,
  },
  label: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '800',
    marginBottom: spacing.xs,
    marginTop: spacing.sm,
    textTransform: 'uppercase',
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
    paddingVertical: spacing.sm,
  },
  textArea: {
    minHeight: 92,
  },
  twoColumns: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  column: {
    flex: 1,
  },
  categoryList: {
    gap: spacing.sm,
    paddingVertical: 2,
  },
  emojiList: {
    gap: spacing.sm,
    paddingTop: spacing.sm,
  },
  emojiChip: {
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    height: 40,
    justifyContent: 'center',
    width: 40,
  },
  emojiChipSelected: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.accent,
  },
  emojiChipText: {
    fontSize: 19,
  },
  categoryChip: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  categoryChipSelected: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.accent,
  },
  categoryChipText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '700',
  },
  categoryChipTextSelected: {
    color: colors.accentStrong,
  },
  emptyCategories: {
    gap: spacing.sm,
  },
  helperText: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
  switchRow: {
    alignItems: 'center',
    borderColor: colors.border,
    borderTopWidth: 1,
    flexDirection: 'row',
    gap: spacing.md,
    justifyContent: 'space-between',
    marginTop: spacing.md,
    paddingTop: spacing.md,
  },
  switchCopy: {
    flex: 1,
  },
  switchTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: '800',
  },
  switchText: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
    marginTop: 2,
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
