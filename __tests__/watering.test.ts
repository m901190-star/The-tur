import {
  addDays,
  compareByUrgency,
  daysBetween,
  fertilizeState,
  formatWater,
  intervalDays,
  needsWaterNow,
  nextWateringDate,
  seasonForDate,
  sortByUrgency,
  startOfDay,
  totalWaterDue,
  wateringState,
} from '../src/lib/watering';
import { Plant } from '../src/types';

function makePlant(overrides: Partial<Plant> = {}): Plant {
  return {
    id: 'p1',
    name: 'פיקוס',
    species: "פיקוס בנג'מינה",
    location: 'סלון',
    waterMl: 600,
    intervalSummerDays: 7,
    intervalWinterDays: 14,
    light: 'partial',
    potSize: 'large',
    containerLiters: null,
    plantCount: 1,
    isOutdoor: false,
    isFrostTender: false,
    keepsDryInCold: false,
    fertilizeEveryDays: 30,
    lastWateredAt: null,
    lastFertilizedAt: null,
    photoUri: null,
    notes: '',
    createdAt: '2026-01-01T00:00:00.000Z',
    calendarEventId: null,
    ...overrides,
  };
}

/** Local-time date, so the tests do not depend on the runner's time zone. */
function at(year: number, month: number, day: number, hour = 12): Date {
  return new Date(year, month - 1, day, hour, 0, 0, 0);
}

describe('date helpers', () => {
  it('startOfDay strips the time', () => {
    const start = startOfDay(at(2026, 7, 14, 23));
    expect(start.getHours()).toBe(0);
    expect(start.getDate()).toBe(14);
  });

  it('daysBetween counts whole calendar days and signs them', () => {
    expect(daysBetween(at(2026, 7, 14), at(2026, 7, 17))).toBe(3);
    expect(daysBetween(at(2026, 7, 17), at(2026, 7, 14))).toBe(-3);
    expect(daysBetween(at(2026, 7, 14, 1), at(2026, 7, 14, 23))).toBe(0);
  });

  it('daysBetween survives a DST shift', () => {
    // Israel moves the clock in late March and late October.
    expect(daysBetween(at(2026, 3, 25), at(2026, 4, 1))).toBe(7);
    expect(daysBetween(at(2026, 10, 20), at(2026, 11, 3))).toBe(14);
  });

  it('addDays rolls over month boundaries', () => {
    const result = addDays(at(2026, 1, 30), 3);
    expect(result.getMonth()).toBe(1);
    expect(result.getDate()).toBe(2);
  });
});

describe('seasonForDate', () => {
  it('treats April through October as summer', () => {
    expect(seasonForDate(at(2026, 4, 1))).toBe('summer');
    expect(seasonForDate(at(2026, 7, 15))).toBe('summer');
    expect(seasonForDate(at(2026, 10, 31))).toBe('summer');
  });

  it('treats November through March as winter', () => {
    expect(seasonForDate(at(2026, 11, 1))).toBe('winter');
    expect(seasonForDate(at(2027, 1, 20))).toBe('winter');
    expect(seasonForDate(at(2027, 3, 31))).toBe('winter');
  });
});

describe('intervalDays', () => {
  it('picks the seasonal interval', () => {
    const plant = makePlant();
    expect(intervalDays(plant, at(2026, 7, 1))).toBe(7);
    expect(intervalDays(plant, at(2026, 12, 1))).toBe(14);
  });

  it('falls back to the other season when one is missing', () => {
    const plant = makePlant({ intervalWinterDays: 0 });
    expect(intervalDays(plant, at(2026, 12, 1))).toBe(7);
  });

  it('never returns less than one day', () => {
    const plant = makePlant({ intervalSummerDays: 0, intervalWinterDays: 0 });
    expect(intervalDays(plant, at(2026, 7, 1))).toBe(7);
  });
});

describe('nextWateringDate', () => {
  it('is null for a plant that was never watered', () => {
    expect(nextWateringDate(makePlant(), at(2026, 7, 1))).toBeNull();
  });

  it('adds the seasonal interval to the last watering', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 1, 9).toISOString() });
    const next = nextWateringDate(plant, at(2026, 7, 3))!;
    expect(daysBetween(at(2026, 7, 1), next)).toBe(7);
  });

  it('ignores a corrupt stored date', () => {
    const plant = makePlant({ lastWateredAt: 'not-a-date' });
    expect(nextWateringDate(plant, at(2026, 7, 1))).toBeNull();
  });
});

describe('wateringState', () => {
  const now = at(2026, 7, 15);

  it('reports never for an unwatered plant', () => {
    expect(wateringState(makePlant(), now).status).toBe('never');
  });

  it('reports today on the due day', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 8).toISOString() });
    const state = wateringState(plant, now);
    expect(state.status).toBe('today');
    expect(state.daysUntil).toBe(0);
  });

  it('reports overdue with a negative count', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 5).toISOString() });
    const state = wateringState(plant, now);
    expect(state.status).toBe('overdue');
    expect(state.daysUntil).toBe(-3);
  });

  it('reports soon the day before', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 9).toISOString() });
    expect(wateringState(plant, now).status).toBe('soon');
  });

  it('reports ok further out', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 14).toISOString() });
    const state = wateringState(plant, now);
    expect(state.status).toBe('ok');
    expect(state.daysUntil).toBe(6);
  });

  it('counts days since the last watering', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 10).toISOString() });
    expect(wateringState(plant, now).daysSinceWatering).toBe(5);
  });
});

describe('needsWaterNow', () => {
  const now = at(2026, 7, 15);

  it('includes overdue, due-today and never-watered plants', () => {
    expect(needsWaterNow(makePlant(), now)).toBe(true);
    expect(
      needsWaterNow(makePlant({ lastWateredAt: at(2026, 7, 8).toISOString() }), now),
    ).toBe(true);
    expect(
      needsWaterNow(makePlant({ lastWateredAt: at(2026, 7, 1).toISOString() }), now),
    ).toBe(true);
  });

  it('excludes plants due tomorrow or later', () => {
    expect(
      needsWaterNow(makePlant({ lastWateredAt: at(2026, 7, 9).toISOString() }), now),
    ).toBe(false);
  });
});

describe('sorting', () => {
  const now = at(2026, 7, 15);

  it('puts the most overdue plant first and the relaxed one last', () => {
    const veryLate = makePlant({ id: 'a', lastWateredAt: at(2026, 7, 1).toISOString() });
    const late = makePlant({ id: 'b', lastWateredAt: at(2026, 7, 6).toISOString() });
    const dueToday = makePlant({ id: 'c', lastWateredAt: at(2026, 7, 8).toISOString() });
    const never = makePlant({ id: 'd' });
    const relaxed = makePlant({ id: 'e', lastWateredAt: at(2026, 7, 14).toISOString() });

    const order = sortByUrgency([relaxed, never, dueToday, late, veryLate], now).map(
      (plant) => plant.id,
    );
    expect(order).toEqual(['a', 'b', 'c', 'd', 'e']);
  });

  it('does not mutate the input array', () => {
    const plants = [
      makePlant({ id: 'x', lastWateredAt: at(2026, 7, 14).toISOString() }),
      makePlant({ id: 'y', lastWateredAt: at(2026, 7, 1).toISOString() }),
    ];
    sortByUrgency(plants, now);
    expect(plants.map((plant) => plant.id)).toEqual(['x', 'y']);
  });

  it('breaks ties by name', () => {
    const first = makePlant({ id: '1', name: 'אלוורה' });
    const second = makePlant({ id: '2', name: 'תמר' });
    expect(compareByUrgency(first, second, now)).toBeLessThan(0);
  });
});

describe('fertilizeState', () => {
  const now = at(2026, 7, 15);

  it('is untracked when the plant is not fertilised', () => {
    const state = fertilizeState(makePlant({ fertilizeEveryDays: null }), now);
    expect(state.tracked).toBe(false);
    expect(state.due).toBe(false);
  });

  it('is due when it was never fertilised', () => {
    expect(fertilizeState(makePlant(), now).due).toBe(true);
  });

  it('is due once the interval has passed', () => {
    const plant = makePlant({ lastFertilizedAt: at(2026, 6, 10).toISOString() });
    expect(fertilizeState(plant, now).due).toBe(true);
  });

  it('is not due inside the interval', () => {
    const plant = makePlant({ lastFertilizedAt: at(2026, 7, 10).toISOString() });
    const state = fertilizeState(plant, now);
    expect(state.due).toBe(false);
    expect(state.daysUntil).toBe(25);
  });
});

describe('totalWaterDue', () => {
  it('adds up only the plants that need water now', () => {
    const now = at(2026, 7, 15);
    const plants = [
      makePlant({ id: 'a', waterMl: 500, lastWateredAt: at(2026, 7, 1).toISOString() }),
      makePlant({ id: 'b', waterMl: 300, lastWateredAt: at(2026, 7, 8).toISOString() }),
      makePlant({ id: 'c', waterMl: 900, lastWateredAt: at(2026, 7, 14).toISOString() }),
    ];
    expect(totalWaterDue(plants, now)).toBe(800);
  });
});

describe('formatWater', () => {
  it('uses millilitres below a litre', () => {
    expect(formatWater(350)).toBe('350 מ״ל');
  });

  it('switches to litres at a litre and rounds to one decimal', () => {
    expect(formatWater(1000)).toBe('1 ליטר');
    expect(formatWater(1250)).toBe('1.3 ליטר');
  });
});
