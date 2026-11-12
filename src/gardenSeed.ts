import { findPreset } from './plantPresets';
import { DEFAULT_ML_PER_LITER, suggestWaterForContainer } from './lib/watering';
import { LightLevel, Plant, PotSize } from './types';

/**
 * The garden this app was built for, identified from photographs of it.
 *
 * Typing twelve planters in by hand is ten minutes of tedium, so the empty
 * screen offers to add them in one tap. Container volumes are eyeballed from
 * the photos and are the one thing worth correcting by hand — everything else
 * comes from the species preset.
 */
export interface SeedPlant {
  name: string;
  /** Must match a species in PLANT_PRESETS. */
  species: string;
  location: string;
  /** Estimated substrate volume in litres. */
  containerLiters: number;
  /** Defaults to one plant per container. */
  plantCount?: number;
  notes?: string;
}

export const GARDEN_SEED: SeedPlant[] = [
  // Three cypresses, each in its own planter — not three in one.
  { name: 'ברוש ליד הגרניום', species: 'ברוש', location: 'חצר', containerLiters: 60 },
  { name: 'ברוש האמצעי', species: 'ברוש', location: 'חצר', containerLiters: 60 },
  { name: 'ברוש ליד הביידנס', species: 'ברוש', location: 'חצר', containerLiters: 60 },

  {
    name: 'עץ הלימון',
    species: 'עץ הדר בעציץ (לימון)',
    location: 'חצר',
    containerLiters: 70,
    notes: 'עלים בהירים — לבדוק חוסר ברזל ולדשן בדשן הדרים.',
  },
  { name: 'כתר קוצים', species: 'כתר קוצים', location: 'חצר', containerLiters: 15 },
  { name: 'ביידנס לבן', species: 'ביידנס', location: 'חצר', containerLiters: 20 },
  { name: 'גרניום אדום בחצר', species: 'גרניום', location: 'חצר', containerLiters: 20 },

  { name: 'השפלרה', species: 'שפלרה מגוונת', location: 'מרפסת', containerLiters: 30 },
  { name: 'ביידנס צהוב', species: 'ביידנס', location: 'מרפסת', containerLiters: 30 },
  { name: 'סקבולה סגולה', species: 'סקבולה', location: 'מרפסת', containerLiters: 30 },
  { name: 'גרניום אדום במרפסת', species: 'גרניום', location: 'מרפסת', containerLiters: 30 },
  { name: 'גרניום ורוד', species: 'גרניום', location: 'מרפסת', containerLiters: 30 },
];

export type SeededPlant = Omit<Plant, 'id' | 'createdAt' | 'calendarEventId'>;

/** Turns the seed list into plants, pulling care figures from each preset. */
export function buildSeedPlants(now: Date = new Date()): SeededPlant[] {
  return GARDEN_SEED.map((seed) => {
    const preset = findPreset(seed.species);
    const mlPerLiter = preset?.mlPerLiterOfSoil ?? DEFAULT_ML_PER_LITER;
    const light: LightLevel = preset?.light ?? 'full-sun';
    const potSize: PotSize = preset?.potSize ?? 'large';

    return {
      name: seed.name,
      species: seed.species,
      location: seed.location,
      containerLiters: seed.containerLiters,
      plantCount: seed.plantCount ?? 1,
      // Every one of these was photographed outdoors.
      isOutdoor: true,
      isFrostTender: preset?.frostTender ?? false,
      waterMl: suggestWaterForContainer(seed.containerLiters, mlPerLiter),
      intervalSummerDays: preset?.intervalSummerDays ?? 7,
      intervalWinterDays: preset?.intervalWinterDays ?? 14,
      light,
      potSize,
      fertilizeEveryDays: preset?.fertilizeEveryDays ?? null,
      // Assume they were watered and fed today, so the list does not open with
      // twelve things already overdue on the day it is first filled in.
      lastWateredAt: now.toISOString(),
      lastFertilizedAt: preset?.fertilizeEveryDays ? now.toISOString() : null,
      photoUri: null,
      notes: seed.notes ?? '',
    };
  });
}
