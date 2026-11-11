import { Ionicons } from '@expo/vector-icons';
import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useMemo, useState } from 'react';
import { Alert, Image, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { AppButton } from '../components/AppButton';
import { SectionHeader } from '../components/SectionHeader';
import { StatusPill } from '../components/StatusPill';
import { deletePlantEvent, upsertPlantEvent } from '../lib/calendar';
import {
  fertilizeState,
  formatRelativeDay,
  formatWater,
  intervalDays,
  seasonForDate,
  wateringState,
} from '../lib/watering';
import { RootStackParamList } from '../navigation';
import { usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';
import { LIGHT_LABELS, LogEntry, POT_LABELS } from '../types';

const HE_DATE_TIME = new Intl.DateTimeFormat('he-IL', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
});

const LOG_LABELS: Record<LogEntry['kind'], string> = {
  water: 'השקיה',
  fertilize: 'דישון',
  skip: 'נדחה',
};

const LOG_ICONS: Record<LogEntry['kind'], keyof typeof Ionicons.glyphMap> = {
  water: 'water-outline',
  fertilize: 'nutrition-outline',
  skip: 'time-outline',
};

export function PlantDetailScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'PlantDetail'>>();
  const insets = useSafeAreaInsets();
  const {
    getPlant,
    removePlant,
    markWatered,
    markFertilized,
    snooze,
    logFor,
    settings,
    updatePlant,
    weather,
  } = usePlants();

  const plant = getPlant(route.params.plantId);
  const [syncing, setSyncing] = useState(false);
  const now = useMemo(() => new Date(), []);

  const syncCalendar = useCallback(async () => {
    if (!plant) return;
    if (!settings.calendarId) {
      Alert.alert('לא נבחר יומן', 'בחר יומן במסך ההגדרות, ואז נוכל לכתוב אליו תזכורות.');
      return;
    }
    setSyncing(true);
    try {
      const eventId = await upsertPlantEvent(plant, settings);
      await updatePlant(plant.id, { calendarEventId: eventId });
      Alert.alert('עודכן ביומן', `התזכורת נכתבה ל״${settings.calendarTitle ?? 'היומן'}״.`);
    } catch {
      Alert.alert('הסנכרון נכשל', 'בדוק את הרשאות היומן ונסה שוב.');
    } finally {
      setSyncing(false);
    }
  }, [plant, settings, updatePlant]);

  const confirmDelete = useCallback(() => {
    if (!plant) return;
    Alert.alert(
      'למחוק את העציץ?',
      `${plant.name} יימחק יחד עם היסטוריית ההשקיות שלו. אין ביטול.`,
      [
        { text: 'ביטול', style: 'cancel' },
        {
          text: 'מחיקה',
          style: 'destructive',
          onPress: async () => {
            await deletePlantEvent(plant);
            await removePlant(plant.id);
            navigation.goBack();
          },
        },
      ],
    );
  }, [plant, removePlant, navigation]);

  if (!plant) {
    return (
      <View style={styles.missing}>
        <Text style={styles.missingText}>העציץ נמחק.</Text>
      </View>
    );
  }

  const water = wateringState(plant, now, weather);
  const fertilize = fertilizeState(plant, now);
  const history = logFor(plant.id);
  const season = seasonForDate(now) === 'summer' ? 'קיץ' : 'חורף';

  return (
    <ScrollView
      contentContainerStyle={[
        styles.content,
        { paddingBottom: insets.bottom + spacing.xxl },
      ]}
    >
      {plant.photoUri ? (
        <Image source={{ uri: plant.photoUri }} style={styles.photo} />
      ) : null}

      <View style={styles.headerBlock}>
        <Text style={styles.name}>{plant.name}</Text>
        {plant.species ? <Text style={styles.species}>{plant.species}</Text> : null}
        <StatusPill state={water} />
      </View>

      {water.weatherReason ? (
        <View style={styles.weatherNote}>
          <Ionicons name="rainy-outline" size={16} color={colors.water} />
          <Text style={styles.weatherNoteText}>{water.weatherReason}</Text>
        </View>
      ) : null}

      <View style={styles.actions}>
        <AppButton
          label="השקיתי עכשיו"
          variant="water"
          onPress={() => markWatered(plant.id)}
          style={styles.grow}
        />
        <AppButton label="דחה ביום" variant="ghost" onPress={() => snooze(plant.id, 1)} />
      </View>

      <View style={styles.grid}>
        <Stat label="כמות מים" value={formatWater(plant.waterMl)} icon="water-outline" />
        <Stat
          label={`תדירות (${season})`}
          value={`כל ${intervalDays(plant, now, weather)} ימים`}
          icon="repeat-outline"
        />
        <Stat
          label={water.status === 'overdue' ? 'היה אמור להיות מושקה' : 'השקיה הבאה'}
          value={water.nextDate ? formatRelativeDay(water.nextDate, now) : 'טרם נקבעה'}
          icon="calendar-outline"
        />
        <Stat
          label="הושקה לאחרונה"
          value={
            plant.lastWateredAt
              ? formatRelativeDay(new Date(plant.lastWateredAt), now)
              : 'אף פעם'
          }
          icon="time-outline"
        />
        <Stat label="מקום" value={plant.location || '—'} icon="home-outline" />
        <Stat label="אור" value={LIGHT_LABELS[plant.light]} icon="sunny-outline" />
        <Stat
          label="נפח האדנית"
          value={
            plant.containerLiters
              ? `${plant.containerLiters} ליטר`
              : POT_LABELS[plant.potSize]
          }
          icon="cube-outline"
        />
        <Stat
          label="צמחים באדנית"
          value={
            plant.plantCount > 1 ? `${plant.plantCount} · מתייבשת מהר יותר` : 'אחד'
          }
          icon="leaf-outline"
        />
        <Stat
          label="מיקום"
          value={plant.isOutdoor ? 'בחוץ · מושפע ממזג האוויר' : 'בבית'}
          icon={plant.isOutdoor ? 'partly-sunny-outline' : 'bed-outline'}
        />
        <Stat
          label="דישון"
          value={
            !fertilize.tracked
              ? 'לא במעקב'
              : fertilize.due
                ? 'מחכה לדישון'
                : fertilize.nextDate
                  ? formatRelativeDay(fertilize.nextDate, now)
                  : '—'
          }
          icon="nutrition-outline"
        />
      </View>

      {fertilize.tracked && fertilize.due ? (
        <AppButton label="דישנתי" onPress={() => markFertilized(plant.id)} />
      ) : null}

      {plant.notes ? (
        <>
          <SectionHeader title="הערות" />
          <Text style={styles.notes}>{plant.notes}</Text>
        </>
      ) : null}

      <SectionHeader
        title="יומן Google"
        caption={
          plant.calendarEventId
            ? `מסונכרן ל״${settings.calendarTitle ?? 'היומן שנבחר'}״`
            : 'עדיין לא נכתבה תזכורת חוזרת ליומן'
        }
      />
      <AppButton
        label={plant.calendarEventId ? 'עדכון התזכורת ביומן' : 'הוספת תזכורת ליומן'}
        variant="ghost"
        busy={syncing}
        onPress={syncCalendar}
      />

      <SectionHeader
        title="היסטוריה"
        caption={history.length === 0 ? undefined : `${history.length} רשומות`}
      />
      {history.length === 0 ? (
        <Text style={styles.emptyLog}>
          כל לחיצה על ״השקיתי״ תירשם כאן, כדי שתראה אם שכחת או השקית יותר מדי.
        </Text>
      ) : (
        <View style={styles.log}>
          {history.slice(0, 30).map((entry) => (
            <View key={entry.id} style={styles.logRow}>
              <Ionicons name={LOG_ICONS[entry.kind]} size={16} color={colors.textMuted} />
              <Text style={styles.logText}>
                {LOG_LABELS[entry.kind]}
                {entry.amountMl ? ` · ${formatWater(entry.amountMl)}` : ''}
                {entry.note ? ` · ${entry.note}` : ''}
              </Text>
              <Text style={styles.logDate}>{HE_DATE_TIME.format(new Date(entry.at))}</Text>
            </View>
          ))}
        </View>
      )}

      <View style={styles.footer}>
        <AppButton
          label="עריכה"
          variant="ghost"
          onPress={() => navigation.navigate('PlantForm', { plantId: plant.id })}
        />
        <AppButton label="מחיקת העציץ" variant="danger" onPress={confirmDelete} />
      </View>
    </ScrollView>
  );
}

function Stat({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: keyof typeof Ionicons.glyphMap;
}) {
  return (
    <View style={styles.stat}>
      <View style={styles.statHeader}>
        <Ionicons name={icon} size={14} color={colors.textMuted} />
        <Text style={styles.statLabel}>{label}</Text>
      </View>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  content: { padding: spacing.lg, gap: spacing.md },
  missing: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  missingText: { ...typography.body, color: colors.textMuted },
  photo: { width: '100%', height: 200, borderRadius: radius.lg },
  headerBlock: { gap: spacing.xs, alignItems: 'flex-end' },
  name: { ...typography.title, color: colors.text, ...rtlText },
  species: { ...typography.body, color: colors.textMuted, ...rtlText },
  weatherNote: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.waterSoft,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  weatherNoteText: { ...typography.small, color: colors.water, flex: 1, ...rtlText },
  actions: { flexDirection: 'row-reverse', gap: spacing.sm },
  grow: { flex: 1 },
  grid: { flexDirection: 'row-reverse', flexWrap: 'wrap', gap: spacing.sm },
  stat: {
    width: '48%',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    gap: spacing.xs,
    alignItems: 'flex-end',
  },
  statHeader: { flexDirection: 'row-reverse', alignItems: 'center', gap: spacing.xs },
  statLabel: { ...typography.small, color: colors.textMuted },
  statValue: { ...typography.bodyStrong, color: colors.text, ...rtlText },
  notes: { ...typography.body, color: colors.text, ...rtlText },
  emptyLog: { ...typography.small, color: colors.textMuted, ...rtlText },
  log: { gap: spacing.sm },
  logRow: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  logText: { ...typography.small, color: colors.text, flex: 1, ...rtlText },
  logDate: { ...typography.small, color: colors.textMuted },
  footer: { gap: spacing.sm, marginTop: spacing.lg },
});
