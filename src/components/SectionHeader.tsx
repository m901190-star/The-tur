import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, rtlText, spacing, typography } from '../theme';

export function SectionHeader({ title, caption }: { title: string; caption?: string }) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>{title}</Text>
      {caption ? <Text style={styles.caption}>{caption}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: 2, marginTop: spacing.lg, marginBottom: spacing.sm },
  title: { ...typography.heading, color: colors.text, ...rtlText },
  caption: { ...typography.small, color: colors.textMuted, ...rtlText },
});
