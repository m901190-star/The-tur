export const colors = {
  background: '#F5F7F2',
  surface: '#FFFFFF',
  surfaceAlt: '#EDF1E8',
  border: '#DCE3D5',
  text: '#1C2419',
  textMuted: '#6B7A64',
  primary: '#3E7C43',
  primaryDark: '#2E5E32',
  primarySoft: '#E3EFE1',
  water: '#2E7DAF',
  waterSoft: '#E1EEF6',
  overdue: '#C0452F',
  overdueSoft: '#FAE6E1',
  today: '#B9821E',
  todaySoft: '#FBF0DC',
  calm: '#6B7A64',
  calmSoft: '#ECEFE8',
  danger: '#B3372A',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
};

export const radius = {
  sm: 8,
  md: 12,
  lg: 18,
  pill: 999,
};

export const typography = {
  title: { fontSize: 24, fontWeight: '700' as const },
  heading: { fontSize: 18, fontWeight: '700' as const },
  body: { fontSize: 15, fontWeight: '400' as const },
  bodyStrong: { fontSize: 15, fontWeight: '600' as const },
  small: { fontSize: 13, fontWeight: '400' as const },
  tiny: { fontSize: 11, fontWeight: '600' as const },
};

/** Every Hebrew text block needs these two to lay out correctly. */
export const rtlText = {
  textAlign: 'right' as const,
  writingDirection: 'rtl' as const,
};
