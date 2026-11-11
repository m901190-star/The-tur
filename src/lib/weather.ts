import { DailyWeather, Plant, Season, WeatherSnapshot } from '../types';
import { seasonForDate, startOfDay, toDateKey } from './dates';

const FORECAST_URL = 'https://api.open-meteo.com/v1/forecast';

/** Days of history to pull, so rain that already fell still counts. */
const PAST_DAYS = 3;
const FORECAST_DAYS = 7;

/**
 * Reference evapotranspiration, in mm/day, that the plants' stated intervals
 * are assumed to have been chosen for. A typical Israeli summer day runs about
 * 5–6 mm; a winter day about 2. When the real ET0 differs, the interval moves
 * in proportion.
 */
export const BASELINE_ET0: Record<Season, number> = {
  summer: 5.5,
  winter: 2.0,
};

/** Rain below this just wets the surface and evaporates; it waters nothing. */
export const MIN_USEFUL_RAIN_MM = 3;

/** How far the forecast may stretch or shrink an interval. */
const MIN_DEMAND_FACTOR = 0.6;
const MAX_DEMAND_FACTOR = 1.6;

export { toDateKey } from './dates';

interface OpenMeteoResponse {
  timezone?: string;
  latitude?: number;
  longitude?: number;
  daily?: {
    time?: string[];
    precipitation_sum?: (number | null)[];
    precipitation_probability_max?: (number | null)[];
    et0_fao_evapotranspiration?: (number | null)[];
    temperature_2m_max?: (number | null)[];
  };
}

function num(value: number | null | undefined, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

/** Turns the Open-Meteo payload into our own shape, tolerating missing fields. */
export function parseForecast(
  payload: OpenMeteoResponse,
  latitude: number,
  longitude: number,
  fetchedAt: Date = new Date(),
): WeatherSnapshot {
  const daily = payload.daily ?? {};
  const times = daily.time ?? [];
  const days: DailyWeather[] = times.map((date, index) => ({
    date,
    rainMm: num(daily.precipitation_sum?.[index]),
    rainChance: num(daily.precipitation_probability_max?.[index]),
    et0Mm: num(daily.et0_fao_evapotranspiration?.[index]),
    maxTempC: num(daily.temperature_2m_max?.[index]),
  }));

  return {
    fetchedAt: fetchedAt.toISOString(),
    latitude: num(payload.latitude, latitude),
    longitude: num(payload.longitude, longitude),
    timezone: payload.timezone ?? 'auto',
    days,
  };
}

/**
 * Open-Meteo's free forecast endpoint. No account and no API key, which is why
 * the app never has to hold a secret or ask the user for one.
 */
export async function fetchWeather(
  latitude: number,
  longitude: number,
): Promise<WeatherSnapshot> {
  const params = new URLSearchParams({
    latitude: latitude.toFixed(4),
    longitude: longitude.toFixed(4),
    daily: [
      'precipitation_sum',
      'precipitation_probability_max',
      'et0_fao_evapotranspiration',
      'temperature_2m_max',
    ].join(','),
    timezone: 'auto',
    past_days: String(PAST_DAYS),
    forecast_days: String(FORECAST_DAYS),
  });

  const response = await fetch(`${FORECAST_URL}?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`weather request failed: ${response.status}`);
  }
  const payload = (await response.json()) as OpenMeteoResponse;
  return parseForecast(payload, latitude, longitude);
}

export function dayFor(snapshot: WeatherSnapshot, date: Date): DailyWeather | null {
  const key = toDateKey(date);
  return snapshot.days.find((day) => day.date === key) ?? null;
}

/**
 * Days in the inclusive offset window around `now`, oldest first. Offset 0 is
 * today, negative is the past.
 */
function windowBetween(
  snapshot: WeatherSnapshot,
  now: Date,
  fromOffset: number,
  toOffset: number,
): DailyWeather[] {
  const keys = new Set<string>();
  for (let offset = fromOffset; offset <= toOffset; offset += 1) {
    const date = new Date(startOfDay(now));
    date.setDate(date.getDate() + offset);
    keys.add(toDateKey(date));
  }
  return snapshot.days.filter((day) => keys.has(day.date));
}

/**
 * Rain that has already fallen over the last `back` days, including today.
 * Today belongs here and not in the forecast window, so a single shower is
 * never counted twice.
 */
export function recentRainMm(snapshot: WeatherSnapshot, now: Date, back = 2): number {
  return windowBetween(snapshot, now, -back, 0).reduce((sum, day) => sum + day.rainMm, 0);
}

/** Rain expected from tomorrow through `ahead` days out. */
export function upcomingRainMm(snapshot: WeatherSnapshot, now: Date, ahead = 1): number {
  if (ahead < 1) return 0;
  return windowBetween(snapshot, now, 1, ahead).reduce((sum, day) => sum + day.rainMm, 0);
}

/** Mean evaporative demand over today and the next few days, or null when unknown. */
export function averageEt0(snapshot: WeatherSnapshot, now: Date, ahead = 2): number | null {
  const days = windowBetween(snapshot, now, 0, ahead).filter((day) => day.et0Mm > 0);
  if (days.length === 0) return null;
  return days.reduce((sum, day) => sum + day.et0Mm, 0) / days.length;
}

export function maxTempAhead(snapshot: WeatherSnapshot, now: Date, ahead = 2): number | null {
  const days = windowBetween(snapshot, now, 0, ahead);
  if (days.length === 0) return null;
  return Math.max(...days.map((day) => day.maxTempC));
}

export interface WeatherAdjustment {
  /** Days added to (positive) or taken off (negative) the base interval. */
  deltaDays: number;
  /** Hebrew explanation of why, or null when the weather changed nothing. */
  reason: string | null;
}

export const NO_ADJUSTMENT: WeatherAdjustment = { deltaDays: 0, reason: null };

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/**
 * Shifts a plant's watering interval to match the actual weather.
 *
 * Two independent effects, both measured in the same unit — millimetres of
 * water:
 *
 *   1. Demand. ET0 says how many mm the soil loses per day. If the coming days
 *      are hotter or drier than the season's norm, the same soil runs out
 *      sooner, so the interval shrinks in proportion (and stretches when it is
 *      cool and humid).
 *   2. Supply. Rain that fell recently, or that is about to fall, is water the
 *      user does not have to carry. Dividing those millimetres by the daily
 *      demand turns them into days of postponement.
 *
 * Indoor plants see neither, so they are left alone.
 */
export function weatherAdjustment(
  plant: Plant,
  baseIntervalDays: number,
  snapshot: WeatherSnapshot | null,
  now: Date = new Date(),
): WeatherAdjustment {
  if (!snapshot || !plant.isOutdoor) return NO_ADJUSTMENT;

  const et0 = averageEt0(snapshot, now);
  if (!et0) return NO_ADJUSTMENT;

  const baseline = BASELINE_ET0[seasonForDate(now)];
  const demandFactor = clamp(baseline / et0, MIN_DEMAND_FACTOR, MAX_DEMAND_FACTOR);
  const scaled = baseIntervalDays * demandFactor;

  const rainMm = recentRainMm(snapshot, now) + upcomingRainMm(snapshot, now);
  const usefulRain = rainMm >= MIN_USEFUL_RAIN_MM ? rainMm : 0;
  // A planter can only hold so much: rain never buys more than one full cycle.
  const rainDays = Math.min(usefulRain / et0, baseIntervalDays);

  const delta = Math.round(scaled + rainDays - baseIntervalDays);
  // Never push the interval below one day, however mild the weather.
  const deltaDays = Math.max(delta, 1 - baseIntervalDays);

  if (deltaDays === 0) return NO_ADJUSTMENT;

  const parts: string[] = [];
  if (usefulRain > 0) {
    parts.push(`ירדו ${Math.round(usefulRain)} מ״מ גשם`);
  }
  if (demandFactor < 0.95) {
    const temp = maxTempAhead(snapshot, now);
    parts.push(temp && temp >= 32 ? `חם מהרגיל (${Math.round(temp)}°)` : 'יבש מהרגיל');
  } else if (demandFactor > 1.05 && usefulRain === 0) {
    parts.push('קריר ולח מהרגיל');
  }

  const movement =
    deltaDays > 0
      ? `דחינו ב-${deltaDays} ${deltaDays === 1 ? 'יום' : 'ימים'}`
      : `הקדמנו ב-${-deltaDays} ${-deltaDays === 1 ? 'יום' : 'ימים'}`;

  const reason = parts.length > 0 ? `${parts.join(' · ')} — ${movement}` : movement;
  return { deltaDays, reason };
}

/** A one-line summary of today for the header strip. */
export function describeToday(
  snapshot: WeatherSnapshot | null,
  now: Date = new Date(),
): string | null {
  if (!snapshot) return null;
  const today = dayFor(snapshot, now);
  if (!today) return null;

  const parts = [`${Math.round(today.maxTempC)}°`];
  if (today.rainMm >= MIN_USEFUL_RAIN_MM) {
    parts.push(`${Math.round(today.rainMm)} מ״מ גשם`);
  } else if (today.rainChance >= 40) {
    parts.push(`${Math.round(today.rainChance)}% סיכוי לגשם`);
  }
  return parts.join(' · ');
}

/** Snapshots older than this are refetched. */
export const WEATHER_TTL_MS = 3 * 60 * 60 * 1000;

export function isStale(
  snapshot: WeatherSnapshot | null,
  now: Date = new Date(),
): boolean {
  if (!snapshot) return true;
  const fetchedAt = new Date(snapshot.fetchedAt).getTime();
  if (!Number.isFinite(fetchedAt)) return true;
  return now.getTime() - fetchedAt > WEATHER_TTL_MS;
}
