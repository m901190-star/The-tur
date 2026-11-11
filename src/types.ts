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
  /** Hour of day (0–23) the calendar reminder fires. */
  reminderHour: number;
}

export const DEFAULT_SETTINGS: Settings = {
  calendarId: null,
  calendarTitle: null,
  reminderHour: 8,
};

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
