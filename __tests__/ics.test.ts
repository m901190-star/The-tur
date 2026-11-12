import {
  buildIcs,
  escapeText,
  firstOccurrence,
  foldLine,
  formatLocalDateTime,
} from '../src/lib/ics';
import { Plant } from '../src/types';

function makePlant(overrides: Partial<Plant> = {}): Plant {
  return {
    id: 'abc123',
    name: 'הפיקוס של הסלון',
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

function at(year: number, month: number, day: number, hour = 12): Date {
  return new Date(year, month - 1, day, hour, 0, 0, 0);
}

describe('escapeText', () => {
  it('escapes the characters iCalendar treats as structure', () => {
    expect(escapeText('a;b,c\\d')).toBe('a\;b\\,c\\\\d');
  });

  it('turns newlines into the literal \\n sequence', () => {
    expect(escapeText('line one\nline two')).toBe('line one\\nline two');
  });
});

describe('foldLine', () => {
  it('leaves a short line alone', () => {
    expect(foldLine('SUMMARY:hello')).toBe('SUMMARY:hello');
  });

  it('folds a long ASCII line with a leading space on continuations', () => {
    const folded = foldLine(`SUMMARY:${'x'.repeat(200)}`);
    const lines = folded.split('\r\n');
    expect(lines.length).toBeGreaterThan(1);
    for (const line of lines.slice(1)) {
      expect(line.startsWith(' ')).toBe(true);
    }
  });

  it('keeps every line within 75 octets', () => {
    const folded = foldLine(`DESCRIPTION:${'השקיית עציצים בסלון '.repeat(12)}`);
    for (const line of folded.split('\r\n')) {
      expect(Buffer.byteLength(line, 'utf8')).toBeLessThanOrEqual(75);
    }
  });

  it('does not split a Hebrew character in half', () => {
    const source = `DESCRIPTION:${'ש'.repeat(120)}`;
    const folded = foldLine(source);
    const rebuilt = folded.split('\r\n ').join('');
    expect(rebuilt).toBe(source);
  });
});

describe('formatLocalDateTime', () => {
  it('emits a floating local timestamp', () => {
    expect(formatLocalDateTime(at(2026, 11, 12, 8))).toBe('20261112T080000');
  });
});

describe('firstOccurrence', () => {
  it('starts on the due day at the reminder hour', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 10).toISOString() });
    const start = firstOccurrence(plant, 8, at(2026, 7, 15));
    expect(start.getDate()).toBe(17);
    expect(start.getHours()).toBe(8);
  });

  it('starts today when the plant was never watered', () => {
    const start = firstOccurrence(makePlant(), 9, at(2026, 7, 15));
    expect(start.getDate()).toBe(15);
    expect(start.getHours()).toBe(9);
  });

  it('does not place the first reminder in the past', () => {
    const plant = makePlant({ lastWateredAt: at(2026, 7, 1).toISOString() });
    const now = at(2026, 7, 15);
    const start = firstOccurrence(plant, 8, now);
    expect(start.getDate()).toBe(15);
  });
});

describe('buildIcs', () => {
  const now = at(2026, 7, 15);

  it('wraps the events in a calendar with CRLF line endings', () => {
    const ics = buildIcs([makePlant()], { reminderHour: 8, now });
    expect(ics.startsWith('BEGIN:VCALENDAR\r\n')).toBe(true);
    expect(ics.trimEnd().endsWith('END:VCALENDAR')).toBe(true);
    expect(ics.includes('\n\n')).toBe(false);
  });

  it('writes one event per plant with a stable UID', () => {
    const ics = buildIcs([makePlant({ id: 'one' }), makePlant({ id: 'two' })], {
      reminderHour: 8,
      now,
    });
    expect(ics.match(/BEGIN:VEVENT/g)).toHaveLength(2);
    expect(ics).toContain('UID:plant-one@tur-watering');
    expect(ics).toContain('UID:plant-two@tur-watering');
  });

  it('uses the seasonal interval in the recurrence rule', () => {
    const summer = buildIcs([makePlant()], { reminderHour: 8, now });
    expect(summer).toContain('RRULE:FREQ=DAILY;INTERVAL=7');

    const winter = buildIcs([makePlant()], { reminderHour: 8, now: at(2026, 12, 15) });
    expect(winter).toContain('RRULE:FREQ=DAILY;INTERVAL=14');
  });

  it('includes a display alarm at the start of the event', () => {
    const ics = buildIcs([makePlant()], { reminderHour: 8, now });
    expect(ics).toContain('BEGIN:VALARM');
    expect(ics).toContain('TRIGGER:PT0S');
  });

  it('clamps an out-of-range reminder hour', () => {
    const ics = buildIcs([makePlant()], { reminderHour: 99, now });
    expect(ics).toContain('T230000');
  });

  it('omits LOCATION when the plant has no location', () => {
    const ics = buildIcs([makePlant({ location: '  ' })], { reminderHour: 8, now });
    expect(ics).not.toContain('LOCATION:');
  });

  it('produces an empty but valid calendar for no plants', () => {
    const ics = buildIcs([], { reminderHour: 8, now });
    expect(ics).toContain('BEGIN:VCALENDAR');
    expect(ics).not.toContain('BEGIN:VEVENT');
  });
});
