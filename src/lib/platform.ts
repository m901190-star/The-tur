import { Platform } from 'react-native';

/**
 * True in the browser build.
 *
 * Compared through `String` on purpose: react-native only lists 'web' in
 * `Platform.OS`'s type when react-native-web is installed, and that is a
 * preview-only dependency here. Without this the native type-check fails on a
 * comparison that is perfectly correct at runtime.
 */
export const IS_WEB = String(Platform.OS) === 'web';

/** True where the OS can schedule a local notification for a future date. */
export const SUPPORTS_LOCAL_NOTIFICATIONS =
  Platform.OS === 'ios' || Platform.OS === 'android';
