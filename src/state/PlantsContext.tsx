import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { rescheduleNotifications } from '../lib/notifications';
import * as storage from '../lib/storage';
import { fetchWeather, isStale } from '../lib/weather';
import {
  DEFAULT_SETTINGS,
  LogEntry,
  LogKind,
  Plant,
  Settings,
  WeatherSnapshot,
} from '../types';

export type NewPlant = Omit<Plant, 'id' | 'createdAt' | 'calendarEventId'>;

interface PlantsContextValue {
  plants: Plant[];
  log: LogEntry[];
  settings: Settings;
  ready: boolean;
  /** Latest forecast, or null when weather is off or has never been fetched. */
  weather: WeatherSnapshot | null;
  weatherLoading: boolean;
  /** Fetches a forecast; `force` ignores the cache's time-to-live. */
  refreshWeather: (force?: boolean) => Promise<void>;
  addPlant: (draft: NewPlant) => Promise<Plant>;
  updatePlant: (id: string, patch: Partial<Plant>) => Promise<void>;
  removePlant: (id: string) => Promise<void>;
  getPlant: (id: string) => Plant | undefined;
  /** Records a watering now and resets the plant's timer. */
  markWatered: (id: string, amountMl?: number) => Promise<void>;
  markFertilized: (id: string) => Promise<void>;
  /** Pushes the next watering out by `days` without recording one. */
  snooze: (id: string, days: number) => Promise<void>;
  logFor: (plantId: string) => LogEntry[];
  updateSettings: (patch: Partial<Settings>) => Promise<void>;
  resetEverything: () => Promise<void>;
}

const PlantsContext = createContext<PlantsContextValue | null>(null);

function createId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

/** Keeps the log from growing without bound on a device used for years. */
const MAX_LOG_ENTRIES = 2000;

export function PlantsProvider({ children }: { children: React.ReactNode }) {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [weather, setWeather] = useState<WeatherSnapshot | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [storedPlants, storedLog, storedSettings, storedWeather] = await Promise.all([
        storage.loadPlants(),
        storage.loadLog(),
        storage.loadSettings(),
        storage.loadWeather(),
      ]);
      if (cancelled) return;
      setPlants(storedPlants);
      setLog(storedLog);
      setSettings(storedSettings);
      setWeather(storedWeather);
      setReady(true);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const refreshWeather = useCallback(
    async (force = false) => {
      if (!settings.weatherEnabled) return;
      if (settings.latitude === null || settings.longitude === null) return;
      if (!force && !isStale(weather)) return;

      setWeatherLoading(true);
      try {
        const snapshot = await fetchWeather(settings.latitude, settings.longitude);
        setWeather(snapshot);
        await storage.saveWeather(snapshot);
      } catch {
        // Offline, or the service is down. The app keeps using the last
        // snapshot, and the plain seasonal schedule if there is none.
      } finally {
        setWeatherLoading(false);
      }
    },
    [settings.weatherEnabled, settings.latitude, settings.longitude, weather],
  );

  // Refresh once the app knows where it is, and whenever that changes.
  useEffect(() => {
    if (!ready) return;
    void refreshWeather();
  }, [ready, refreshWeather]);

  // The notification schedule is derived state: every change to the plants, the
  // settings or the forecast moves the dates, so rebuild it from scratch.
  useEffect(() => {
    if (!ready) return;
    void rescheduleNotifications(
      plants,
      settings,
      new Date(),
      settings.weatherEnabled ? weather : null,
    );
  }, [ready, plants, settings, weather]);

  const persistPlants = useCallback(async (next: Plant[]) => {
    setPlants(next);
    await storage.savePlants(next);
  }, []);

  const persistLog = useCallback(async (next: LogEntry[]) => {
    const trimmed = next.slice(0, MAX_LOG_ENTRIES);
    setLog(trimmed);
    await storage.saveLog(trimmed);
  }, []);

  const appendLog = useCallback(
    async (plantId: string, kind: LogKind, amountMl: number | null, note: string | null) => {
      const entry: LogEntry = {
        id: createId(),
        plantId,
        at: new Date().toISOString(),
        kind,
        amountMl,
        note,
      };
      await persistLog([entry, ...log]);
    },
    [log, persistLog],
  );

  const addPlant = useCallback(
    async (draft: NewPlant) => {
      const plant: Plant = {
        ...draft,
        id: createId(),
        createdAt: new Date().toISOString(),
        calendarEventId: null,
      };
      await persistPlants([...plants, plant]);
      return plant;
    },
    [plants, persistPlants],
  );

  const updatePlant = useCallback(
    async (id: string, patch: Partial<Plant>) => {
      await persistPlants(
        plants.map((plant) => (plant.id === id ? { ...plant, ...patch } : plant)),
      );
    },
    [plants, persistPlants],
  );

  const removePlant = useCallback(
    async (id: string) => {
      await persistPlants(plants.filter((plant) => plant.id !== id));
      await persistLog(log.filter((entry) => entry.plantId !== id));
    },
    [plants, log, persistPlants, persistLog],
  );

  const getPlant = useCallback(
    (id: string) => plants.find((plant) => plant.id === id),
    [plants],
  );

  const markWatered = useCallback(
    async (id: string, amountMl?: number) => {
      const plant = plants.find((candidate) => candidate.id === id);
      if (!plant) return;
      await updatePlant(id, { lastWateredAt: new Date().toISOString() });
      await appendLog(id, 'water', amountMl ?? plant.waterMl, null);
    },
    [plants, updatePlant, appendLog],
  );

  const markFertilized = useCallback(
    async (id: string) => {
      await updatePlant(id, { lastFertilizedAt: new Date().toISOString() });
      await appendLog(id, 'fertilize', null, null);
    },
    [updatePlant, appendLog],
  );

  const snooze = useCallback(
    async (id: string, days: number) => {
      const plant = plants.find((candidate) => candidate.id === id);
      if (!plant) return;
      // Snoozing moves the clock forward by shifting the "last watered" anchor,
      // without claiming the plant was actually watered.
      const anchor = plant.lastWateredAt ? new Date(plant.lastWateredAt) : new Date();
      anchor.setDate(anchor.getDate() + days);
      await updatePlant(id, { lastWateredAt: anchor.toISOString() });
      await appendLog(id, 'skip', null, `נדחה ב-${days} ימים`);
    },
    [plants, updatePlant, appendLog],
  );

  const logFor = useCallback(
    (plantId: string) =>
      log
        .filter((entry) => entry.plantId === plantId)
        .sort((a, b) => b.at.localeCompare(a.at)),
    [log],
  );

  const updateSettings = useCallback(
    async (patch: Partial<Settings>) => {
      const next = { ...settings, ...patch };
      setSettings(next);
      await storage.saveSettings(next);
    },
    [settings],
  );

  const resetEverything = useCallback(async () => {
    await storage.clearAll();
    setPlants([]);
    setLog([]);
    setSettings(DEFAULT_SETTINGS);
    setWeather(null);
  }, []);

  const value = useMemo<PlantsContextValue>(
    () => ({
      plants,
      log,
      settings,
      ready,
      weather: settings.weatherEnabled ? weather : null,
      weatherLoading,
      refreshWeather,
      addPlant,
      updatePlant,
      removePlant,
      getPlant,
      markWatered,
      markFertilized,
      snooze,
      logFor,
      updateSettings,
      resetEverything,
    }),
    [
      plants,
      log,
      settings,
      ready,
      weather,
      weatherLoading,
      refreshWeather,
      addPlant,
      updatePlant,
      removePlant,
      getPlant,
      markWatered,
      markFertilized,
      snooze,
      logFor,
      updateSettings,
      resetEverything,
    ],
  );

  return <PlantsContext.Provider value={value}>{children}</PlantsContext.Provider>;
}

export function usePlants(): PlantsContextValue {
  const context = useContext(PlantsContext);
  if (!context) {
    throw new Error('usePlants must be used inside <PlantsProvider>');
  }
  return context;
}
