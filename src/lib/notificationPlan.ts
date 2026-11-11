import { Plant, Settings, WeatherSnapshot } from '../types';
import { addDays, daysBetween, startOfDay } from './dates';
import { formatWater, intervalDays, nextWateringDate } from './watering';

/** How far ahead we lay down notifications before the next reschedule. */
export const SCHEDULE_HORIZON_DAYS = 14;

/** iOS caps pending local notifications at 64; stay well inside that. */
export const MAX_SCHEDULED = 20;

export interface PlannedNotification {
  /** When it fires. */
  fireAt: Date;
  title: string;
  body: string;
  /** Plants the notification is about. */
  plantIds: string[];
}

/**
 * Works out the digest notifications for the next two weeks.
 *
 * One notification per day rather than one per plant: a morning that says
 * "3 אדניות · 25 ליטר" is actionable, where five separate buzzes are noise.
 * Pure, so the scheduling rules can be tested without a device.
 */
export function planNotifications(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): PlannedNotification[] {
  if (!settings.notificationsEnabled || plants.length === 0) return [];

  const hour = Math.min(23, Math.max(0, Math.round(settings.reminderHour)));
  const today = startOfDay(now);

  const slotOn = (day: Date): Date => {
    const slot = new Date(day);
    slot.setHours(hour, 0, 0, 0);
    return slot;
  };

  // The first day each plant needs attention. A plant that was never watered,
  // or that is already overdue, needs it today — but if today's slot has
  // already gone by, the reminder moves to tomorrow morning rather than being
  // lost until a whole interval later.
  const firstDue = new Map<string, Date>();
  for (const plant of plants) {
    const next = nextWateringDate(plant, now, weather);
    let first = !next || next.getTime() < today.getTime() ? today : next;
    if (slotOn(first).getTime() <= now.getTime()) {
      first = addDays(first, 1);
    }
    firstDue.set(plant.id, first);
  }

  const planned: PlannedNotification[] = [];

  for (let offset = 0; offset <= SCHEDULE_HORIZON_DAYS; offset += 1) {
    const day = addDays(today, offset);
    const fireAt = slotOn(day);
    // Today's slot has usually passed by the time the app is opened.
    if (fireAt.getTime() <= now.getTime()) continue;

    const due = plants.filter((plant) => {
      const first = firstDue.get(plant.id);
      if (!first || day.getTime() < first.getTime()) return false;
      const daysLate = daysBetween(first, day);
      if (daysLate === 0) return true;
      // Still unwatered a full interval later: nudge again, but not daily.
      // If the user does water it, the whole schedule is rebuilt anyway.
      return daysLate % intervalDays(plant, day, weather) === 0;
    });

    if (due.length === 0) continue;

    const totalMl = due.reduce((sum, plant) => sum + Math.max(0, plant.waterMl), 0);
    const names = due.map((plant) => plant.name || plant.species).filter(Boolean);
    const shown = names.slice(0, 3).join(', ');
    const rest = names.length > 3 ? ` ועוד ${names.length - 3}` : '';

    planned.push({
      fireAt,
      title: due.length === 1 ? 'זמן להשקות' : `${due.length} עציצים צריכים מים`,
      body: `${shown}${rest} · ${formatWater(totalMl)}`,
      plantIds: due.map((plant) => plant.id),
    });

    if (planned.length >= MAX_SCHEDULED) break;
  }

  return planned;
}

