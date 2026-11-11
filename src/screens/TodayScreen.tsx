import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useMemo, useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { EmptyState } from '../components/EmptyState';
import { PlantCard } from '../components/PlantCard';
import { SectionHeader } from '../components/SectionHeader';
import { WeatherStrip } from '../components/WeatherStrip';
import {
  fertilizeState,
  formatWater,
  needsWaterNow,
  sortByUrgency,
  totalWaterDue,
} from '../lib/watering';
import { RootStackParamList } from '../navigation';
import { usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';

const HE_FULL_DATE = new Intl.DateTimeFormat('he-IL', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});

export function TodayScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const insets = useSafeAreaInsets();
  const { plants, markWatered, snooze, settings, weather, weatherLoading, refreshWeather } =
    usePlants();
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
  list: { gap: spacing.md },
});
