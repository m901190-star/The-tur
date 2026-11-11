import * as Calendar from 'expo-calendar';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Platform } from 'react-native';

import { Plant, Settings } from '../types';
import { buildIcs, eventDescription, eventTitle, firstOccurrence } from './ics';
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
 * Writes an .ics file and opens the share sheet, so the schedule can be imported
 * into Google Calendar on the web or sent to someone watering for you.
 */
export async function shareIcsFile(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
): Promise<string> {
  const contents = buildIcs(plants, { reminderHour: settings.reminderHour, now });
  const directory = FileSystem.Paths.cache;
  const file = new FileSystem.File(directory, 'plant-watering.ics');
  if (file.exists) file.delete();
  file.create();
  file.write(contents);

  if (Platform.OS !== 'web' && (await Sharing.isAvailableAsync())) {
    await Sharing.shareAsync(file.uri, {
      mimeType: 'text/calendar',
      dialogTitle: 'ייצוא לוח ההשקיה',
      UTI: 'com.apple.ical.ics',
    });
  }
  return file.uri;
}
