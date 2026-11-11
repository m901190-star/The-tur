export type LightLevel = 'full-sun' | 'partial' | 'shade';

export type PotSize = 'small' | 'medium' | 'large';

export type Season = 'summer' | 'winter';

/** A single plant the user owns. */
export interface Plant {
  id: string;
  /** What the user calls it: "הפיקוס של הסלון". */
  name: string;
  /** Species / kind of plant: "פיקוס בנג'מינה". */
  species: string;
  /** Where it lives: "סלון", "מרפסת". */
  location: string;
  /** Water per watering, in millilitres. */
  waterMl: number;
  /** Days between waterings in the warm season (Apr–Oct). */
  intervalSummerDays: number;
  /** Days between waterings in the cold season (Nov–Mar). */
  intervalWinterDays: number;
  light: LightLevel;
  potSize: PotSize;
  /**
   * Substrate volume of the pot or planter, in litres. Set for a planter the
   * user measured; null falls back to the coarse `potSize` bucket.
   */
  containerLiters: number | null;
  /** How many plants share this container. Three cypresses in one planter
   *  drink the same soil dry roughly three times as fast. */
  plantCount: number;
  /**
   * Outdoors, the weather decides how fast the soil dries and rain counts as a
   * watering. Indoors neither is true, so the weather adjustment is skipped.
   */
  isOutdoor: boolean;
  /** Days between fertilising, or null if the user does not fertilise it. */
  fertilizeEveryDays: number | null;
  /** ISO date string of the last watering, or null if never watered. */
  lastWateredAt: string | null;
  /** ISO date string of the last fertilising, or null. */
  lastFertilizedAt: string | null;
  photoUri: string | null;
  notes: string;
  createdAt: string;
  /** Id of the recurring event this plant owns in the device calendar. */
  calendarEventId: string | null;
}

export type LogKind = 'water' | 'fertilize' | 'skip';

export interface LogEntry {
  id: string;
  plantId: string;
  /** ISO timestamp of the action. */
  at: string;
  kind: LogKind;
  /** Millilitres actually given, for 'water' entries. */
  amountMl: number | null;
  note: string | null;
}

export interface Settings {
  /** Device calendar the reminders are written to. */
  calendarId: string | null;
  calendarTitle: string | null;
  /** Hour of day (0–23) the reminder fires, both in the calendar and as a push. */
  reminderHour: number;
  /** Whether the app schedules its own notifications. */
  notificationsEnabled: boolean;
  /** Whether forecasts shift the watering schedule. */
  weatherEnabled: boolean;
  latitude: number | null;
  longitude: number | null;
  /** What to show the user for the coordinates above. */
  locationLabel: string | null;
}

export const DEFAULT_SETTINGS: Settings = {
  calendarId: null,
  calendarTitle: null,
  reminderHour: 8,
  notificationsEnabled: false,
  weatherEnabled: true,
  latitude: null,
  longitude: null,
  locationLabel: null,
};

/** One day of weather, past or forecast. */
export interface DailyWeather {
  /** Local calendar day, YYYY-MM-DD. */
  date: string;
  rainMm: number;
  /** Chance of rain, 0–100. */
  rainChance: number;
  /**
   * FAO-56 reference evapotranspiration in mm: how much water a standard crop
   * loses that day. This is the number that says how fast a planter dries.
   */
  et0Mm: number;
  maxTempC: number;
}

export interface WeatherSnapshot {
  fetchedAt: string;
  latitude: number;
  longitude: number;
  timezone: string;
  /** Oldest first: a few past days, today, then the forecast. */
  days: DailyWeather[];
}

export const LIGHT_LABELS: Record<LightLevel, string> = {
  'full-sun': 'שמש מלאה',
  partial: 'חצי צל',
  shade: 'צל',
};

export const POT_LABELS: Record<PotSize, string> = {
  small: 'קטן',
  medium: 'בינוני',
  large: 'גדול',
};

export const POT_DEFAULT_ML: Record<PotSize, number> = {
  small: 150,
  medium: 350,
  large: 700,
};

/** Rough substrate volume behind each pot-size bucket, in litres. */
export const POT_DEFAULT_LITERS: Record<PotSize, number> = {
  small: 2,
  medium: 7,
  large: 20,
};
