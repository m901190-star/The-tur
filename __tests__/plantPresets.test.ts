import { PLANT_PRESETS, findPreset, searchPresets } from '../src/plantPresets';

describe('plant presets', () => {
  it('has a unique species name per entry', () => {
    const names = PLANT_PRESETS.map((preset) => preset.species);
    expect(new Set(names).size).toBe(names.length);
  });

  it('waters every plant less often in winter than in summer', () => {
    for (const preset of PLANT_PRESETS) {
      expect(preset.intervalWinterDays).toBeGreaterThanOrEqual(preset.intervalSummerDays);
    }
  });

  it('gives every preset a positive interval, amount and a tip', () => {
    for (const preset of PLANT_PRESETS) {
      expect(preset.intervalSummerDays).toBeGreaterThan(0);
      expect(preset.waterMl).toBeGreaterThan(0);
      expect(preset.tip.length).toBeGreaterThan(10);
    }
  });

  it('finds a preset by exact species name, trimming whitespace', () => {
    expect(findPreset(' מונסטרה ')?.species).toBe('מונסטרה');
    expect(findPreset('עץ שלא קיים')).toBeUndefined();
  });

  it('searches by substring and returns everything for an empty query', () => {
    expect(searchPresets('')).toHaveLength(PLANT_PRESETS.length);
    expect(searchPresets('   ')).toHaveLength(PLANT_PRESETS.length);
    const results = searchPresets('קקט');
    expect(results.length).toBeGreaterThan(0);
    expect(results.every((preset) => preset.species.includes('קקט'))).toBe(true);
  });
});
