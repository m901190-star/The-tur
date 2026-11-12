import AsyncStorage from '@react-native-async-storage/async-storage';

import {
  DEFAULT_SETTINGS,
  LogEntry,
  Plant,
  Settings,
  WeatherSnapshot,
} from '../types';

const PLANTS_KEY = 'tur.plants.v1';
const LOG_KEY = 'tur.log.v1';
const SETTINGS_KEY = 'tur.settings.v1';
const WEATHER_KEY = 'tur.weather.v1';

async function readJson<T>(key: string, fallback: T): Promise<T> {
  try {
    const raw = await AsyncStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    // A corrupt record should not brick the app; start from the fallback.
    return fallback;
  }
}

async function writeJson(key: string, value: unknown): Promise<void> {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

/**
 * Fills in fields added after a plant was first saved, so an app updated on a
 * phone that already holds plants does not start handing `undefined` to the
 * scheduling maths.
 */
function normalisePlant(stored: Plant): Plant {
  return {
    ...stored,
    containerLiters:
      typeof stored.containerLiters === 'number' ? stored.containerLiters : null,
    plantCount:
      typeof stored.plantCount === 'number' && stored.plantCount > 0
        ? stored.plantCount
        : 1,
    isOutdoor: typeof stored.isOutdoor === 'boolean' ? stored.isOutdoor : false,
    isFrostTender:
      typeof stored.isFrostTender === 'boolean' ? stored.isFrostTender : false,
    keepsDryInCold:
      typeof stored.keepsDryInCold === 'boolean' ? stored.keepsDryInCold : false,
  };
}

export async function loadPlants(): Promise<Plant[]> {
  const stored = await readJson<Plant[]>(PLANTS_KEY, []);
  return stored.map(normalisePlant);
}

export function savePlants(plants: Plant[]): Promise<void> {
  return writeJson(PLANTS_KEY, plants);
}

export function loadLog(): Promise<LogEntry[]> {
  return readJson<LogEntry[]>(LOG_KEY, []);
}

export function saveLog(log: LogEntry[]): Promise<void> {
  return writeJson(LOG_KEY, log);
}

export async function loadSettings(): Promise<Settings> {
  const stored = await readJson<Partial<Settings>>(SETTINGS_KEY, {});
  return { ...DEFAULT_SETTINGS, ...stored };
}

export function saveSettings(settings: Settings): Promise<void> {
  return writeJson(SETTINGS_KEY, settings);
}

export function loadWeather(): Promise<WeatherSnapshot | null> {
  return readJson<WeatherSnapshot | null>(WEATHER_KEY, null);
}

export function saveWeather(snapshot: WeatherSnapshot): Promise<void> {
  return writeJson(WEATHER_KEY, snapshot);
}

export async function clearAll(): Promise<void> {
  await AsyncStorage.multiRemove([PLANTS_KEY, LOG_KEY, SETTINGS_KEY, WEATHER_KEY]);
}
