import { Plant, POT_DEFAULT_ML, PotSize, Season } from '../types';

export const MS_PER_DAY = 24 * 60 * 60 * 1000;

/** Midnight local time of the day `date` falls in. */
export function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export function addDays(date: Date, days: number): Date {
  const next = startOfDay(date);
  next.setDate(next.getDate() + days);
  return next;
}

/** Whole calendar days from `from` to `to`; negative when `to` is in the past. */
export function daysBetween(from: Date, to: Date): number {
  return Math.round((startOfDay(to).getTime() - startOfDay(from).getTime()) / MS_PER_DAY);
}

/**
 * Israeli growing season. April–October the plants drink markedly more than
 * November–March, which is why every plant carries two intervals.
 */
export function seasonForDate(date: Date): Season {
  const month = date.getMonth() + 1;
  return month >= 4 && month <= 10 ? 'summer' : 'winter';
}

/** Days between waterings for this plant, for the season `now` falls in. */
export function intervalDays(plant: Plant, now: Date = new Date()): number {
  const seasonal =
    seasonForDate(now) === 'summer' ? plant.intervalSummerDays : plant.intervalWinterDays;
  const fallback = plant.intervalSummerDays || plant.intervalWinterDays || 7;
  const value = seasonal > 0 ? seasonal : fallback;
  return Math.max(1, Math.round(value));
}

/** The day this plant is next due, or null when it was never watered. */
export function nextWateringDate(plant: Plant, now: Date = new Date()): Date | null {
  if (!plant.lastWateredAt) return null;
  const last = new Date(plant.lastWateredAt);
  if (Number.isNaN(last.getTime())) return null;
  return addDays(last, intervalDays(plant, now));
}

export type DueStatus =
  /** Never watered through the app — we have nothing to count from. */
  | 'never'
  /** The due day has passed. */
  | 'overdue'
  /** Due today. */
  | 'today'
  /** Due tomorrow. */
  | 'soon'
  /** Due in two days or more. */
  | 'ok';

export interface WateringState {
  status: DueStatus;
  /** Calendar days until due: 0 today, negative when overdue. */
  daysUntil: number;
  nextDate: Date | null;
  /** How many days ago it was last watered, or null if never. */
  daysSinceWatering: number | null;
}

export function wateringState(plant: Plant, now: Date = new Date()): WateringState {
  const nextDate = nextWateringDate(plant, now);
  const daysSinceWatering = plant.lastWateredAt
    ? Math.max(0, -daysBetween(now, new Date(plant.lastWateredAt)))
    : null;

  if (!nextDate) {
    return { status: 'never', daysUntil: 0, nextDate: null, daysSinceWatering };
  }

  const daysUntil = daysBetween(now, nextDate);
  let status: DueStatus;
  if (daysUntil < 0) status = 'overdue';
  else if (daysUntil === 0) status = 'today';
  else if (daysUntil === 1) status = 'soon';
  else status = 'ok';

  return { status, daysUntil, nextDate, daysSinceWatering };
}

/** True when the plant belongs on the "water today" list. */
export function needsWaterNow(plant: Plant, now: Date = new Date()): boolean {
  const { status } = wateringState(plant, now);
  return status === 'never' || status === 'overdue' || status === 'today';
}

const URGENCY: Record<DueStatus, number> = {
  overdue: 0,
  today: 1,
  never: 2,
  soon: 3,
  ok: 4,
};

/** Most urgent first; within the same status, the soonest (or most overdue) first. */
export function compareByUrgency(a: Plant, b: Plant, now: Date = new Date()): number {
  const left = wateringState(a, now);
  const right = wateringState(b, now);
  const byStatus = URGENCY[left.status] - URGENCY[right.status];
  if (byStatus !== 0) return byStatus;
  if (left.daysUntil !== right.daysUntil) return left.daysUntil - right.daysUntil;
  return a.name.localeCompare(b.name, 'he');
}

export function sortByUrgency(plants: Plant[], now: Date = new Date()): Plant[] {
  return [...plants].sort((a, b) => compareByUrgency(a, b, now));
}

export interface FertilizeState {
  /** False when this plant is not fertilised at all. */
  tracked: boolean;
  due: boolean;
  daysUntil: number;
  nextDate: Date | null;
}

export function fertilizeState(plant: Plant, now: Date = new Date()): FertilizeState {
  const every = plant.fertilizeEveryDays;
  if (!every || every <= 0) {
    return { tracked: false, due: false, daysUntil: 0, nextDate: null };
  }
  if (!plant.lastFertilizedAt) {
    return { tracked: true, due: true, daysUntil: 0, nextDate: null };
  }
  const nextDate = addDays(new Date(plant.lastFertilizedAt), Math.round(every));
  const daysUntil = daysBetween(now, nextDate);
  return { tracked: true, due: daysUntil <= 0, daysUntil, nextDate };
}

/** Total water the due plants need right now, in millilitres. */
export function totalWaterDue(plants: Plant[], now: Date = new Date()): number {
  return plants
    .filter((plant) => needsWaterNow(plant, now))
    .reduce((sum, plant) => sum + Math.max(0, plant.waterMl), 0);
}

export function suggestWaterMl(potSize: PotSize): number {
  return POT_DEFAULT_ML[potSize];
}

/** "350 מ״ל" / "1.2 ליטר" */
export function formatWater(ml: number): string {
  if (ml >= 1000) {
    const litres = ml / 1000;
    const rounded = Math.round(litres * 10) / 10;
    return `${rounded} ליטר`;
  }
  return `${Math.round(ml)} מ״ל`;
}

const HE_DATE = new Intl.DateTimeFormat('he-IL', { day: 'numeric', month: 'short' });

/** "היום" / "מחר" / "לפני 3 ימים" / "12 בנוב׳" */
export function formatRelativeDay(date: Date, now: Date = new Date()): string {
  const diff = daysBetween(now, date);
  if (diff === 0) return 'היום';
  if (diff === 1) return 'מחר';
  if (diff === -1) return 'אתמול';
  if (diff > 1 && diff <= 7) return `בעוד ${diff} ימים`;
  if (diff < -1 && diff >= -7) return `לפני ${-diff} ימים`;
  return HE_DATE.format(date);
}

export function statusLabel(state: WateringState): string {
  switch (state.status) {
    case 'never':
      return 'טרם הושקה';
    case 'overdue':
      return state.daysUntil === -1 ? 'באיחור של יום' : `באיחור של ${-state.daysUntil} ימים`;
    case 'today':
      return 'להשקות היום';
    case 'soon':
      return 'מחר';
    default:
      return `בעוד ${state.daysUntil} ימים`;
  }
}
