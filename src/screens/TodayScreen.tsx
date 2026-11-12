import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useMemo, useState } from 'react';
import { Alert, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { EmptyState } from '../components/EmptyState';
import { PlantCard } from '../components/PlantCard';
import { SectionHeader } from '../components/SectionHeader';
import { SetupBanner } from '../components/SetupBanner';
import { WeatherStrip } from '../components/WeatherStrip';
import {
  fertilizeState,
  formatWater,
  needsWaterNow,
  sortByUrgency,
  totalWaterDue,
} from '../lib/watering';
import { detectLocation } from '../lib/location';
import { requestNotificationAccess } from '../lib/notifications';
import { frostRisk } from '../lib/weather';
import { RootStackParamList } from '../navigation';
import { GARDEN_SEED, buildSeedPlants } from '../gardenSeed';
import { usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';

/** "הלימון" / "הלימון והשפלרה" / "הלימון, השפלרה ועוד 2" */
function joinNames(names: string[]): string {
  if (names.length <= 2) return names.join(' ו');
  return `${names.slice(0, 2).join(', ')} ועוד ${names.length - 2}`;
}

const HE_FULL_DATE = new Intl.DateTimeFormat('he-IL', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});

export function TodayScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const insets = useSafeAreaInsets();
  const {
    plants,
    markWatered,
    snooze,
    settings,
    weather,
    weatherLoading,
    refreshWeather,
    addPlants,
    updateSettings,
  } = usePlants();
  const [seeding, setSeeding] = useState(false);
  const [enabling, setEnabling] = useState<'none' | 'push' | 'place'>('none');

  const enableReminders = useCallback(async () => {
    setEnabling('push');
    try {
      const allowed = await requestNotificationAccess();
      if (!allowed) {
        Alert.alert(
          'אין הרשאה להתראות',
          'אפשר לאשר התראות בהגדרות המכשיר ולחזור לכאן. בלי זה האפליקציה לא תוכל להזכיר לך כלום.',
        );
        return;
      }
      // The provider rebuilds the whole schedule when the settings change.
      await updateSettings({ notificationsEnabled: true });
    } finally {
      setEnabling('none');
    }
  }, [updateSettings]);

  const enableLocation = useCallback(async () => {
    setEnabling('place');
    try {
      const found = await detectLocation();
      if (!found) {
        navigation.navigate('Tabs', { screen: 'Settings' });
        return;
      }
      await updateSettings({
        latitude: found.latitude,
        longitude: found.longitude,
        locationLabel: found.label,
      });
      await refreshWeather(true);
    } finally {
      setEnabling('none');
    }
  }, [updateSettings, refreshWeather, navigation]);

  const seedGarden = useCallback(async () => {
    setSeeding(true);
    try {
      await addPlants(buildSeedPlants());
    } finally {
      setSeeding(false);
    }
  }, [addPlants]);
  // Recomputed on pull-to-refresh so a session left open overnight still shows
  // the right day without the user restarting the app.
  const [now, setNow] = useState(() => new Date());

  const refresh = useCallback(() => {
    setNow(new Date());
    void refreshWeather(true);
  }, [refreshWeather]);

  const { due, upcoming, litres, fertilizeDue } = useMemo(() => {
    const sorted = sortByUrgency(plants, now, weather);
    return {
      due: sorted.filter((plant) => needsWaterNow(plant, now, weather)),
      upcoming: sorted.filter((plant) => !needsWaterNow(plant, now, weather)),
      litres: totalWaterDue(plants, now, weather),
      fertilizeDue: plants.filter((plant) => fertilizeState(plant, now).due),
    };
  }, [plants, now, weather]);

  // Worth saying out loud only when something outside could actually be hit.
  const frost = useMemo(() => {
    const outdoor = plants.filter((plant) => plant.isOutdoor);
    if (outdoor.length === 0) return null;
    const risk = frostRisk(weather, now);
    if (!risk) return null;
    const label = (plant: (typeof outdoor)[number]) => plant.name || plant.species;
    // The two groups need opposite instructions, so they are counted apart.
    const cover = outdoor
      .filter((plant) => plant.isFrostTender && !plant.keepsDryInCold)
      .map(label)
      .filter(Boolean);
    const keepDry = outdoor.filter((plant) => plant.keepsDryInCold).map(label).filter(Boolean);
    return { ...risk, cover, keepDry };
  }, [plants, weather, now]);

  if (plants.length === 0) {
    return (
      <ScrollView
        contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.lg }]}
      >
        <EmptyState
          title="בוא נתחיל"
          body="הוסף את העציץ הראשון שלך, ומכאן האפליקציה תגיד לך בכל יום מה צריך השקיה."
          actionLabel="הוספת עציץ"
          onAction={() => navigation.navigate('PlantForm')}
          secondaryLabel={`הוספת הגינה שלי (${GARDEN_SEED.length} עציצים)`}
          onSecondary={seedGarden}
          secondaryBusy={seeding}
        />
      </ScrollView>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={[
        styles.content,
        { paddingTop: insets.top + spacing.lg, paddingBottom: insets.bottom + spacing.xxl },
      ]}
      refreshControl={<RefreshControl refreshing={false} onRefresh={refresh} />}
    >
      <Text style={styles.date}>{HE_FULL_DATE.format(now)}</Text>
      <Text style={styles.headline}>
        {due.length === 0 ? 'הכל מושקה' : `${due.length} עציצים צריכים מים`}
      </Text>

      {!settings.notificationsEnabled ? (
        <SetupBanner
          title="התראות כבויות"
          body="בלי זה האפליקציה לא תזכיר לך להשקות — תצטרך לפתוח אותה בעצמך כל פעם. הפעלה אחת, ומכאן התזכורות מגיעות לבד."
          actionLabel="הפעלת תזכורות"
          onPress={enableReminders}
          busy={enabling === 'push'}
        />
      ) : null}

      {settings.notificationsEnabled &&
      settings.weatherEnabled &&
      settings.latitude === null ? (
        <SetupBanner
          icon="location-outline"
          title="חסר מיקום"
          body="בלי מיקום ההשקיה עובדת לפי לוח עונתי בלבד — גשם וגל חום לא ישנו כלום."
          actionLabel="שימוש במיקום שלי"
          onPress={enableLocation}
          busy={enabling === 'place'}
        />
      ) : null}

      <WeatherStrip
        snapshot={weather}
        settings={settings}
        loading={weatherLoading}
        now={now}
        onConfigure={() => navigation.navigate('Tabs', { screen: 'Settings' })}
      />

      {due.length > 0 ? (
        <View style={styles.summary}>
          <Ionicons name="water" size={18} color={colors.water} />
          <Text style={styles.summaryText}>
            סך הכל {formatWater(litres)} להיום
          </Text>
        </View>
      ) : null}

      {frost ? (
        <View style={styles.frost}>
          <Ionicons name="snow-outline" size={18} color={colors.water} />
          <View style={styles.frostBody}>
            <Text style={styles.frostHeading}>
              {frost.daysAway === 0
                ? `קור הלילה: ${Math.round(frost.minTempC)}°`
                : `קור בעוד ${frost.daysAway} ${frost.daysAway === 1 ? 'יום' : 'ימים'}: ${Math.round(frost.minTempC)}°`}
            </Text>
            <Text style={styles.frostText}>
              להשקות בערב שלפני: קרקע לחה מחזיקה חום ומגינה על השורשים
              {frost.cover.length > 0 ? `, וכדאי גם לכסות את ${joinNames(frost.cover)}` : ''}.
            </Text>
            {frost.keepDry.length > 0 ? (
              <Text style={styles.frostText}>
                חוץ מ{joinNames(frost.keepDry)} — לקקטוסים ולסוקולנטים זה הפוך,
                קור ורטיבות ביחד מרקיבים אותם. ההשקיה שלהם נדחתה עד שהקור עובר.
              </Text>
            ) : null}
          </View>
        </View>
      ) : null}

      {fertilizeDue.length > 0 ? (
        <View style={styles.notice}>
          <Ionicons name="nutrition-outline" size={18} color={colors.primaryDark} />
          <Text style={styles.noticeText}>
            {fertilizeDue.length === 1
              ? `${fertilizeDue[0].name || fertilizeDue[0].species} מחכה לדישון`
              : `${fertilizeDue.length} עציצים מחכים לדישון`}
          </Text>
        </View>
      ) : null}

      {due.length > 0 ? (
        <>
          <SectionHeader title="להשקות עכשיו" caption="לחיצה על ״השקיתי״ מאפסת את הטיימר" />
          <View style={styles.list}>
            {due.map((plant) => (
              <PlantCard
                key={plant.id}
                plant={plant}
                now={now}
                weather={weather}
                onPress={() => navigation.navigate('PlantDetail', { plantId: plant.id })}
                onWater={() => markWatered(plant.id)}
                onSnooze={() => snooze(plant.id, 1)}
              />
            ))}
          </View>
        </>
      ) : (
        <View style={styles.allDone}>
          <Ionicons name="checkmark-circle" size={22} color={colors.primary} />
          <Text style={styles.allDoneText}>
            שום דבר לא דחוף היום. העציץ הבא בתור מופיע למטה.
          </Text>
        </View>
      )}

      {upcoming.length > 0 ? (
        <>
          <SectionHeader title="בהמשך השבוע" />
          <View style={styles.list}>
            {upcoming.slice(0, 5).map((plant) => (
              <PlantCard
                key={plant.id}
                plant={plant}
                now={now}
                weather={weather}
                onPress={() => navigation.navigate('PlantDetail', { plantId: plant.id })}
              />
            ))}
          </View>
        </>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { paddingHorizontal: spacing.lg, gap: spacing.xs },
  date: { ...typography.small, color: colors.textMuted, ...rtlText },
  headline: { ...typography.title, color: colors.text, ...rtlText },
  summary: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.waterSoft,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  summaryText: { ...typography.bodyStrong, color: colors.water, ...rtlText },
  notice: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.sm,
  },
  noticeText: { ...typography.small, color: colors.primaryDark, flex: 1, ...rtlText },
  allDone: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  allDoneText: { ...typography.body, color: colors.primaryDark, flex: 1, ...rtlText },
  frost: {
    flexDirection: 'row-reverse',
    gap: spacing.sm,
    backgroundColor: colors.waterSoft,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.sm,
    borderWidth: 1,
    borderColor: colors.water,
  },
  frostBody: { flex: 1, gap: spacing.xs },
  frostHeading: { ...typography.bodyStrong, color: colors.water, ...rtlText },
  frostText: { ...typography.small, color: colors.water, ...rtlText },
  list: { gap: spacing.md },
});
