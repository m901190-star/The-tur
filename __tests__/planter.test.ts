import {
  baseIntervalDays,
  containerLitersFor,
  crowdingFactor,
  intervalDays,
  seasonalIntervalDays,
  suggestWaterForContainer,
} from '../src/lib/watering';
import { toDateKey } from '../src/lib/dates';
import { DailyWeather, Plant, WeatherSnapshot } from '../src/types';

function at(year: number, month: number, day: number, hour = 12): Date {
  return new Date(year, month - 1, day, hour, 0, 0, 0);
}

function makePlant(overrides: Partial<Plant> = {}): Plant {
  return {
    id: 'p1',
    name: 'הברושים',
    species: 'ברוש',
    location: 'חצר',
    waterMl: 10500,
    intervalSummerDays: 5,
    intervalWinterDays: 12,
    light: 'full-sun',
    potSize: 'large',
    containerLiters: 70,
    plantCount: 3,
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

function flatSnapshot(now: Date, values: Partial<DailyWeather>): WeatherSnapshot {
  const days: DailyWeather[] = [];
  for (let offset = -3; offset <= 6; offset += 1) {
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    date.setDate(date.getDate() + offset);
    days.push({
      date: toDateKey(date),
      rainMm: 0,
      rainChance: 0,
      et0Mm: 5.5,
      maxTempC: 28,
      ...values,
    });
  }
  return {
    fetchedAt: now.toISOString(),
    latitude: 32.08,
    longitude: 34.78,
    timezone: 'Asia/Jerusalem',
    days,
  };
}

describe('crowdingFactor', () => {
  it('leaves a lone plant exactly as stated', () => {
    expect(crowdingFactor(1)).toBe(1);
  });

  it('shortens the interval as more plants share the soil', () => {
    expect(crowdingFactor(3)).toBeCloseTo(0.577, 3);
    expect(crowdingFactor(4)).toBe(0.5);
  });

  it('is damped rather than proportional', () => {
    // Three plants do not empty the planter three times as fast.
    expect(crowdingFactor(3)).toBeGreaterThan(1 / 3);
  });

  it('treats a missing or nonsensical count as one plant', () => {
    expect(crowdingFactor(0)).toBe(1);
    expect(crowdingFactor(Number.NaN)).toBe(1);
  });
});

describe('baseIntervalDays', () => {
  const summer = at(2026, 7, 15);
  const winter = at(2026, 12, 15);

  it('turns three cypresses in one planter from five days into three', () => {
    expect(seasonalIntervalDays(makePlant(), summer)).toBe(5);
    expect(baseIntervalDays(makePlant(), summer)).toBe(3);
  });

  it('applies crowding in winter too', () => {
    expect(seasonalIntervalDays(makePlant(), winter)).toBe(12);
    expect(baseIntervalDays(makePlant(), winter)).toBe(7);
  });

  it('leaves a single plant on its stated interval', () => {
    expect(baseIntervalDays(makePlant({ plantCount: 1 }), summer)).toBe(5);
  });

  it('never drops below one day', () => {
    const crowded = makePlant({ intervalSummerDays: 1, plantCount: 9 });
    expect(baseIntervalDays(crowded, summer)).toBe(1);
  });
});

describe('intervalDays with a forecast', () => {
  const summer = at(2026, 7, 15);

  it('matches the base interval in ordinary weather', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 5.5 });
    expect(intervalDays(makePlant(), summer, snapshot)).toBe(
      baseIntervalDays(makePlant(), summer),
    );
  });

  it('stretches after rain', () => {
    const snapshot = flatSnapshot(summer, { rainMm: 0 });
    snapshot.days[2].rainMm = 20; // yesterday
    const withRain = intervalDays(makePlant(), summer, snapshot);
    expect(withRain).toBeGreaterThan(baseIntervalDays(makePlant(), summer));
  });

  it('ignores the forecast for an indoor plant', () => {
    const indoor = makePlant({ isOutdoor: false, plantCount: 1 });
    const snapshot = flatSnapshot(summer, { rainMm: 40, et0Mm: 1 });
    expect(intervalDays(indoor, summer, snapshot)).toBe(
      baseIntervalDays(indoor, summer),
    );
  });

  it('falls back to the base interval with no snapshot', () => {
    expect(intervalDays(makePlant(), summer, null)).toBe(
      baseIntervalDays(makePlant(), summer),
    );
  });

  it('never returns less than a day in extreme heat', () => {
    const snapshot = flatSnapshot(summer, { et0Mm: 60, maxTempC: 50 });
    expect(intervalDays(makePlant(), summer, snapshot)).toBeGreaterThanOrEqual(1);
  });
});

describe('suggestWaterForContainer', () => {
  it('gives about 15% of the substrate volume', () => {
    expect(suggestWaterForContainer(70)).toBe(10500);
    expect(suggestWaterForContainer(30)).toBe(4500);
    expect(suggestWaterForContainer(60)).toBe(9000);
  });

  it('respects a plant-specific ratio', () => {
    // Bamboo wants more per litre of soil than a lavender does.
    expect(suggestWaterForContainer(30, 200)).toBe(6000);
    expect(suggestWaterForContainer(30, 110)).toBe(3300);
  });

  it('rounds to a round number of hundreds of millilitres', () => {
    expect(suggestWaterForContainer(7) % 100).toBe(0);
  });

  it('returns nothing for a volume that makes no sense', () => {
    expect(suggestWaterForContainer(0)).toBe(0);
    expect(suggestWaterForContainer(-5)).toBe(0);
  });

  it('never suggests less than 100 ml for a real container', () => {
    expect(suggestWaterForContainer(0.1)).toBe(100);
  });
});

describe('containerLitersFor', () => {
  it('prefers the measured volume', () => {
    expect(containerLitersFor(makePlant({ containerLiters: 70 }))).toBe(70);
  });

  it('falls back to the pot-size bucket', () => {
    expect(containerLitersFor(makePlant({ containerLiters: null, potSize: 'small' }))).toBe(2);
    expect(containerLitersFor(makePlant({ containerLiters: 0, potSize: 'large' }))).toBe(20);
  });
});
