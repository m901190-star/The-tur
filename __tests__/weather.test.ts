import {
  BASELINE_ET0,
  MIN_USEFUL_RAIN_MM,
  averageEt0,
  describeToday,
  isStale,
  parseForecast,
  recentRainMm,
  upcomingRainMm,
  weatherAdjustment,
} from '../src/lib/weather';
import { toDateKey } from '../src/lib/dates';
import { DailyWeather, Plant, WeatherSnapshot } from '../src/types';

function at(year: number, month: number, day: number, hour = 12): Date {
  return new Date(year, month - 1, day, hour, 0, 0, 0);
}

function makePlant(overrides: Partial<Plant> = {}): Plant {
  return {
    id: 'p1',
    name: 'ברושים',
    species: 'ברוש',
    location: 'מרפסת',
    waterMl: 10000,
    intervalSummerDays: 5,
    intervalWinterDays: 12,
    light: 'full-sun',
    potSize: 'large',
    containerLiters: 70,
    plantCount: 1,
    isOutdoor: true,
    fertilizeEveryDays: 60,
    lastWateredAt: null,
    lastFertilizedAt: null,
    photoUri: null,
    notes: '',
    createdAt: '2026-01-01T00:00:00.000Z',
    calendarEventId: null,
    ...overrides,
  };
}

/**
 * Builds a snapshot centred on `now`: `offsets` maps a day offset (negative is
 * the past) to that day's weather.
 */
function makeSnapshot(
  now: Date,
  offsets: Record<number, Partial<DailyWeather>>,
  fetchedAt: Date = now,
): WeatherSnapshot {
  const days: DailyWeather[] = Object.entries(offsets).map(([offset, values]) => {
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    date.setDate(date.getDate() + Number(offset));
    return {
      date: toDateKey(date),
      rainMm: 0,
      rainChance: 0,
      et0Mm: 5.5,
      maxTempC: 28,
      ...values,
    };
  });
  return {
    fetchedAt: fetchedAt.toISOString(),
    latitude: 32.08,
    longitude: 34.78,
    timezone: 'Asia/Jerusalem',
    days,
  };
}

/** Every day in [-3, +6] gets the same weather. */
function flatSnapshot(now: Date, values: Partial<DailyWeather>): WeatherSnapshot {
  const offsets: Record<number, Partial<DailyWeather>> = {};
  for (let offset = -3; offset <= 6; offset += 1) offsets[offset] = values;
  return makeSnapshot(now, offsets);
}

describe('parseForecast', () => {
  it('maps the Open-Meteo payload into daily rows', () => {
    const snapshot = parseForecast(
      {
        latitude: 32.1,
        longitude: 34.83,
        timezone: 'Asia/Jerusalem',
        daily: {
          time: ['2026-11-08', '2026-11-09'],
          precipitation_sum: [4.8, 0],
          precipitation_probability_max: [80, 5],
          et0_fao_evapotranspiration: [1.98, 3.07],
          temperature_2m_max: [21, 21.7],
        },
      },
      32.08,
      34.78,
      at(2026, 11, 9),
    );

    expect(snapshot.days).toHaveLength(2);
    expect(snapshot.days[0]).toEqual({
      date: '2026-11-08',
      rainMm: 4.8,
      rainChance: 80,
      et0Mm: 1.98,
      maxTempC: 21,
    });
    expect(snapshot.timezone).toBe('Asia/Jerusalem');
  });

  it('survives missing arrays and null entries', () => {
    const snapshot = parseForecast(
      { daily: { time: ['2026-11-08'], precipitation_sum: [null] } },
      32,
      34,
    );
    expect(snapshot.days[0].rainMm).toBe(0);
    expect(snapshot.days[0].et0Mm).toBe(0);
    expect(snapshot.latitude).toBe(32);
  });

  it('returns no days when the payload has no daily block', () => {
    expect(parseForecast({}, 32, 34).days).toEqual([]);
  });
});

describe('windows over the snapshot', () => {
  const now = at(2026, 7, 15);

  it('sums rain that already fell, including today', () => {
    const snapshot = makeSnapshot(now, {
      '-3': { rainMm: 100 },
      '-2': { rainMm: 5 },
      '-1': { rainMm: 3 },
      0: { rainMm: 2 },
      1: { rainMm: 50 },
    });
    // Default window is two days back plus today; -3 and tomorrow are outside it.
    expect(recentRainMm(snapshot, now)).toBe(10);
  });

  it('sums rain expected from tomorrow on, leaving today to the past window', () => {
    const snapshot = makeSnapshot(now, {
      '-1': { rainMm: 90 },
      0: { rainMm: 4 },
      1: { rainMm: 6 },
      2: { rainMm: 70 },
    });
    expect(upcomingRainMm(snapshot, now)).toBe(6);
  });

  it('never counts today\u2019s rain in both windows', () => {
    const snapshot = makeSnapshot(now, { 0: { rainMm: 9 } });
    expect(recentRainMm(snapshot, now) + upcomingRainMm(snapshot, now)).toBe(9);
  });

  it('averages evaporative demand over the coming days', () => {
    const snapshot = makeSnapshot(now, {
      0: { et0Mm: 6 },
      1: { et0Mm: 4 },
      2: { et0Mm: 5 },
      3: { et0Mm: 100 },
    });
    expect(averageEt0(snapshot, now)).toBe(5);
  });

  it('returns null demand when the snapshot has nothing useful', () => {
    expect(averageEt0(makeSnapshot(now, { 0: { et0Mm: 0 } }), now)).toBeNull();
    expect(averageEt0(makeSnapshot(now, {}), now)).toBeNull();
  });
});

describe('weatherAdjustment', () => {
  const summer = at(2026, 7, 15);

  it('leaves indoor plants alone, however hard it rains', () => {
    const snapshot = flatSnapshot(summer, { rainMm: 40, et0Mm: 1 });
    const result = weatherAdjustment(makePlant({ isOutdoor: false }), 7, snapshot, summer);
    expect(result).toEqual({ deltaDays: 0, reason: null });
  });

  it('does nothing without a snapshot', () => {
    expect(weatherAdjustment(makePlant(), 7, null, summer).deltaDays).toBe(0);
  });

  it('does nothing when the forecast carries no demand figure', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 0 });
    expect(weatherAdjustment(makePlant(), 7, snapshot, summer).deltaDays).toBe(0);
  });

  it('postpones watering after real rain', () => {
    // 22 mm of rain against 5.5 mm/day of demand is about four days of water.
    const snapshot = makeSnapshot(summer, {
      '-1': { rainMm: 22 },
      0: { et0Mm: 5.5 },
      1: { et0Mm: 5.5 },
      2: { et0Mm: 5.5 },
    });
    const result = weatherAdjustment(makePlant(), 7, snapshot, summer);
    expect(result.deltaDays).toBe(4);
    expect(result.reason).toContain('גשם');
    expect(result.reason).toContain('דחינו');
  });

  it('ignores a drizzle that only wets the surface', () => {
    const snapshot = flatSnapshot(summer, { rainMm: 0 });
    const drizzle = makeSnapshot(summer, {
      0: { rainMm: MIN_USEFUL_RAIN_MM - 1, et0Mm: 5.5 },
      1: { et0Mm: 5.5 },
      2: { et0Mm: 5.5 },
    });
    expect(weatherAdjustment(makePlant(), 7, drizzle, summer).deltaDays).toBe(
      weatherAdjustment(makePlant(), 7, snapshot, summer).deltaDays,
    );
  });

  it('brings watering forward in a heatwave', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 9, maxTempC: 39 });
    const result = weatherAdjustment(makePlant(), 7, snapshot, summer);
    expect(result.deltaDays).toBeLessThan(0);
    expect(result.reason).toContain('חם מהרגיל');
  });

  it('stretches the interval when it is unusually cool and humid', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 3, maxTempC: 24 });
    const result = weatherAdjustment(makePlant(), 7, snapshot, summer);
    expect(result.deltaDays).toBeGreaterThan(0);
    expect(result.reason).toContain('קריר');
  });

  it('never shortens the interval below a single day', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 50, maxTempC: 48 });
    const result = weatherAdjustment(makePlant(), 2, snapshot, summer);
    expect(2 + result.deltaDays).toBeGreaterThanOrEqual(1);
  });

  it('caps the demand factor so one odd forecast cannot double the interval', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 0.2, maxTempC: 12 });
    const result = weatherAdjustment(makePlant(), 10, snapshot, summer);
    // 1.6x is the ceiling, so ten days become at most sixteen.
    expect(result.deltaDays).toBeLessThanOrEqual(6);
  });

  it('never lets rain buy more than one full cycle', () => {
    const snapshot = makeSnapshot(summer, {
      '-1': { rainMm: 300 },
      0: { et0Mm: 5.5 },
      1: { et0Mm: 5.5 },
      2: { et0Mm: 5.5 },
    });
    const result = weatherAdjustment(makePlant(), 7, snapshot, summer);
    expect(result.deltaDays).toBeLessThanOrEqual(7);
  });

  it('measures demand against the winter baseline in winter', () => {
    const winter = at(2026, 12, 15);
    // Winter ET0 at its baseline should move nothing at all.
    const snapshot = flatSnapshot(winter, { et0Mm: BASELINE_ET0.winter, maxTempC: 17 });
    expect(weatherAdjustment(makePlant(), 12, snapshot, winter).deltaDays).toBe(0);
  });
});

describe('describeToday', () => {
  const now = at(2026, 7, 15);

  it('names the temperature and real rain', () => {
    const snapshot = makeSnapshot(now, { 0: { maxTempC: 31.4, rainMm: 12 } });
    expect(describeToday(snapshot, now)).toBe('31° · 12 מ״מ גשם');
  });

  it('falls back to the chance of rain when none has fallen', () => {
    const snapshot = makeSnapshot(now, { 0: { maxTempC: 22, rainChance: 60 } });
    expect(describeToday(snapshot, now)).toBe('22° · 60% סיכוי לגשם');
  });

  it('shows the temperature alone on a dry, unlikely day', () => {
    const snapshot = makeSnapshot(now, { 0: { maxTempC: 29, rainChance: 10 } });
    expect(describeToday(snapshot, now)).toBe('29°');
  });

  it('returns null without a snapshot or a matching day', () => {
    expect(describeToday(null, now)).toBeNull();
    expect(describeToday(makeSnapshot(now, { 5: {} }), now)).toBeNull();
  });
});

describe('isStale', () => {
  const now = at(2026, 7, 15, 12);

  it('treats a missing or unreadable snapshot as stale', () => {
    expect(isStale(null, now)).toBe(true);
    expect(
      isStale({ ...flatSnapshot(now, {}), fetchedAt: 'nonsense' }, now),
    ).toBe(true);
  });

  it('keeps a recent snapshot and drops an old one', () => {
    expect(isStale(flatSnapshot(now, {}), now)).toBe(false);
    const old = makeSnapshot(now, { 0: {} }, at(2026, 7, 15, 2));
    expect(isStale(old, now)).toBe(true);
  });
});
