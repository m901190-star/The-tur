import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '../theme';
import { DueStatus, WateringState, statusLabel } from '../lib/watering';

const PALETTE: Record<DueStatus, { bg: string; fg: string }> = {
  overdue: { bg: colors.overdueSoft, fg: colors.overdue },
  today: { bg: colors.todaySoft, fg: colors.today },
  never: { bg: colors.waterSoft, fg: colors.water },
  soon: { bg: colors.calmSoft, fg: colors.calm },
  ok: { bg: colors.calmSoft, fg: colors.calm },
};

export function StatusPill({ state }: { state: WateringState }) {
  const palette = PALETTE[state.status];
  return (
    <View style={[styles.pill, { backgroundColor: palette.bg }]}>
      <Text style={[styles.label, { color: palette.fg }]}>{statusLabel(state)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
  },
  label: { ...typography.tiny },
});
