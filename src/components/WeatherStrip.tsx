import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { MIN_USEFUL_RAIN_MM, dayFor, describeToday } from '../lib/weather';
import { colors, radius, rtlText, spacing, typography } from '../theme';
import { Settings, WeatherSnapshot } from '../types';

interface Props {
  snapshot: WeatherSnapshot | null;
  settings: Settings;
  loading: boolean;
  now: Date;
  /** Opens settings when the weather has nowhere to read a location from. */
  onConfigure: () => void;
}

export function WeatherStrip({ snapshot, settings, loading, now, onConfigure }: Props) {
  if (!settings.weatherEnabled) return null;

  if (settings.latitude === null || settings.longitude === null) {
    return (
      <Pressable
        accessibilityRole="button"
        onPress={onConfigure}
        style={({ pressed }) => [styles.strip, styles.prompt, pressed && styles.pressed]}
      >
        <Ionicons name="location-outline" size={18} color={colors.water} />
        <Text style={styles.promptText}>
          הגדר מיקום כדי שהשקיה תתחשב בגשם ובחום
        </Text>
        <Ionicons name="chevron-back" size={16} color={colors.water} />
      </Pressable>
    );
  }

  if (!snapshot) {
    return (
      <View style={[styles.strip, styles.neutral]}>
        {loading ? (
          <ActivityIndicator size="small" color={colors.water} />
        ) : (
          <Ionicons name="cloud-offline-outline" size={18} color={colors.textMuted} />
        )}
        <Text style={styles.neutralText}>
          {loading ? 'טוען מזג אוויר…' : 'אין נתוני מזג אוויר — משתמשים בלוח הרגיל'}
        </Text>
      </View>
    );
  }

  const today = dayFor(snapshot, now);
  const raining = (today?.rainMm ?? 0) >= MIN_USEFUL_RAIN_MM;
  const summary = describeToday(snapshot, now);

  return (
    <View style={[styles.strip, raining ? styles.rain : styles.neutral]}>
      <Ionicons
        name={raining ? 'rainy-outline' : 'partly-sunny-outline'}
        size={18}
        color={raining ? colors.water : colors.today}
      />
      <Text style={styles.summaryText}>{summary ?? 'מזג אוויר לא זמין'}</Text>
      {settings.locationLabel ? (
        <Text style={styles.place}>{settings.locationLabel}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  strip: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  neutral: { backgroundColor: colors.surfaceAlt },
  rain: { backgroundColor: colors.waterSoft },
  prompt: { backgroundColor: colors.waterSoft },
  pressed: { opacity: 0.8 },
  promptText: { ...typography.small, color: colors.water, flex: 1, ...rtlText },
  neutralText: { ...typography.small, color: colors.textMuted, flex: 1, ...rtlText },
  summaryText: { ...typography.bodyStrong, color: colors.text, flex: 1, ...rtlText },
  place: { ...typography.small, color: colors.textMuted },
});
