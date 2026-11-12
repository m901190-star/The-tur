import { GARDEN_SEED, buildSeedPlants } from '../src/gardenSeed';
import { PLANT_PRESETS, findPreset } from '../src/plantPresets';
import { baseIntervalDays, fertilizeState, suggestWaterForContainer } from '../src/lib/watering';

describe('garden seed', () => {
  it('names a real preset for every entry', () => {
    const known = new Set(PLANT_PRESETS.map((preset) => preset.species));
    for (const seed of GARDEN_SEED) {
      expect(known).toContain(seed.species);
    }
  });

  it('gives every planter a name and a volume', () => {
    for (const seed of GARDEN_SEED) {
      expect(seed.name.trim().length).toBeGreaterThan(0);
      expect(seed.containerLiters).toBeGreaterThan(0);
    }
  });

  it('uses a distinct name per planter, so the list is readable', () => {
    const names = GARDEN_SEED.map((seed) => seed.name);
    expect(new Set(names).size).toBe(names.length);
  });

  it('keeps the three cypresses in three separate containers', () => {
    const cypresses = GARDEN_SEED.filter((seed) => seed.species === 'ברוש');
    expect(cypresses).toHaveLength(3);
    for (const cypress of cypresses) {
      // One tree each: three in one planter would shorten the interval.
      expect(cypress.plantCount ?? 1).toBe(1);
    }
  });

  it('builds plants whose water comes from the volume and the species ratio', () => {
    const built = buildSeedPlants();
    expect(built).toHaveLength(GARDEN_SEED.length);
    for (const [index, plant] of built.entries()) {
      const seed = GARDEN_SEED[index];
      const preset = findPreset(seed.species)!;
      expect(plant.waterMl).toBe(
        suggestWaterForContainer(seed.containerLiters, preset.mlPerLiterOfSoil),
      );
    }
  });

  it('marks every one of them as outdoors', () => {
    expect(buildSeedPlants().every((plant) => plant.isOutdoor)).toBe(true);
  });

  it('marks both succulents to stay dry in the cold, and nothing else', () => {
    const built = buildSeedPlants();
    const dry = built.filter((plant) => plant.keepsDryInCold).map((plant) => plant.species);
    // The crown of thorns is a succulent too, so it gets the same handling.
    expect(new Set(dry)).toEqual(new Set(['כתר קוצים', 'אופונטיה (אוזני ארנב)']));
    // The lemon is frost-tender but wants the opposite treatment.
    const lemon = built.find((plant) => plant.species.includes('לימון'));
    expect(lemon?.keepsDryInCold).toBe(false);
  });

  it('carries frost tenderness over from the preset', () => {
    const built = buildSeedPlants();
    const lemon = built.find((plant) => plant.species.includes('לימון'));
    const cypress = built.find((plant) => plant.species === 'ברוש');
    expect(lemon?.isFrostTender).toBe(true);
    expect(cypress?.isFrostTender).toBe(false);
  });

  it('starts every plant as watered, so nothing is overdue on day one', () => {
    const now = new Date(2026, 10, 12, 9);
    for (const plant of buildSeedPlants(now)) {
      expect(plant.lastWateredAt).toBe(now.toISOString());
    }
  });

  it('starts the fed plants as fed, so the list does not open with a dozen alerts', () => {
    const now = new Date(2026, 10, 12, 9);
    for (const plant of buildSeedPlants(now)) {
      if (plant.fertilizeEveryDays) {
        expect(fertilizeState({ ...plant, id: 'x', createdAt: '', calendarEventId: null }, now).due).toBe(
          false,
        );
      }
    }
  });

  it('produces sane intervals for the cypresses in their own pots', () => {
    const now = new Date(2026, 6, 15);
    const cypress = buildSeedPlants().find((plant) => plant.species === 'ברוש')!;
    const asPlant = {
      ...cypress,
      id: 'c',
      createdAt: now.toISOString(),
      calendarEventId: null,
    };
    // One tree per planter means the stated summer interval, undamped.
    expect(baseIntervalDays(asPlant, now)).toBe(5);
  });
});
