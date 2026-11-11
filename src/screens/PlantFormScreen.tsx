import { Ionicons } from '@expo/vector-icons';
import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import React, { useCallback, useMemo, useState } from 'react';
import {
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { AppButton } from '../components/AppButton';
import { Chip } from '../components/Chip';
import { Field, FieldGroup } from '../components/Field';
import { upsertPlantEvent } from '../lib/calendar';
import {
  addDays,
  suggestWaterForContainer,
  suggestWaterMl,
} from '../lib/watering';
import { RootStackParamList } from '../navigation';
import { PLANT_PRESETS, PlantPreset, searchPresets } from '../plantPresets';
import { NewPlant, usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';
import {
  LIGHT_LABELS,
  LightLevel,
  POT_DEFAULT_LITERS,
  POT_LABELS,
  Plant,
  PotSize,
} from '../types';

interface FormState {
  name: string;
  species: string;
  location: string;
  /** Substrate volume in litres, as typed. Empty falls back to the pot size. */
  containerLiters: string;
  /** How many plants share the container, as typed. */
  plantCount: string;
  isOutdoor: boolean;
  waterMl: string;
  intervalSummerDays: string;
  intervalWinterDays: string;
  light: LightLevel;
  potSize: PotSize;
  fertilizeEveryDays: string;
  notes: string;
  photoUri: string | null;
  /** Days ago it was last watered; null means "never watered". */
  lastWateredDaysAgo: number | null;
}

const LIGHT_OPTIONS: LightLevel[] = ['full-sun', 'partial', 'shade'];
const POT_OPTIONS: PotSize[] = ['small', 'medium', 'large'];

const LAST_WATERED_OPTIONS: { label: string; value: number | null }[] = [
  { label: 'היום', value: 0 },
  { label: 'אתמול', value: 1 },
  { label: 'לפני 3 ימים', value: 3 },
  { label: 'לפני שבוע', value: 7 },
  { label: 'טרם הושקה', value: null },
];

function emptyForm(): FormState {
  return {
    name: '',
    species: '',
    location: '',
    containerLiters: '',
    plantCount: '1',
    isOutdoor: false,
    waterMl: String(suggestWaterMl('medium')),
    intervalSummerDays: '7',
    intervalWinterDays: '12',
    light: 'partial',
    potSize: 'medium',
    fertilizeEveryDays: '30',
    notes: '',
    photoUri: null,
    lastWateredDaysAgo: 0,
  };
}

function formFromPlant(plant: Plant): FormState {
  let lastWateredDaysAgo: number | null = null;
  if (plant.lastWateredAt) {
    const then = new Date(plant.lastWateredAt);
    const days = Math.round((Date.now() - then.getTime()) / (24 * 60 * 60 * 1000));
    lastWateredDaysAgo = Math.max(0, days);
  }
  return {
    name: plant.name,
    species: plant.species,
    location: plant.location,
    containerLiters: plant.containerLiters ? String(plant.containerLiters) : '',
    plantCount: String(plant.plantCount || 1),
    isOutdoor: plant.isOutdoor,
    waterMl: String(plant.waterMl),
    intervalSummerDays: String(plant.intervalSummerDays),
    intervalWinterDays: String(plant.intervalWinterDays),
    light: plant.light,
    potSize: plant.potSize,
    fertilizeEveryDays: plant.fertilizeEveryDays ? String(plant.fertilizeEveryDays) : '',
    notes: plant.notes,
    photoUri: plant.photoUri,
    lastWateredDaysAgo,
  };
}

function toPositiveInt(value: string, fallback: number): number {
  const parsed = Number.parseInt(value.replace(/[^\d]/g, ''), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback;
  return parsed;
}

export function PlantFormScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'PlantForm'>>();
  const insets = useSafeAreaInsets();
  const { getPlant, addPlant, updatePlant, settings } = usePlants();

  const editingId = route.params?.plantId;
  const existing = editingId ? getPlant(editingId) : undefined;

  const [form, setForm] = useState<FormState>(() =>
    existing ? formFromPlant(existing) : emptyForm(),
  );
  const [presetQuery, setPresetQuery] = useState('');
  const [showAllPresets, setShowAllPresets] = useState(false);
  const [saving, setSaving] = useState(false);

  const patch = useCallback(
    (changes: Partial<FormState>) => setForm((current) => ({ ...current, ...changes })),
    [],
  );

  const activePreset = useMemo(
    () => PLANT_PRESETS.find((preset) => preset.species === form.species.trim()),
    [form.species],
  );

  const presetResults = useMemo(() => {
    const results = searchPresets(presetQuery);
    return showAllPresets || presetQuery.trim() ? results : results.slice(0, 8);
  }, [presetQuery, showAllPresets]);

  const applyPreset = useCallback((preset: PlantPreset) => {
    setForm((current) => {
      const liters = Number.parseInt(current.containerLiters.replace(/[^\d]/g, ''), 10);
      // If the user already said how big the planter is, the preset's ratio
      // beats its generic "typical pot" amount.
      const waterMl =
        Number.isFinite(liters) && liters > 0
          ? suggestWaterForContainer(liters, preset.mlPerLiterOfSoil)
          : preset.waterMl;
      return {
      ...current,
      species: preset.species,
      // Keep whatever the user already typed as the plant's own name.
      name: current.name,
      isOutdoor: preset.outdoor,
      waterMl: String(waterMl),
      intervalSummerDays: String(preset.intervalSummerDays),
      intervalWinterDays: String(preset.intervalWinterDays),
      light: preset.light,
      potSize: preset.potSize,
      fertilizeEveryDays: preset.fertilizeEveryDays ? String(preset.fertilizeEveryDays) : '',
      };
    });
  }, []);

  const pickPhoto = useCallback(async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('אין הרשאה', 'כדי לצרף תמונה יש לאשר גישה לגלריה בהגדרות המכשיר.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.6,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!result.canceled && result.assets[0]) {
      patch({ photoUri: result.assets[0].uri });
    }
  }, [patch]);

  const save = useCallback(async () => {
    const species = form.species.trim();
    const name = form.name.trim() || species;
    if (!name) {
      Alert.alert('חסר שם', 'תן לעציץ שם או בחר סוג, כדי שתזהה אותו ברשימה.');
      return;
    }

    setSaving(true);
    try {
      const lastWateredAt =
        form.lastWateredDaysAgo === null
          ? null
          : addDays(new Date(), -form.lastWateredDaysAgo).toISOString();

      const fertilizeEveryDays = form.fertilizeEveryDays.trim()
        ? toPositiveInt(form.fertilizeEveryDays, 30)
        : null;

      const containerLiters = form.containerLiters.trim()
        ? toPositiveInt(form.containerLiters, POT_DEFAULT_LITERS[form.potSize])
        : null;

      const draft: NewPlant = {
        name,
        species,
        location: form.location.trim(),
        containerLiters,
        plantCount: toPositiveInt(form.plantCount, 1),
        isOutdoor: form.isOutdoor,
        waterMl: toPositiveInt(form.waterMl, suggestWaterMl(form.potSize)),
        intervalSummerDays: toPositiveInt(form.intervalSummerDays, 7),
        intervalWinterDays: toPositiveInt(form.intervalWinterDays, 12),
        light: form.light,
        potSize: form.potSize,
        fertilizeEveryDays,
        lastWateredAt,
        lastFertilizedAt: existing?.lastFertilizedAt ?? null,
        photoUri: form.photoUri,
        notes: form.notes.trim(),
      };

      const saved: Plant = existing
        ? { ...existing, ...draft }
        : await addPlant(draft);

      if (existing) {
        await updatePlant(existing.id, draft);
      }

      // Keep the calendar in step, but never block the save on it.
      if (settings.calendarId) {
        try {
          const eventId = await upsertPlantEvent(saved, settings);
          await updatePlant(saved.id, { calendarEventId: eventId });
        } catch {
          Alert.alert(
            'נשמר, אבל לא עודכן ביומן',
            'אפשר לנסות לסנכרן מחדש ממסך ההגדרות.',
          );
        }
      }

      navigation.goBack();
    } finally {
      setSaving(false);
    }
  }, [form, existing, addPlant, updatePlant, settings, navigation]);

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingBottom: insets.bottom + spacing.xxl },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Pressable onPress={pickPhoto} style={styles.photoPicker}>
          {form.photoUri ? (
            <Image source={{ uri: form.photoUri }} style={styles.photo} />
          ) : (
            <View style={[styles.photo, styles.photoEmpty]}>
              <Ionicons name="camera-outline" size={26} color={colors.primary} />
              <Text style={styles.photoHint}>הוספת תמונה</Text>
            </View>
          )}
        </Pressable>

        <Field
          label="איך תקרא לו"
          value={form.name}
          onChangeText={(value) => patch({ name: value })}
          placeholder="הפיקוס של הסלון"
        />

        <View style={styles.block}>
          <Text style={styles.blockLabel}>סוג הצמח</Text>
          <Field
            label=""
            value={form.species}
            onChangeText={(value) => {
              patch({ species: value });
              setPresetQuery(value);
            }}
            placeholder="חפש או כתוב סוג חופשי"
          />
          <View style={styles.presetWrap}>
            {presetResults.map((preset) => (
              <Chip
                key={preset.species}
                label={preset.species}
                selected={activePreset?.species === preset.species}
                onPress={() => {
                  applyPreset(preset);
                  setPresetQuery('');
                }}
              />
            ))}
          </View>
          {!presetQuery.trim() && !showAllPresets ? (
            <Pressable onPress={() => setShowAllPresets(true)}>
              <Text style={styles.link}>הצג את כל הסוגים</Text>
            </Pressable>
          ) : null}
          {activePreset ? (
            <View style={styles.tip}>
              <Ionicons name="bulb-outline" size={16} color={colors.primaryDark} />
              <Text style={styles.tipText}>{activePreset.tip}</Text>
            </View>
          ) : null}
        </View>

        <Field
          label="מקום בבית"
          value={form.location}
          onChangeText={(value) => patch({ location: value })}
          placeholder="סלון / מרפסת / חדר שינה"
          hint="משפיע על צריכת המים, וגם מאפשר לסנן לפי חדר."
        />

        <FieldGroup
          label="איפה הוא עומד"
          hint="רק לעציצים בחוץ מזג האוויר משנה — גשם לא מגיע לסלון."
        >
          <Chip
            label="בבית"
            selected={!form.isOutdoor}
            onPress={() => patch({ isOutdoor: false })}
          />
          <Chip
            label="בחוץ / מרפסת"
            selected={form.isOutdoor}
            onPress={() => patch({ isOutdoor: true })}
          />
        </FieldGroup>

        <View style={styles.pairRow}>
          <View style={styles.pairItem}>
            <Field
              label="נפח האדנית"
              value={form.containerLiters}
              onChangeText={(value) => {
                const liters = Number.parseInt(value.replace(/[^\d]/g, ''), 10);
                const ratio = activePreset?.mlPerLiterOfSoil;
                patch({
                  containerLiters: value,
                  ...(Number.isFinite(liters) && liters > 0
                    ? { waterMl: String(suggestWaterForContainer(liters, ratio)) }
                    : {}),
                });
              }}
              keyboardType="number-pad"
              suffix="ליטר"
              placeholder="70"
            />
          </View>
          <View style={styles.pairItem}>
            <Field
              label="כמה צמחים בה"
              value={form.plantCount}
              onChangeText={(value) => patch({ plantCount: value })}
              keyboardType="number-pad"
              placeholder="1"
            />
          </View>
        </View>
        <Text style={styles.blockHint}>
          אדנית אחת עם שלושה צמחים מתייבשת מהר יותר מאדנית עם אחד, אז המספר
          מקצר את התדירות. כמות המים נשארת של האדנית — אתה משקה אותה, לא כל
          צמח בנפרד.
        </Text>

        {!form.containerLiters.trim() ? (
          <FieldGroup label="גודל העציץ" hint="אם לא מילאת נפח מדויק למעלה.">
            {POT_OPTIONS.map((option) => (
              <Chip
                key={option}
                label={POT_LABELS[option]}
                selected={form.potSize === option}
                onPress={() =>
                  patch({ potSize: option, waterMl: String(suggestWaterMl(option)) })
                }
              />
            ))}
          </FieldGroup>
        ) : null}

        <Field
          label="כמות מים להשקיה"
          value={form.waterMl}
          onChangeText={(value) => patch({ waterMl: value })}
          keyboardType="number-pad"
          suffix="מ״ל"
          hint={
            form.containerLiters.trim()
              ? 'מחושב כ-15% מנפח האדנית — השקיה שמרטיבה את כל גוש השורשים בלי שהכול ייצא מהניקוז.'
              : 'כוס רגילה היא בערך 250 מ״ל.'
          }
        />

        <FieldGroup label="כמה אור הוא מקבל">
          {LIGHT_OPTIONS.map((option) => (
            <Chip
              key={option}
              label={LIGHT_LABELS[option]}
              selected={form.light === option}
              onPress={() => patch({ light: option })}
            />
          ))}
        </FieldGroup>

        <View style={styles.block}>
          <Text style={styles.blockLabel}>תדירות השקיה</Text>
          <Text style={styles.blockHint}>
            בחורף הצמחים שותים פחות, לכן יש שתי תדירויות. האפליקציה בוחרת לבד לפי
            החודש.
          </Text>
          <View style={styles.pairRow}>
            <View style={styles.pairItem}>
              <Field
                label="קיץ (אפריל–אוקטובר)"
                value={form.intervalSummerDays}
                onChangeText={(value) => patch({ intervalSummerDays: value })}
                keyboardType="number-pad"
                suffix="ימים"
              />
            </View>
            <View style={styles.pairItem}>
              <Field
                label="חורף (נובמבר–מרץ)"
                value={form.intervalWinterDays}
                onChangeText={(value) => patch({ intervalWinterDays: value })}
                keyboardType="number-pad"
                suffix="ימים"
              />
            </View>
          </View>
        </View>

        <FieldGroup label="מתי הושקה בפעם האחרונה" hint="מכאן מחושבת התזכורת הבאה.">
          {LAST_WATERED_OPTIONS.map((option) => (
            <Chip
              key={option.label}
              label={option.label}
              selected={form.lastWateredDaysAgo === option.value}
              onPress={() => patch({ lastWateredDaysAgo: option.value })}
            />
          ))}
        </FieldGroup>

        <Field
          label="דישון כל"
          value={form.fertilizeEveryDays}
          onChangeText={(value) => patch({ fertilizeEveryDays: value })}
          keyboardType="number-pad"
          suffix="ימים"
          hint="השאר ריק אם אתה לא מדשן את העציץ הזה."
        />

        <Field
          label="הערות"
          value={form.notes}
          onChangeText={(value) => patch({ notes: value })}
          placeholder="רגיש להשקיה יתרה, עלים מתחילים להצהיב..."
          multiline
          style={styles.notes}
        />

        <AppButton
          label={existing ? 'שמירת שינויים' : 'הוספת העציץ'}
          onPress={save}
          busy={saving}
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { padding: spacing.lg, gap: spacing.lg },
  photoPicker: { alignSelf: 'center' },
  photo: { width: 110, height: 110, borderRadius: radius.lg },
  photoEmpty: {
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
    borderStyle: 'dashed',
  },
  photoHint: { ...typography.small, color: colors.primaryDark },
  block: { gap: spacing.sm },
  blockLabel: { ...typography.bodyStrong, color: colors.text, ...rtlText },
  blockHint: { ...typography.small, color: colors.textMuted, ...rtlText },
  presetWrap: { flexDirection: 'row-reverse', flexWrap: 'wrap', gap: spacing.sm },
  link: { ...typography.small, color: colors.water, ...rtlText },
  tip: {
    flexDirection: 'row-reverse',
    gap: spacing.sm,
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  tipText: { ...typography.small, color: colors.primaryDark, flex: 1, ...rtlText },
  pairRow: { flexDirection: 'row-reverse', gap: spacing.md },
  pairItem: { flex: 1 },
  notes: { minHeight: 90, paddingTop: spacing.md, textAlignVertical: 'top' },
});
