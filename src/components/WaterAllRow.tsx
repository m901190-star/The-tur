import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, rtlText, spacing, typography } from '../theme';

interface Props {
  onConfirm: (daysAgo: number) => Promise<void>;
}

const WHEN: { label: string; daysAgo: number }[] = [
  { label: 'היום', daysAgo: 0 },
  { label: 'אתמול', daysAgo: 1 },
  { label: 'שלשום', daysAgo: 2 },
];

/**
 * Marks the whole garden watered in one go.
 *
 * Watering every planter in one round is how it actually happens, and the day
 * is often not today — you remember on Monday that you did it on Saturday. The
 * choice is inline rather than a dialog so it works the same everywhere.
 */
export function WaterAllRow({ onConfirm }: Props) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const apply = async (daysAgo: number) => {
    setBusy(true);
    try {
      await onConfirm(daysAgo);
      setOpen(false);
    } finally {
      setBusy(false);
    }
  };

  if (!open) {
    return (
      <Pressable
        accessibilityRole="button"
        onPress={() => setOpen(true)}
        style={({ pressed }) => [styles.row, pressed && styles.pressed]}
      >
        <Ionicons name="checkmark-done-outline" size={18} color={colors.water} />
        <Text style={styles.label}>השקיתי את כל העציצים</Text>
      </Pressable>
    );
  }

  return (
    <View style={styles.open}>
      <Text style={styles.question}>מתי השקית את כולם?</Text>
      <View style={styles.choices}>
        {WHEN.map((option) => (
          <Pressable
            key={option.label}
            accessibilityRole="button"
            disabled={busy}
            onPress={() => apply(option.daysAgo)}
            style={({ pressed }) => [styles.choice, pressed && styles.pressed]}
          >
            <Text style={styles.choiceLabel}>{option.label}</Text>
          </Pressable>
        ))}
        <Pressable
          accessibilityRole="button"
          disabled={busy}
          onPress={() => setOpen(false)}
          style={({ pressed }) => [styles.cancel, pressed && styles.pressed]}
        >
          {busy ? (
            <ActivityIndicator size="small" color={colors.textMuted} />
          ) : (
            <Text style={styles.cancelLabel}>ביטול</Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.waterSoft,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    marginTop: spacing.md,
  },
  pressed: { opacity: 0.75 },
  label: { ...typography.bodyStrong, color: colors.water, flex: 1, ...rtlText },
  open: {
    backgroundColor: colors.waterSoft,
    borderRadius: radius.md,
    padding: spacing.md,
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  question: { ...typography.bodyStrong, color: colors.water, ...rtlText },
  choices: { flexDirection: 'row-reverse', flexWrap: 'wrap', gap: spacing.sm },
  choice: {
    backgroundColor: colors.water,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    minHeight: 44,
    justifyContent: 'center',
  },
  choiceLabel: { ...typography.bodyStrong, color: '#FFFFFF' },
  cancel: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    minHeight: 44,
    justifyContent: 'center',
  },
  cancelLabel: { ...typography.small, color: colors.textMuted },
});
