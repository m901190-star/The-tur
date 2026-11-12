import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, rtlText, spacing, typography } from '../theme';

interface Props {
  title: string;
  body: string;
  actionLabel: string;
  onPress: () => void;
  busy?: boolean;
  icon?: keyof typeof Ionicons.glyphMap;
}

/**
 * The one thing standing between the app and actually being useful.
 *
 * Reminders are off until the device grants permission, and nothing about a
 * working-looking list of plants tells the user that. Without this, the app
 * sits there looking correct and silently never reminds anyone of anything.
 */
export function SetupBanner({
  title,
  body,
  actionLabel,
  onPress,
  busy,
  icon = 'notifications-outline',
}: Props) {
  return (
    <View style={styles.banner}>
      <View style={styles.header}>
        <Ionicons name={icon} size={20} color={colors.primaryDark} />
        <Text style={styles.title}>{title}</Text>
      </View>
      <Text style={styles.body}>{body}</Text>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={actionLabel}
        accessibilityState={{ disabled: !!busy }}
        onPress={onPress}
        disabled={busy}
        style={({ pressed }) => [styles.action, pressed && styles.pressed]}
      >
        {busy ? (
          <ActivityIndicator color="#FFFFFF" size="small" />
        ) : (
          <Text style={styles.actionLabel}>{actionLabel}</Text>
        )}
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.primary,
    padding: spacing.lg,
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  header: { flexDirection: 'row-reverse', alignItems: 'center', gap: spacing.sm },
  title: { ...typography.bodyStrong, color: colors.primaryDark, flex: 1, ...rtlText },
  body: { ...typography.small, color: colors.primaryDark, ...rtlText },
  action: {
    backgroundColor: colors.primary,
    borderRadius: radius.sm,
    paddingVertical: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
    marginTop: spacing.xs,
  },
  pressed: { opacity: 0.8 },
  actionLabel: { ...typography.bodyStrong, color: '#FFFFFF' },
});
