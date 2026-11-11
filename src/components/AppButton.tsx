import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, ViewStyle } from 'react-native';

import { colors, radius, spacing, typography } from '../theme';

type Variant = 'primary' | 'water' | 'ghost' | 'danger';

interface Props {
  label: string;
  onPress: () => void;
  variant?: Variant;
  disabled?: boolean;
  busy?: boolean;
  style?: ViewStyle;
}

const BACKGROUNDS: Record<Variant, string> = {
  primary: colors.primary,
  water: colors.water,
  ghost: 'transparent',
  danger: colors.danger,
};

const LABEL_COLORS: Record<Variant, string> = {
  primary: '#FFFFFF',
  water: '#FFFFFF',
  ghost: colors.primaryDark,
  danger: '#FFFFFF',
};

export function AppButton({
  label,
  onPress,
  variant = 'primary',
  disabled,
  busy,
  style,
}: Props) {
  const inactive = disabled || busy;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled: !!inactive }}
      onPress={onPress}
      disabled={inactive}
      style={({ pressed }) => [
        styles.base,
        { backgroundColor: BACKGROUNDS[variant] },
        variant === 'ghost' && styles.ghost,
        pressed && styles.pressed,
        inactive && styles.inactive,
        style,
      ]}
    >
      {busy ? (
        <ActivityIndicator color={LABEL_COLORS[variant]} />
      ) : (
        <Text style={[styles.label, { color: LABEL_COLORS[variant] }]}>{label}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 46,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ghost: {
    borderWidth: 1,
    borderColor: colors.border,
  },
  pressed: { opacity: 0.75 },
  inactive: { opacity: 0.45 },
  label: { ...typography.bodyStrong },
});
