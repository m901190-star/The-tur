import { Ionicons } from '@expo/vector-icons';
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { AppButton } from '../components/AppButton';
import { Chip } from '../components/Chip';
import { SectionHeader } from '../components/SectionHeader';
import {
  CalendarOption,
  hasCalendarAccess,
  listWritableCalendars,
  requestCalendarAccess,
  shareIcsFile,
  suggestCalendar,
  syncAllPlants,
} from '../lib/calendar';
import { usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';

const REMINDER_HOURS = [6, 7, 8, 9, 17, 18, 19, 20];

export function SettingsScreen() {
  const insets = useSafeAreaInsets();
  const { plants, log, settings, updateSettings, updatePlant, resetEverything } = usePlants();

  const [calendars, setCalendars] = useState<CalendarOption[]>([]);
  const [granted, setGranted] = useState<boolean | null>(null);
  const [busy, setBusy] = useState<'none' | 'sync' | 'export' | 'load'>('none');

  const loadCalendars = useCallback(async () => {
    const options = await listWritableCalendars();
    setCalendars(options);
    return options;
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const allowed = await hasCalendarAccess();
      if (cancelled) return;
      setGranted(allowed);
      if (allowed) await loadCalendars();
    })();
    return () => {
      cancelled = true;
    };
  }, [loadCalendars]);

  const connect = useCallback(async () => {
    setBusy('load');
    try {
      const allowed = await requestCalendarAccess();
      setGranted(allowed);
      if (!allowed) {
        Alert.alert(
          'אין הרשאה ליומן',
          'אפשר לאשר גישה ליומן בהגדרות המכשיר, ואז לחזור לכאן.',
        );
        return;
      }
      await loadCalendars();
      if (!settings.calendarId) {
        const suggested = await suggestCalendar();
        if (suggested) {
          await updateSettings({
            calendarId: suggested.id,
            calendarTitle: suggested.title,
          });
        }
      }
    } finally {
      setBusy('none');
    }
  }, [loadCalendars, settings.calendarId, updateSettings]);

  const chooseCalendar = useCallback(
    async (option: CalendarOption) => {
      await updateSettings({ calendarId: option.id, calendarTitle: option.title });
    },
    [updateSettings],
  );

  const syncNow = useCallback(async () => {
    if (!settings.calendarId) {
      Alert.alert('בחר יומן', 'קודם כל בחר לאיזה יומן לכתוב את התזכורות.');
      return;
    }
    setBusy('sync');
    try {
      const result = await syncAllPlants(plants, settings);
      for (const [plantId, eventId] of Object.entries(result.eventIds)) {
        await updatePlant(plantId, { calendarEventId: eventId });
      }
      Alert.alert(
        'סונכרן',
        result.failed === 0
          ? `${result.synced} תזכורות חוזרות נכתבו ל״${settings.calendarTitle}״.`
          : `${result.synced} הצליחו, ${result.failed} נכשלו. נסה שוב בעוד רגע.`,
      );
    } finally {
      setBusy('none');
    }
  }, [plants, settings, updatePlant]);

  const exportIcs = useCallback(async () => {
    if (plants.length === 0) {
      Alert.alert('אין מה לייצא', 'הוסף עציץ אחד לפחות.');
      return;
    }
    setBusy('export');
    try {
      await shareIcsFile(plants, settings);
    } catch {
      Alert.alert('הייצוא נכשל', 'נסה שוב, או השתמש בסנכרון הישיר ליומן.');
    } finally {
      setBusy('none');
    }
  }, [plants, settings]);

  const confirmReset = useCallback(() => {
    Alert.alert(
      'למחוק את כל הנתונים?',
      'כל העציצים וההיסטוריה יימחקו מהמכשיר. אירועים שכבר נכתבו ליומן יישארו שם.',
      [
        { text: 'ביטול', style: 'cancel' },
        { text: 'מחיקה', style: 'destructive', onPress: () => resetEverything() },
      ],
    );
  }, [resetEverything]);

  return (
    <ScrollView
      contentContainerStyle={[
        styles.content,
        { paddingTop: insets.top + spacing.lg, paddingBottom: insets.bottom + spacing.xxl },
      ]}
    >
      <Text style={styles.headline}>הגדרות</Text>

      <SectionHeader
        title="תזכורות ביומן"
        caption="האפליקציה כותבת לכל עציץ אירוע חוזר ביומן שתבחר. חשבון Google שמחובר למכשיר מופיע כאן, וכך התזכורת מגיעה ליומן Google שלך."
      />

      {granted === false || calendars.length === 0 ? (
        <AppButton
          label="חיבור ליומן"
          onPress={connect}
          busy={busy === 'load'}
        />
      ) : (
        <View style={styles.calendarList}>
          {calendars.map((option) => {
            const selected = settings.calendarId === option.id;
            return (
              <Pressable
                key={option.id}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                onPress={() => chooseCalendar(option)}
                style={({ pressed }) => [
                  styles.calendarRow,
                  selected && styles.calendarRowSelected,
                  pressed && styles.pressed,
                ]}
              >
                <Ionicons
                  name={selected ? 'radio-button-on' : 'radio-button-off'}
                  size={20}
                  color={selected ? colors.primary : colors.textMuted}
                />
                <View style={styles.calendarText}>
                  <Text style={styles.calendarTitle}>{option.title}</Text>
                  <Text style={styles.calendarSource}>
                    {option.source || 'יומן מקומי'}
                    {option.isGoogle ? ' · Google' : ''}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>
      )}

      <SectionHeader title="שעת התזכורת" caption="באיזו שעה ביום האירוע ייפתח ביומן." />
      <View style={styles.hours}>
        {REMINDER_HOURS.map((hour) => (
          <Chip
            key={hour}
            label={`${String(hour).padStart(2, '0')}:00`}
            selected={settings.reminderHour === hour}
            onPress={() => updateSettings({ reminderHour: hour })}
          />
        ))}
      </View>

      <SectionHeader title="סנכרון" />
      <AppButton
        label="סנכרון כל העציצים ליומן"
        onPress={syncNow}
        busy={busy === 'sync'}
        disabled={plants.length === 0}
      />
      <AppButton
        label="ייצוא קובץ ‎.ics‎ לשיתוף"
        variant="ghost"
        onPress={exportIcs}
        busy={busy === 'export'}
      />
      <Text style={styles.hint}>
        קובץ ‎.ics‎ אפשר לייבא ל-Google Calendar בדפדפן, או לשלוח למי שמשקה
        במקומך כשאתה בחופשה.
      </Text>

      <SectionHeader title="הנתונים שלי" />
      <View style={styles.statsRow}>
        <Text style={styles.statsText}>{plants.length} עציצים</Text>
        <Text style={styles.statsText}>{log.length} רשומות בהיסטוריה</Text>
      </View>
      <Text style={styles.hint}>
        הנתונים נשמרים במכשיר בלבד, ולא נשלחים לשום מקום.
      </Text>
      <AppButton label="מחיקת כל הנתונים" variant="danger" onPress={confirmReset} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { paddingHorizontal: spacing.lg, gap: spacing.sm },
  headline: { ...typography.title, color: colors.text, ...rtlText },
  calendarList: { gap: spacing.sm },
  calendarRow: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.md,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  calendarRowSelected: { borderColor: colors.primary, backgroundColor: colors.primarySoft },
  pressed: { opacity: 0.8 },
  calendarText: { flex: 1, alignItems: 'flex-end' },
  calendarTitle: { ...typography.bodyStrong, color: colors.text, ...rtlText },
  calendarSource: { ...typography.small, color: colors.textMuted, ...rtlText },
  hours: { flexDirection: 'row-reverse', flexWrap: 'wrap', gap: spacing.sm },
  hint: { ...typography.small, color: colors.textMuted, ...rtlText },
  statsRow: { flexDirection: 'row-reverse', gap: spacing.lg },
  statsText: { ...typography.body, color: colors.text },
});
