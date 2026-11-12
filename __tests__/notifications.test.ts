import { SCHEDULE_HORIZON_DAYS, planNotifications } from '../src/lib/notificationPlan';
import { DEFAULT_SETTINGS, Plant, Settings } from '../src/types';

function at(year: number, month: number, day: number, hour = 12): Date {
  return new Date(year, month - 1, day, hour, 0, 0, 0);
}

function makePlant(overrides: Partial<Plant> = {}): Plant {
  return {
    id: 'p1',
    name: 'הברושים',
    species: 'ברוש',
    location: 'חצר',
    waterMl: 10000,
    intervalSummerDays: 6,
    intervalWinterDays: 12,
    light: 'full-sun',
    potSize: 'large',
    containerLiters: 70,
    plantCount: 1,
    isOutdoor: true,
    isFrostTender: true,
    keepsDryInCold: false,
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

const ON: Settings = { ...DEFAULT_SETTINGS, notificationsEnabled: true, reminderHour: 8 };

describe('planNotifications', () => {
  // Morning of the 15th, before the 08:00 slot has passed.
  const earlyMorning = at(2026, 7, 15, 6);
  // Afternoon, so today's slot is already behind us.
  const afternoon = at(2026, 7, 15, 14);

  it('plans nothing while notifications are switched off', () => {
    expect(planNotifications([makePlant()], DEFAULT_SETTINGS, earlyMorning)).toEqual([]);
  });

  it('plans nothing without plants', () => {
    expect(planNotifications([], ON, earlyMorning)).toEqual([]);
  });

  it('fires at the chosen hour', () => {
    const planned = planNotifications([makePlant()], ON, earlyMorning);
    expect(planned[0].fireAt.getHours()).toBe(8);
    expect(planned[0].fireAt.getMinutes()).toBe(0);
  });

  it('skips a slot that has already passed today', () => {
    const planned = planNotifications([makePlant()], ON, afternoon);
    expect(planned[0].fireAt.getDate()).toBe(16);
  });

  it('reminds today about a plant that was never watered', () => {
    const planned = planNotifications([makePlant()], ON, earlyMorning);
    expect(planned[0].fireAt.getDate()).toBe(15);
    expect(planned[0].plantIds).toEqual(['p1']);
  });

  it('reminds on the due day for a watered plant', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 14).toISOString() });
    const planned = planNotifications([plant], ON, earlyMorning);
    // Watered on the 14th with a six-day interval: due the 20th.
    expect(planned[0].fireAt.getDate()).toBe(20);
  });

  it('treats an overdue plant as due today', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 1).toISOString() });
    const planned = planNotifications([plant], ON, earlyMorning);
    expect(planned[0].fireAt.getDate()).toBe(15);
  });

  it('groups the plants due on the same day into one notification', () => {
    const plants = [
      makePlant({ id: 'a', name: 'הברושים', waterMl: 10000 }),
      makePlant({ id: 'b', name: 'הלימון', waterMl: 14000 }),
      makePlant({ id: 'c', name: 'הבמבוק', waterMl: 6000 }),
    ];
    const planned = planNotifications(plants, ON, earlyMorning);
    const today = planned[0];
    expect(today.plantIds).toEqual(['a', 'b', 'c']);
    expect(today.title).toBe('3 עציצים צריכים מים');
    expect(today.body).toContain('הברושים');
    // 10 + 14 + 6 litres.
    expect(today.body).toContain('30 ליטר');
  });

  it('names at most three plants and counts the rest', () => {
    const plants = ['a', 'b', 'c', 'd', 'e'].map((id) =>
      makePlant({ id, name: `עציץ ${id}` }),
    );
    const planned = planNotifications(plants, ON, earlyMorning);
    expect(planned[0].body).toContain('ועוד 2');
  });

  it('uses the singular title for a lone plant', () => {
    expect(planNotifications([makePlant()], ON, earlyMorning)[0].title).toBe('זמן להשקות');
  });

  it('repeats on the plant own rhythm, not every day', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 14).toISOString() });
    const planned = planNotifications([plant], ON, earlyMorning);
    // Due on the 20th, then nudged every six days while it stays unwatered.
    expect(planned[0].fireAt.getDate()).toBe(20);
    const gaps = planned
      .slice(1)
      .map((item, index) =>
        Math.round(
          (item.fireAt.getTime() - planned[index].fireAt.getTime()) /
            (24 * 60 * 60 * 1000),
        ),
      );
    expect(gaps.every((gap) => gap === 6)).toBe(true);
    expect(gaps.length).toBeGreaterThan(0);
  });

  it('stays inside the scheduling horizon', () => {
    const plant = makePlant({ intervalSummerDays: 1, intervalWinterDays: 1 });
    const planned = planNotifications([plant], ON, earlyMorning);
    const last = planned[planned.length - 1];
    const daysOut = Math.round(
      (last.fireAt.getTime() - earlyMorning.getTime()) / (24 * 60 * 60 * 1000),
    );
    expect(daysOut).toBeLessThanOrEqual(SCHEDULE_HORIZON_DAYS);
  });

  it('caps how many notifications it queues at once', () => {
    const plants = Array.from({ length: 60 }, (_, index) =>
      makePlant({ id: `p${index}`, intervalSummerDays: 1, intervalWinterDays: 1 }),
    );
    const planned = planNotifications(plants, ON, earlyMorning);
    // Well inside the 64 pending notifications iOS allows an app.
    expect(planned.length).toBeLessThanOrEqual(32);
    expect(planned.length).toBeGreaterThan(20);
  });

  it('covers long enough that a fortnight away does not silence it', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 14).toISOString() });
    const planned = planNotifications([plant], ON, earlyMorning);
    const last = planned[planned.length - 1];
    const daysOut = Math.round(
      (last.fireAt.getTime() - earlyMorning.getTime()) / (24 * 60 * 60 * 1000),
    );
    expect(daysOut).toBeGreaterThan(14);
  });

  it('honours a reminder hour the user moved to the evening', () => {
    const evening: Settings = { ...ON, reminderHour: 19 };
    expect(planNotifications([makePlant()], evening, afternoon)[0].fireAt.getHours()).toBe(
      19,
    );
  });

  it('clamps a nonsensical reminder hour', () => {
    const broken: Settings = { ...ON, reminderHour: 99 };
    expect(planNotifications([makePlant()], broken, earlyMorning)[0].fireAt.getHours()).toBe(
      23,
    );
  });
});
