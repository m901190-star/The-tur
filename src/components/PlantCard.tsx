import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';

import { formatRelativeDay, formatWater, intervalDays, wateringState } from '../lib/watering';
import { colors, radius, rtlText, spacing, typography } from '../theme';
import { Plant } from '../types';
import { AppButton } from './AppButton';
import { StatusPill } from './StatusPill';

interface Props {
  plant: Plant;
  now: Date;
  onPress: () => void;
  onWater?: () => void;
  onSnooze?: () => void;
}

export function PlantCard({ plant, now, onPress, onWater, onSnooze }: Props) {
  const state = wateringState(plant, now);
  const subtitleParts = [plant.species, plant.location].filter(Boolean);

  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
    >
      <View style={styles.header}>
        {plant.photoUri ? (
          <Image source={{ uri: plant.photoUri }} style={styles.photo} />
        ) : (
          <View style={[styles.photo, styles.photoPlaceholder]}>
            <Ionicons name="leaf-outline" size={24} color={colors.primary} />
          </View>
        )}
        <View style={styles.headerText}>
          <Text style={styles.name} numberOfLines={1}>
            {plant.name || plant.species || 'עציץ'}
          </Text>
          {subtitleParts.length > 0 ? (
            <Text style={styles.subtitle} numberOfLines={1}>
              {subtitleParts.join(' · ')}
            </Text>
          ) : null}
          <StatusPill state={state} />
        </View>
      </View>

      <View style={styles.metaRow}>
        <Meta icon="water-outline" text={formatWater(plant.waterMl)} />
        <Meta icon="repeat-outline" text={`כל ${intervalDays(plant, now)} ימים`} />
        <Meta
          icon="time-outline"
          text={
            state.nextDate
              ? formatRelativeDay(state.nextDate, now)
              : 'סמן השקיה ראשונה'
          }
        />
      </View>

      {onWater || onSnooze ? (
        <View style={styles.actions}>
          {onWater ? (
            <AppButton
              label="השקיתי"
              variant="water"
              onPress={onWater}
              style={styles.actionGrow}
            />
          ) : null}
          {onSnooze ? (
            <AppButton label="דחה ליום" variant="ghost" onPress={onSnooze} />
          ) : null}
        </View>
      ) : null}
    </Pressable>
  );
}

function Meta({ icon, text }: { icon: keyof typeof Ionicons.glyphMap; text: string }) {
  return (
    <View style={styles.meta}>
      <Ionicons name={icon} size={14} color={colors.textMuted} />
      <Text style={styles.metaText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.md,
  },
  pressed: { opacity: 0.85 },
  header: { flexDirection: 'row-reverse', gap: spacing.md, alignItems: 'center' },
  photo: { width: 56, height: 56, borderRadius: radius.md },
  photoPlaceholder: {
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerText: { flex: 1, gap: spacing.xs, alignItems: 'flex-end' },
  name: { ...typography.heading, color: colors.text, ...rtlText },
  subtitle: { ...typography.small, color: colors.textMuted, ...rtlText },
  metaRow: {
    flexDirection: 'row-reverse',
    flexWrap: 'wrap',
    gap: spacing.md,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceAlt,
  },
  meta: { flexDirection: 'row-reverse', alignItems: 'center', gap: spacing.xs },
  metaText: { ...typography.small, color: colors.textMuted },
  actions: { flexDirection: 'row-reverse', gap: spacing.sm },
  actionGrow: { flex: 1 },
});
