import { Season } from '../types';

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

/** Local calendar day as YYYY-MM-DD. */
export function toDateKey(date: Date): string {
  const local = startOfDay(date);
  const month = String(local.getMonth() + 1).padStart(2, '0');
  const day = String(local.getDate()).padStart(2, '0');
  return `${local.getFullYear()}-${month}-${day}`;
}
