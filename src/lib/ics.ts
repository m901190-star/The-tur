import { Plant } from '../types';
import { formatWater, intervalDays, nextWateringDate, startOfDay } from './watering';

/** UTF-8 byte length of a single code point. */
function byteLength(char: string): number {
  const code = char.codePointAt(0) ?? 0;
  if (code < 0x80) return 1;
  if (code < 0x800) return 2;
  if (code < 0x10000) return 3;
  return 4;
}

/**
 * RFC 5545 line folding: no line may exceed 75 octets, continuations start with
 * a single space. Folds on code-point boundaries so Hebrew text stays intact.
 */
export function foldLine(line: string): string {
  const limit = 73;
  const out: string[] = [];
  let current = '';
  let bytes = 0;
  for (const char of line) {
    const size = byteLength(char);
    if (bytes + size > limit) {
      out.push(current);
      current = char;
      bytes = size + 1; // the leading space of a continuation line
    } else {
      current += char;
      bytes += size;
    }
  }
  out.push(current);
  return out.join('\r\n ');
}

/** Escapes a value for a TEXT-typed iCalendar property. */
export function escapeText(value: string): string {
  return value
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\;')
    .replace(/,/g, '\\,')
    .replace(/\r?\n/g, '\\n');
}

function pad(value: number, width = 2): string {
  return String(value).padStart(width, '0');
}

/** Floating local date-time, e.g. 20261112T080000. Deliberately without a zone
 *  so the reminder fires at 08:00 wherever the user happens to be. */
export function formatLocalDateTime(date: Date): string {
  return (
    `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}` +
    `T${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
  );
}

export function formatUtcStamp(date: Date): string {
  return (
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
    `T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}Z`
  );
}

export interface IcsOptions {
  /** Hour of day the reminder should fire. */
  reminderHour: number;
  /** "Now", used for DTSTAMP and for plants that were never watered. */
  now?: Date;
}

export function eventTitle(plant: Plant): string {
  const label = plant.name.trim() || plant.species.trim() || 'עציץ';
  return `להשקות: ${label}`;
}

export function eventDescription(plant: Plant, now: Date): string {
  const lines = [
    `כמות מים: ${formatWater(plant.waterMl)}`,
    `תדירות עכשווית: כל ${intervalDays(plant, now)} ימים`,
  ];
  if (plant.species.trim()) lines.push(`סוג: ${plant.species.trim()}`);
  if (plant.notes.trim()) lines.push(`הערות: ${plant.notes.trim()}`);
  return lines.join('\n');
}

/** First occurrence of the reminder for this plant. */
export function firstOccurrence(plant: Plant, reminderHour: number, now: Date): Date {
  const due = nextWateringDate(plant, now) ?? startOfDay(now);
  const start = startOfDay(due);
  start.setHours(reminderHour, 0, 0, 0);
  // A due day that has already passed should not create history in the calendar;
  // start the series today instead.
  const today = startOfDay(now);
  if (start.getTime() < today.getTime()) {
    const todayStart = new Date(today);
    todayStart.setHours(reminderHour, 0, 0, 0);
    return todayStart;
  }
  return start;
}

/**
 * Builds an .ics file holding one recurring all-plants-included event per plant.
 * Importing it into Google Calendar creates the whole watering schedule at once.
 */
export function buildIcs(plants: Plant[], options: IcsOptions): string {
  const now = options.now ?? new Date();
  const hour = Math.min(23, Math.max(0, Math.round(options.reminderHour)));
  const stamp = formatUtcStamp(now);

  const lines: string[] = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//tur-watering//plant watering//HE',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    `X-WR-CALNAME:${escapeText('השקיית עציצים')}`,
  ];

  for (const plant of plants) {
    const start = firstOccurrence(plant, hour, now);
    const end = new Date(start.getTime() + 15 * 60 * 1000);
    lines.push(
      'BEGIN:VEVENT',
      `UID:plant-${plant.id}@tur-watering`,
      `DTSTAMP:${stamp}`,
      `DTSTART:${formatLocalDateTime(start)}`,
      `DTEND:${formatLocalDateTime(end)}`,
      `RRULE:FREQ=DAILY;INTERVAL=${intervalDays(plant, now)}`,
      `SUMMARY:${escapeText(eventTitle(plant))}`,
      `DESCRIPTION:${escapeText(eventDescription(plant, now))}`,
    );
    if (plant.location.trim()) {
      lines.push(`LOCATION:${escapeText(plant.location.trim())}`);
    }
    lines.push(
      'BEGIN:VALARM',
      'ACTION:DISPLAY',
      'TRIGGER:PT0S',
      `DESCRIPTION:${escapeText(eventTitle(plant))}`,
      'END:VALARM',
      'END:VEVENT',
    );
  }

  lines.push('END:VCALENDAR');
  return `${lines.map(foldLine).join('\r\n')}\r\n`;
}
