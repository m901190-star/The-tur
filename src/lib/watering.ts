import {
  Plant,
  POT_DEFAULT_LITERS,
  POT_DEFAULT_ML,
  PotSize,
  Season,
  WeatherSnapshot,
} from '../types';
import { addDays, daysBetween, seasonForDate, startOfDay } from './dates';
import { weatherAdjustment } from './weather';

export { MS_PER_DAY, addDays, daysBetween, seasonForDate, startOfDay } from './dates';


/** The plant's own stated interval for the season `now` falls in. */
export function seasonalIntervalDays(plant: Plant, now: Date = new Date()): number {
  const seasonal =
    seasonForDate(now) === 'summer' ? plant.intervalSummerDays : plant.intervalWinterDays;
  const fallback = plant.intervalSummerDays || plant.intervalWinterDays || 7;
  const value = seasonal > 0 ? seasonal : fallback;
  return Math.max(1, Math.round(value));
}

/**
 * Several plants sharing one container empty it faster, but not in proportion
 * to their number: crowded roots stay smaller than one plant given the whole
 * planter to itself. Damping by the square root lands between "ignore it"
 * (wrong) and "divide by the count" (too aggressive). Three cypresses in one
 * planter turn a 7-day interval into 4 days.
 */
export function crowdingFactor(plantCount: number): number {
  const count = Math.max(1, Math.round(plantCount || 1));
  return 1 / Math.sqrt(count);
}

/** Interval before the weather has its say: season and crowding only. */
export function baseIntervalDays(plant: Plant, now: Date = new Date()): number {
  const seasonal = seasonalIntervalDays(plant, now);
  return Math.max(1, Math.round(seasonal * crowdingFactor(plant.plantCount)));
}

/**
 * Days between waterings for this plant right now. With a weather snapshot and
 * an outdoor plant, rain and evaporative demand move the number; otherwise this
 * is the seasonal interval adjusted for how many plants share the container.
 */
export function intervalDays(
  plant: Plant,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): number {
  const base = baseIntervalDays(plant, now);
  const { deltaDays } = weatherAdjustment(plant, base, weather, now);
  return Math.max(1, base + deltaDays);
}

/** The day this plant is next due, or null when it was never watered. */
export function nextWateringDate(
  plant: Plant,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): Date | null {
  if (!plant.lastWateredAt) return null;
  const last = new Date(plant.lastWateredAt);
  if (Number.isNaN(last.getTime())) return null;
  return addDays(last, intervalDays(plant, now, weather));
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
  /** Why the weather moved this plant's schedule, or null if it did not. */
  weatherReason: string | null;
}

export function wateringState(
  plant: Plant,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): WateringState {
  const base = baseIntervalDays(plant, now);
  const { reason } = weatherAdjustment(plant, base, weather, now);
  const nextDate = nextWateringDate(plant, now, weather);
  const daysSinceWatering = plant.lastWateredAt
    ? Math.max(0, -daysBetween(now, new Date(plant.lastWateredAt)))
    : null;

  if (!nextDate) {
    return {
      status: 'never',
      daysUntil: 0,
      nextDate: null,
      daysSinceWatering,
      weatherReason: reason,
    };
  }

  const daysUntil = daysBetween(now, nextDate);
  let status: DueStatus;
  if (daysUntil < 0) status = 'overdue';
  else if (daysUntil === 0) status = 'today';
  else if (daysUntil === 1) status = 'soon';
  else status = 'ok';

  return { status, daysUntil, nextDate, daysSinceWatering, weatherReason: reason };
}

/** True when the plant belongs on the "water today" list. */
export function needsWaterNow(
  plant: Plant,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): boolean {
  const { status } = wateringState(plant, now, weather);
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
export function compareByUrgency(
  a: Plant,
  b: Plant,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): number {
  const left = wateringState(a, now, weather);
  const right = wateringState(b, now, weather);
  const byStatus = URGENCY[left.status] - URGENCY[right.status];
  if (byStatus !== 0) return byStatus;
  if (left.daysUntil !== right.daysUntil) return left.daysUntil - right.daysUntil;
  return a.name.localeCompare(b.name, 'he');
}

export function sortByUrgency(
  plants: Plant[],
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): Plant[] {
  return [...plants].sort((a, b) => compareByUrgency(a, b, now, weather));
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
export function totalWaterDue(
  plants: Plant[],
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): number {
  return plants
    .filter((plant) => needsWaterNow(plant, now, weather))
    .reduce((sum, plant) => sum + Math.max(0, plant.waterMl), 0);
}

/**
 * A thorough watering wets the whole root ball without most of it running
 * straight out of the drainage holes: roughly 15% of the substrate volume.
 */
export const DEFAULT_ML_PER_LITER = 150;

export function suggestWaterForContainer(
  liters: number,
  mlPerLiter: number = DEFAULT_ML_PER_LITER,
): number {
  if (!(liters > 0)) return 0;
  // Round to the nearest 100 ml — nobody measures a planter to the millilitre.
  return Math.max(100, Math.round((liters * mlPerLiter) / 100) * 100);
}

export function suggestWaterMl(potSize: PotSize): number {
  return POT_DEFAULT_ML[potSize];
}

/** The plant's substrate volume: measured if the user gave one, else the bucket. */
export function containerLitersFor(plant: Plant): number {
  return plant.containerLiters && plant.containerLiters > 0
    ? plant.containerLiters
    : POT_DEFAULT_LITERS[plant.potSize];
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
