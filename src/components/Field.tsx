import React from 'react';
import { StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';

import { colors, radius, rtlText, spacing, typography } from '../theme';

interface Props extends TextInputProps {
  label: string;
  hint?: string;
  suffix?: string;
}

export function Field({ label, hint, suffix, style, ...inputProps }: Props) {
  return (
    <View style={styles.wrapper}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <View style={styles.inputRow}>
        <TextInput
          {...inputProps}
          placeholderTextColor={colors.textMuted}
          style={[styles.input, style]}
        />
        {suffix ? <Text style={styles.suffix}>{suffix}</Text> : null}
      </View>
      {hint ? <Text style={styles.hint}>{hint}</Text> : null}
    </View>
  );
}

export function FieldGroup({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>{children}</View>
      {hint ? <Text style={styles.hint}>{hint}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: spacing.sm },
  label: { ...typography.bodyStrong, color: colors.text, ...rtlText },
  inputRow: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
  },
  input: {
    flex: 1,
    minHeight: 46,
    ...typography.body,
    color: colors.text,
    ...rtlText,
  },
  suffix: { ...typography.small, color: colors.textMuted },
  hint: { ...typography.small, color: colors.textMuted, ...rtlText },
  row: { flexDirection: 'row-reverse', flexWrap: 'wrap', gap: spacing.sm },
});
