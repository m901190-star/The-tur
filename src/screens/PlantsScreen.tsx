import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Chip } from '../components/Chip';
import { EmptyState } from '../components/EmptyState';
import { PlantCard } from '../components/PlantCard';
import { formatWater, sortByUrgency } from '../lib/watering';
import { RootStackParamList } from '../navigation';
import { GARDEN_SEED, buildSeedPlants } from '../gardenSeed';
import { usePlants } from '../state/PlantsContext';
import { colors, radius, rtlText, spacing, typography } from '../theme';

export function PlantsScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const insets = useSafeAreaInsets();
  const { plants, weather, addPlants } = usePlants();
  const [seeding, setSeeding] = useState(false);

  const seedGarden = useCallback(async () => {
    setSeeding(true);
    try {
      await addPlants(buildSeedPlants());
    } finally {
      setSeeding(false);
    }
  }, [addPlants]);
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState<string | null>(null);
  const now = useMemo(() => new Date(), []);

  const locations = useMemo(() => {
    const unique = new Set(
      plants.map((plant) => plant.location.trim()).filter((value) => value.length > 0),
    );
    return [...unique].sort((a, b) => a.localeCompare(b, 'he'));
  }, [plants]);

  const visible = useMemo(() => {
    const needle = query.trim();
    return sortByUrgency(plants, now, weather).filter((plant) => {
      const matchesQuery =
        !needle ||
        plant.name.includes(needle) ||
        plant.species.includes(needle) ||
        plant.location.includes(needle);
      const matchesLocation = !location || plant.location.trim() === location;
      return matchesQuery && matchesLocation;
    });
  }, [plants, query, location, now, weather]);

  const totalWater = visible.reduce((sum, plant) => sum + Math.max(0, plant.waterMl), 0);

  return (
    <View style={styles.screen}>
      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.lg, paddingBottom: insets.bottom + 96 },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.headline}>העציצים שלי</Text>
        <Text style={styles.caption}>
          {plants.length} עציצים · {formatWater(totalWater)} בסבב השקיה מלא
        </Text>

        {plants.length > 0 ? (
          <View style={styles.searchRow}>
            <Ionicons name="search" size={18} color={colors.textMuted} />
            <TextInput
              value={query}
              onChangeText={setQuery}
              placeholder="חיפוש לפי שם, סוג או מקום"
              placeholderTextColor={colors.textMuted}
              style={styles.searchInput}
            />
          </View>
        ) : null}

        {locations.length > 1 ? (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.filters}
          >
            <Chip label="הכל" selected={location === null} onPress={() => setLocation(null)} />
            {locations.map((value) => (
              <Chip
                key={value}
                label={value}
                selected={location === value}
                onPress={() => setLocation(location === value ? null : value)}
              />
            ))}
          </ScrollView>
        ) : null}

        {plants.length === 0 ? (
          <EmptyState
            title="עדיין אין עציצים"
            body="כל עציץ שתוסיף כאן יקבל תדירות השקיה משלו, וממנה נבנה היומן."
            actionLabel="הוספת עציץ"
            onAction={() => navigation.navigate('PlantForm')}
            secondaryLabel={`הוספת הגינה שלי (${GARDEN_SEED.length} עציצים)`}
            onSecondary={seedGarden}
            secondaryBusy={seeding}
          />
        ) : visible.length === 0 ? (
          <EmptyState
            icon="search-outline"
            title="לא נמצא עציץ"
            body="נסה שם אחר, או נקה את הסינון."
          />
        ) : (
          <View style={styles.list}>
            {visible.map((plant) => (
              <PlantCard
                key={plant.id}
                plant={plant}
                now={now}
                weather={weather}
                onPress={() => navigation.navigate('PlantDetail', { plantId: plant.id })}
              />
            ))}
          </View>
        )}
      </ScrollView>

      <Pressable
        accessibilityRole="button"
        accessibilityLabel="הוספת עציץ"
        onPress={() => navigation.navigate('PlantForm')}
        style={({ pressed }) => [
          styles.fab,
          { bottom: insets.bottom + spacing.lg },
          pressed && styles.fabPressed,
        ]}
      >
        <Ionicons name="add" size={26} color="#FFFFFF" />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { paddingHorizontal: spacing.lg, gap: spacing.sm },
  headline: { ...typography.title, color: colors.text, ...rtlText },
  caption: { ...typography.small, color: colors.textMuted, ...rtlText },
  searchRow: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    marginTop: spacing.sm,
  },
  searchInput: {
    flex: 1,
    minHeight: 44,
    ...typography.body,
    color: colors.text,
    ...rtlText,
  },
  filters: { flexDirection: 'row-reverse', gap: spacing.sm, paddingVertical: spacing.sm },
  list: { gap: spacing.md, marginTop: spacing.sm },
  fab: {
    position: 'absolute',
    left: spacing.lg,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
  },
  fabPressed: { opacity: 0.8 },
});
