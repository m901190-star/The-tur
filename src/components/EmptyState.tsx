import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, spacing, typography } from '../theme';
import { AppButton } from './AppButton';

interface Props {
  icon?: keyof typeof Ionicons.glyphMap;
  title: string;
  body: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryLabel?: string;
  onSecondary?: () => void;
  secondaryBusy?: boolean;
}

export function EmptyState({
  icon = 'leaf-outline',
  title,
  body,
  actionLabel,
  onAction,
  secondaryLabel,
  onSecondary,
  secondaryBusy,
}: Props) {
  return (
    <View style={styles.wrapper}>
      <View style={styles.badge}>
        <Ionicons name={icon} size={30} color={colors.primary} />
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{body}</Text>
      {actionLabel && onAction ? (
        <AppButton label={actionLabel} onPress={onAction} style={styles.action} />
      ) : null}
      {secondaryLabel && onSecondary ? (
        <AppButton
          label={secondaryLabel}
          variant="ghost"
          busy={secondaryBusy}
          onPress={onSecondary}
          style={styles.action}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { alignItems: 'center', gap: spacing.md, paddingVertical: spacing.xxl },
  badge: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: { ...typography.heading, color: colors.text, textAlign: 'center' },
  body: {
    ...typography.body,
    color: colors.textMuted,
    maxWidth: 280,
    writingDirection: 'rtl',
    textAlign: 'center',
  },
  action: { marginTop: spacing.sm, minWidth: 180 },
});
