import * as Location from 'expo-location';

export interface Coordinates {
  latitude: number;
  longitude: number;
  /** What to show the user, e.g. "תל אביב" or "32.08, 34.78". */
  label: string;
}

/** Fallback list for when the user would rather not share their location. */
export const ISRAELI_CITIES: Coordinates[] = [
  { label: 'תל אביב', latitude: 32.0853, longitude: 34.7818 },
  { label: 'ירושלים', latitude: 31.7683, longitude: 35.2137 },
  { label: 'חיפה', latitude: 32.794, longitude: 34.9896 },
  { label: 'באר שבע', latitude: 31.2518, longitude: 34.7913 },
  { label: 'אילת', latitude: 29.5577, longitude: 34.9519 },
  { label: 'טבריה', latitude: 32.7922, longitude: 35.5312 },
  { label: 'מודיעין', latitude: 31.8928, longitude: 35.0104 },
  { label: 'אשדוד', latitude: 31.8044, longitude: 34.6553 },
];

function formatCoords(latitude: number, longitude: number): string {
  return `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
}

/**
 * Asks the device where it is. Returns null when the user declines or the fix
 * fails — the caller then falls back to a city the user picks by hand, so the
 * weather feature never depends on the permission being granted.
 */
export async function detectLocation(): Promise<Coordinates | null> {
  try {
    const { granted } = await Location.requestForegroundPermissionsAsync();
    if (!granted) return null;

    const position = await Location.getLastKnownPositionAsync();
    const fix =
      position ??
      (await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Low,
      }));
    if (!fix) return null;

    const { latitude, longitude } = fix.coords;
    return {
      latitude,
      longitude,
      label: await describeCoordinates(latitude, longitude),
    };
  } catch {
    return null;
  }
}

/** Turns coordinates into a place name, falling back to the numbers. */
async function describeCoordinates(latitude: number, longitude: number): Promise<string> {
  try {
    const places = await Location.reverseGeocodeAsync({ latitude, longitude });
    const place = places[0];
    const name = place?.city || place?.subregion || place?.region;
    return name ?? formatCoords(latitude, longitude);
  } catch {
    return formatCoords(latitude, longitude);
  }
}
