import * as Calendar from 'expo-calendar';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Platform } from 'react-native';

import { Plant, Settings } from '../types';
import { errorCodeOf, useMcp } from './claudeRuntime';
import { buildIcs, eventDescription, eventTitle, firstOccurrence } from './ics';
import { IS_WEB } from './platform';
import { intervalDays } from './watering';

export interface CalendarOption {
  id: string;
  title: string;
  /** Account the calendar belongs to, e.g. a gmail address. */
  source: string;
  /** True when this calendar is backed by a Google account. */
  isGoogle: boolean;
}

export async function requestCalendarAccess(): Promise<boolean> {
  const { status } = await Calendar.requestCalendarPermissionsAsync();
  return status === 'granted';
}

export async function hasCalendarAccess(): Promise<boolean> {
  try {
    const { status } = await Calendar.getCalendarPermissionsAsync();
    return status === 'granted';
  } catch {
    return false;
  }
}

function looksLikeGoogle(source: string, title: string): boolean {
  const haystack = `${source} ${title}`.toLowerCase();
  return (
    haystack.includes('google') ||
    haystack.includes('gmail') ||
    haystack.includes('@gmail.') ||
    haystack.includes('googlemail')
  );
}

/**
 * Calendars we may write to. On both platforms a Google account added to the
 * device shows up here, which is how a reminder lands in Google Calendar
 * without the app ever holding an OAuth token.
 */
export async function listWritableCalendars(): Promise<CalendarOption[]> {
  // The namespace import shadows expo-calendar's own `Calendar` type, so take
  // the element type straight off the function.
  let calendars: Awaited<ReturnType<typeof Calendar.getCalendarsAsync>> = [];
  try {
    calendars = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
  } catch {
    return [];
  }
  return calendars
    .filter((calendar) => calendar.allowsModifications)
    .map((calendar) => {
      const source =
        typeof calendar.source === 'string'
          ? calendar.source
          : (calendar.source?.name ?? '');
      return {
        id: calendar.id,
        title: calendar.title,
        source,
        isGoogle: looksLikeGoogle(source, calendar.title),
      };
    })
    .sort((a, b) => Number(b.isGoogle) - Number(a.isGoogle));
}

/** The Google calendar if there is one, otherwise the device default. */
export async function suggestCalendar(): Promise<CalendarOption | null> {
  const options = await listWritableCalendars();
  if (options.length === 0) return null;
  return options.find((option) => option.isGoogle) ?? options[0];
}

interface EventDetails {
  title: string;
  startDate: Date;
  endDate: Date;
  notes: string;
  location: string;
  recurrenceRule: Calendar.RecurrenceRule;
  alarms: Calendar.Alarm[];
  timeZone?: string;
}

function detailsFor(plant: Plant, settings: Settings, now: Date): EventDetails {
  const start = firstOccurrence(plant, settings.reminderHour, now);
  return {
    title: eventTitle(plant),
    startDate: start,
    endDate: new Date(start.getTime() + 15 * 60 * 1000),
    notes: eventDescription(plant, now),
    location: plant.location.trim(),
    recurrenceRule: {
      frequency: Calendar.Frequency.DAILY,
      interval: intervalDays(plant, now),
    },
    alarms: [{ relativeOffset: 0 }],
  };
}

/**
 * Creates or updates this plant's recurring reminder and returns the event id.
 * The id is stored on the plant so later edits move the same event rather than
 * piling duplicates into the calendar.
 */
export async function upsertPlantEvent(
  plant: Plant,
  settings: Settings,
  now: Date = new Date(),
): Promise<string> {
  if (!settings.calendarId) {
    throw new Error('לא נבחר יומן');
  }
  const details = detailsFor(plant, settings, now);

  if (plant.calendarEventId) {
    try {
      await Calendar.updateEventAsync(plant.calendarEventId, details, {
        futureEvents: true,
      });
      return plant.calendarEventId;
    } catch {
      // The event was deleted in the calendar app — fall through and recreate it.
    }
  }

  return Calendar.createEventAsync(settings.calendarId, details);
}

export async function deletePlantEvent(plant: Plant): Promise<void> {
  if (!plant.calendarEventId) return;
  try {
    await Calendar.deleteEventAsync(plant.calendarEventId, { futureEvents: true });
  } catch {
    // Already gone. Nothing to do.
  }
}

export interface SyncResult {
  synced: number;
  failed: number;
  /** Plant id -> calendar event id, for the plants that synced. */
  eventIds: Record<string, string>;
}

export async function syncAllPlants(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
): Promise<SyncResult> {
  const result: SyncResult = { synced: 0, failed: 0, eventIds: {} };
  for (const plant of plants) {
    try {
      result.eventIds[plant.id] = await upsertPlantEvent(plant, settings, now);
      result.synced += 1;
    } catch {
      result.failed += 1;
    }
  }
  return result;
}

/**
 * Hands the browser the .ics as a download.
 *
 * On the web build this is not a convenience, it is the whole reminder
 * mechanism: a page cannot schedule notifications in the background on iOS, so
 * the schedule has to leave the app and live in the phone's own calendar.
 * Opening the downloaded file on an iPhone offers to add the events, alerts and
 * all.
 */
function downloadIcsInBrowser(contents: string): string {
  const blob = new Blob([`\ufeff${contents}`], {
    type: 'text/calendar;charset=utf-8',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'plant-watering.ics';
  document.body.appendChild(link);
  link.click();
  link.remove();
  // Give the browser a moment to start the download before revoking.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
  return url;
}

/**
 * Writes an .ics file and opens the share sheet, so the schedule can be imported
 * into Google Calendar on the web or sent to someone watering for you.
 */
export async function shareIcsFile(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
): Promise<string> {
  const contents = buildIcs(plants, { reminderHour: settings.reminderHour, now });

  if (IS_WEB) {
    return downloadIcsInBrowser(contents);
  }

  const directory = FileSystem.Paths.cache;
  const file = new FileSystem.File(directory, 'plant-watering.ics');
  if (file.exists) file.delete();
  file.create();
  file.write(contents);

  if (!IS_WEB && (await Sharing.isAvailableAsync())) {
    await Sharing.shareAsync(file.uri, {
      mimeType: 'text/calendar',
      dialogTitle: 'ייצוא לוח ההשקיה',
      UTI: 'com.apple.ical.ics',
    });
  }
  return file.uri;
}


/** The connector's display name, which is also how a page addresses it. */
const GOOGLE_CALENDAR = 'Google Calendar';

function pad(value: number): string {
  return String(value).padStart(2, '0');
}

/** Local time with no offset, which is what the connector asks for. */
function localIso(date: Date): string {
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}:00`
  );
}

export interface CalendarPushResult {
  created: number;
  failed: number;
  /** Null when the whole run succeeded; otherwise what to tell the user. */
  problem: string | null;
  /** True when this page cannot reach the connector at all. */
  unavailable: boolean;
}

/** What each failure code means for someone trying to get reminders working. */
function explain(code: string): string {
  switch (code) {
    case 'server_not_connected':
      return 'יומן Google לא מחובר. אפשר לחבר אותו בהגדרות של claude.ai, תחת Connectors, ואז לנסות שוב.';
    case 'needs_reauth':
      return 'החיבור ליומן Google פג. יש להתחבר מחדש בהגדרות של claude.ai, תחת Connectors.';
    case 'selection_required':
      return 'יש כמה חשבונות Google מחוברים. בחר אחד מהם כשתישאל, ואז נסה שוב.';
    case 'not_in_manifest':
    case 'approval_required':
      return 'הגישה ליומן לא אושרה לדף הזה. אשר אותה כשתישאל, ואז נסה שוב.';
    case 'blocked_by_policy':
      return 'מדיניות הארגון חוסמת כתיבה ליומן מהדף הזה.';
    case 'server_unavailable':
    case 'rate_limited':
      return 'יומן Google לא זמין כרגע. כדאי לנסות שוב בעוד רגע.';
    default:
      return 'הכתיבה ליומן נכשלה. כדאי לנסות שוב.';
  }
}

/**
 * Writes one recurring event per plant straight into the viewer's Google
 * Calendar, which is how reminders reach a phone from a page that cannot
 * schedule notifications itself. Each event carries the plant's own interval
 * as an RRULE and a popup alert, so the schedule keeps running without the
 * page being open.
 *
 * Call this only from a deliberate tap: it writes, and a second tap writes the
 * events again.
 */
export async function pushToGoogleCalendar(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
): Promise<CalendarPushResult> {
  const mcp = await useMcp();
  if (!mcp) {
    return { created: 0, failed: 0, problem: null, unavailable: true };
  }

  let created = 0;
  let failed = 0;
  let problem: string | null = null;

  for (const plant of plants) {
    const start = firstOccurrence(plant, settings.reminderHour, now);
    const end = new Date(start.getTime() + 15 * 60 * 1000);
    try {
      await mcp.callTool(GOOGLE_CALENDAR, 'create_event', {
        summary: eventTitle(plant),
        description: eventDescription(plant, now),
        startTime: localIso(start),
        endTime: localIso(end),
        recurrenceData: [`RRULE:FREQ=DAILY;INTERVAL=${intervalDays(plant, now)}`],
        overrideReminders: [{ method: 'popup', minutes: 0 }],
        ...(plant.location.trim() ? { location: plant.location.trim() } : {}),
      });
      created += 1;
    } catch (error) {
      failed += 1;
      // Keep the first explanation: later plants usually fail the same way,
      // and the first code is the one that names the fix.
      problem = problem ?? explain(errorCodeOf(error));
    }
  }

  return { created, failed, problem, unavailable: false };
}
