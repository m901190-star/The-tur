import {
  CANOPY_KC,
  Plant,
  POT_DEFAULT_LITERS,
  POT_DEFAULT_ML,
  PotSize,
  Season,
  WeatherSnapshot,
} from '../types';
import { MS_PER_DAY, addDays, daysBetween, seasonForDate, startOfDay } from './dates';
import { deferPastFrost, weatherAdjustment } from './weather';

export { MS_PER_DAY, addDays, daysBetween, seasonForDate, startOfDay } from './dates';


/** Peak of winter: the longest intervals of the year sit here. */
const PEAK_WINTER_DAY = 15;
const DAYS_IN_YEAR = 365.25;

function dayOfYear(date: Date): number {
  const start = new Date(date.getFullYear(), 0, 0);
  return Math.round((startOfDay(date).getTime() - start.getTime()) / MS_PER_DAY);
}

/**
 * Where the year sits between deep winter and high summer, 0 to 1: 0 in
 * mid-January, 1 in mid-July, and everything in between on a smooth curve.
 *
 * The plant's two stated intervals are the two ends of that curve, not two
 * boxes the year is sorted into. Sorting produced a cliff — the last day of
 * October asked for water every three days and the first of November every
 * eight, though nothing outside had changed — and it flattened autumn into
 * high summer, giving a mild October the same interval as mid-July.
 */
export function seasonProgress(date: Date = new Date()): number {
  const phase = Math.cos((2 * Math.PI * (dayOfYear(date) - PEAK_WINTER_DAY)) / DAYS_IN_YEAR);
  return (1 - phase) / 2;
}

/** The plant's own interval for this point in the year. */
export function seasonalIntervalDays(plant: Plant, now: Date = new Date()): number {
  const stated = (value: number, other: number) =>
    value > 0 ? value : other > 0 ? other : 7;
  const summer = stated(plant.intervalSummerDays, plant.intervalWinterDays);
  const winter = stated(plant.intervalWinterDays, plant.intervalSummerDays);
  const progress = seasonProgress(now);
  return Math.max(1, Math.round(winter + (summer - winter) * progress));
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
  const due = addDays(last, intervalDays(plant, now, weather));
  // A succulent must not go into a cold night with wet soil.
  if (plant.isOutdoor && plant.keepsDryInCold) {
    return deferPastFrost(due, weather, now).date;
  }
  return due;
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

  // When a cold night held the watering back, say so instead of the usual
  // demand-and-rain explanation: it is the more important of the two.
  let weatherReason = reason;
  if (plant.isOutdoor && plant.keepsDryInCold && plant.lastWateredAt) {
    const raw = addDays(new Date(plant.lastWateredAt), intervalDays(plant, now, weather));
    const { coldNight } = deferPastFrost(raw, weather, now);
    if (coldNight) {
      weatherReason = `לילה קר (${Math.round(coldNight.minTempC)}°) — דחינו את ההשקיה לאחריו, קקטוס רטוב בקור נרקב`;
    }
  }
  const daysSinceWatering = plant.lastWateredAt
    ? Math.max(0, -daysBetween(now, new Date(plant.lastWateredAt)))
    : null;

  if (!nextDate) {
    return {
      status: 'never',
      daysUntil: 0,
      nextDate: null,
      daysSinceWatering,
      weatherReason,
    };
  }

  const daysUntil = daysBetween(now, nextDate);
  let status: DueStatus;
  if (daysUntil < 0) status = 'overdue';
  else if (daysUntil === 0) status = 'today';
  else if (daysUntil === 1) status = 'soon';
  else status = 'ok';

  return { status, daysUntil, nextDate, daysSinceWatering, weatherReason };
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
 * The most a watering can usefully put in: the plant-available water a
 * substrate holds, about a fifth of its volume. Past this the rest runs out of
 * the drainage holes.
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

/**
 * Top surface of a container, in square metres, from its volume.
 * Calibrated against ordinary planters: a 70-litre bowl is about 50 cm across.
 */
export function potSurfaceArea(liters: number): number {
  if (!(liters > 0)) return 0;
  return 0.0118 * Math.pow(liters, 2 / 3);
}

/** Reference evapotranspiration for this point in the year, mm/day. */
export function seasonalEt0(now: Date = new Date()): number {
  const winter = 2.0;
  const summer = 5.5;
  return winter + (summer - winter) * seasonProgress(now);
}

/**
 * Litres the plant draws per day: evaporative demand over the pot's surface,
 * scaled by how much of it the foliage covers.
 */
export function dailyWaterUse(
  plant: Plant,
  now: Date = new Date(),
  et0?: number,
): number {
  const demand = et0 && et0 > 0 ? et0 : seasonalEt0(now);
  const area = potSurfaceArea(containerLitersFor(plant));
  const kc = CANOPY_KC[plant.canopy] ?? CANOPY_KC.filling;
  // Several plants share the pot's surface but each adds foliage over it.
  const crowding = Math.min(1.6, Math.sqrt(Math.max(1, plant.plantCount)));
  return demand * kc * area * crowding;
}

/** Enough extra to wet the root ball evenly and carry salts down past it. */
const LEACHING_MARGIN = 1.5;

/**
 * How much to pour, in millilitres.
 *
 * Sized to what the plant will actually drink before the next watering, not to
 * the pot. Sizing it to the pot is right only when the roots fill the pot; for
 * a young tree in a large planter it prescribes several times what the tree
 * uses, and the planter never dries out — which is how citrus roots drown. The
 * container's own capacity stays as the ceiling, since water past it just runs
 * out of the bottom.
 */
export function suggestWaterForPlant(
  plant: Plant,
  now: Date = new Date(),
  et0?: number,
): number {
  const liters = containerLitersFor(plant);
  if (!(liters > 0)) return 0;

  const interval = Math.max(1, seasonalIntervalDays(plant, now));
  const needMl = dailyWaterUse(plant, now, et0) * interval * LEACHING_MARGIN * 1000;
  const ceilingMl = suggestWaterForContainer(liters);

  const chosen = Math.min(needMl, ceilingMl);
  return Math.max(100, Math.round(chosen / 100) * 100);
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
