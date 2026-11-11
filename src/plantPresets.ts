import { LightLevel, PotSize } from './types';

export interface PlantPreset {
  species: string;
  /** Millilitres per watering for a typical pot of this plant. */
  waterMl: number;
  intervalSummerDays: number;
  intervalWinterDays: number;
  light: LightLevel;
  potSize: PotSize;
  fertilizeEveryDays: number | null;
  /** One line of care advice shown under the picker. */
  tip: string;
}

/**
 * Starting points, not gospel. Light, pot size, soil and the room's air all move
 * these numbers, so the app lets the user override every field.
 */
export const PLANT_PRESETS: PlantPreset[] = [
  {
    species: 'מונסטרה',
    waterMl: 500,
    intervalSummerDays: 7,
    intervalWinterDays: 12,
    light: 'partial',
    potSize: 'large',
    fertilizeEveryDays: 30,
    tip: 'אוהבת אור עקיף חזק. להשקות כשהשכבה העליונה יבשה למגע.',
  },
  {
    species: 'פותוס',
    waterMl: 250,
    intervalSummerDays: 7,
    intervalWinterDays: 14,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 45,
    tip: 'הסלחני שבצמחים. עדיף יבש מדי מרטוב מדי.',
  },
  {
    species: "פיקוס בנג'מינה",
    waterMl: 600,
    intervalSummerDays: 7,
    intervalWinterDays: 14,
    light: 'partial',
    potSize: 'large',
    fertilizeEveryDays: 30,
    tip: 'שונא הזזות ורוח קרה. משיר עלים כשמשנים לו מקום.',
  },
  {
    species: 'סנסיווריה (חרב הקיסר)',
    waterMl: 200,
    intervalSummerDays: 18,
    intervalWinterDays: 35,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 90,
    tip: 'הסיכון היחיד שלה הוא השקיה יתרה. בחורף כמעט לא צריכה מים.',
  },
  {
    species: 'זמיוקולקס (ZZ)',
    waterMl: 250,
    intervalSummerDays: 18,
    intervalWinterDays: 30,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 90,
    tip: 'אוגר מים בפקעות. להשקות רק כשהאדמה יבשה לגמרי.',
  },
  {
    species: 'אלוורה',
    waterMl: 200,
    intervalSummerDays: 14,
    intervalWinterDays: 28,
    light: 'full-sun',
    potSize: 'small',
    fertilizeEveryDays: 90,
    tip: 'סוקולנט. להשקות לעומק ואז לתת לאדמה להתייבש לחלוטין.',
  },
  {
    species: 'קקטוס',
    waterMl: 100,
    intervalSummerDays: 21,
    intervalWinterDays: 45,
    light: 'full-sun',
    potSize: 'small',
    fertilizeEveryDays: null,
    tip: 'בחורף להפסיק כמעט לגמרי — זו תקופת המנוחה שלו.',
  },
  {
    species: 'ספטיפילום (שלום הבית)',
    waterMl: 400,
    intervalSummerDays: 5,
    intervalWinterDays: 9,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 30,
    tip: 'מרכין עלים כשהוא צמא — סימן ברור ומיידי.',
  },
  {
    species: 'פילודנדרון',
    waterMl: 350,
    intervalSummerDays: 7,
    intervalWinterDays: 12,
    light: 'partial',
    potSize: 'medium',
    fertilizeEveryDays: 30,
    tip: 'אור עקיף. אוהב לחות באוויר — התזה על העלים עוזרת.',
  },
  {
    species: 'דרצנה',
    waterMl: 400,
    intervalSummerDays: 10,
    intervalWinterDays: 18,
    light: 'partial',
    potSize: 'large',
    fertilizeEveryDays: 45,
    tip: 'רגישה לפלואוריד במי ברז — עדיף מים שעמדו לילה.',
  },
  {
    species: 'שרך',
    waterMl: 350,
    intervalSummerDays: 3,
    intervalWinterDays: 6,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 30,
    tip: 'אוהב אדמה לחה תמיד ולחות גבוהה. חדר אמבטיה מושלם לו.',
  },
  {
    species: 'קלתיאה',
    waterMl: 300,
    intervalSummerDays: 4,
    intervalWinterDays: 8,
    light: 'shade',
    potSize: 'medium',
    fertilizeEveryDays: 30,
    tip: 'דרמטית. רגישה למי ברז — עדיף מים מסוננים.',
  },
  {
    species: 'אורכידאה',
    waterMl: 150,
    intervalSummerDays: 7,
    intervalWinterDays: 10,
    light: 'partial',
    potSize: 'small',
    fertilizeEveryDays: 21,
    tip: 'להשקות בהטבלה ולנקז היטב. שורשים עומדים במים = ריקבון.',
  },
  {
    species: 'יוקה',
    waterMl: 350,
    intervalSummerDays: 14,
    intervalWinterDays: 28,
    light: 'full-sun',
    potSize: 'large',
    fertilizeEveryDays: 90,
    tip: 'שמש ישירה ומעט מים. סובלת הזנחה בקלות.',
  },
  {
    species: 'עץ זית',
    waterMl: 1500,
    intervalSummerDays: 5,
    intervalWinterDays: 14,
    light: 'full-sun',
    potSize: 'large',
    fertilizeEveryDays: 60,
    tip: 'בעציץ הוא תלוי בך לגמרי. בקיץ על מרפסת חשופה — גם כל 3 ימים.',
  },
  {
    species: 'עץ הדר בעציץ (לימון)',
    waterMl: 2000,
    intervalSummerDays: 3,
    intervalWinterDays: 8,
    light: 'full-sun',
    potSize: 'large',
    fertilizeEveryDays: 21,
    tip: 'צמא ורעב. דשן הדרים בקיץ, וחשוב ניקוז מלא.',
  },
  {
    species: 'בוגנוויליה',
    waterMl: 1200,
    intervalSummerDays: 4,
    intervalWinterDays: 12,
    light: 'full-sun',
    potSize: 'large',
    fertilizeEveryDays: 30,
    tip: 'פורחת יותר כשהיא מעט בלחץ מים. לא להצעיף אותה במים.',
  },
  {
    species: 'גרניום',
    waterMl: 500,
    intervalSummerDays: 3,
    intervalWinterDays: 8,
    light: 'full-sun',
    potSize: 'medium',
    fertilizeEveryDays: 21,
    tip: 'להסיר פרחים שנבלו — זה מאריך את הפריחה.',
  },
  {
    species: 'בזיליקום',
    waterMl: 300,
    intervalSummerDays: 1,
    intervalWinterDays: 3,
    light: 'full-sun',
    potSize: 'small',
    fertilizeEveryDays: 21,
    tip: 'בקיץ כמעט כל יום. לקטוף את הקצה כדי שיתפצל ולא יפרח.',
  },
  {
    species: 'נענע',
    waterMl: 300,
    intervalSummerDays: 2,
    intervalWinterDays: 4,
    light: 'partial',
    potSize: 'medium',
    fertilizeEveryDays: 30,
    tip: 'צמאה ומשתלטת. עדיף עציץ נפרד משלה.',
  },
  {
    species: 'רוזמרין',
    waterMl: 350,
    intervalSummerDays: 7,
    intervalWinterDays: 16,
    light: 'full-sun',
    potSize: 'medium',
    fertilizeEveryDays: 60,
    tip: 'צמח ים-תיכוני: שמש הרבה, מים מעט, ניקוז מעולה.',
  },
  {
    species: 'סוקולנט',
    waterMl: 100,
    intervalSummerDays: 14,
    intervalWinterDays: 30,
    light: 'full-sun',
    potSize: 'small',
    fertilizeEveryDays: null,
    tip: 'עלים מקומטים = צמא. עלים שקופים ורכים = השקיה יתרה.',
  },
];

export function findPreset(species: string): PlantPreset | undefined {
  const needle = species.trim();
  return PLANT_PRESETS.find((preset) => preset.species === needle);
}

export function searchPresets(query: string): PlantPreset[] {
  const needle = query.trim();
  if (!needle) return PLANT_PRESETS;
  return PLANT_PRESETS.filter((preset) => preset.species.includes(needle));
}
