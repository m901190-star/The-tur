import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

import { Plant, Settings, WeatherSnapshot } from '../types';
import { PlannedNotification, planNotifications } from './notificationPlan';

export { SCHEDULE_HORIZON_DAYS, planNotifications } from './notificationPlan';
export type { PlannedNotification } from './notificationPlan';

const ANDROID_CHANNEL_ID = 'watering';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export async function requestNotificationAccess(): Promise<boolean> {
  if (!Device.isDevice) {
    // Simulators never deliver local notifications; say so rather than
    // pretending the schedule is live.
    return false;
  }

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync(ANDROID_CHANNEL_ID, {
      name: 'השקיית עציצים',
      importance: Notifications.AndroidImportance.DEFAULT,
      sound: 'default',
    });
  }

  const existing = await Notifications.getPermissionsAsync();
  if (existing.granted) return true;
  const requested = await Notifications.requestPermissionsAsync();
  return requested.granted;
}

export async function hasNotificationAccess(): Promise<boolean> {
  try {
    const { granted } = await Notifications.getPermissionsAsync();
    return granted;
  } catch {
    return false;
  }
}

/**
 * Replaces every pending reminder with a freshly computed schedule. Called
 * whenever the plants, the settings or the forecast change, because all three
 * move the dates.
 */
export async function rescheduleNotifications(
  plants: Plant[],
  settings: Settings,
  now: Date = new Date(),
  weather: WeatherSnapshot | null = null,
): Promise<number> {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
  } catch {
    return 0;
  }

  if (!settings.notificationsEnabled) return 0;
  if (!(await hasNotificationAccess())) return 0;

  const planned = planNotifications(plants, settings, now, weather);
  let scheduled = 0;

  for (const item of planned) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: item.title,
          body: item.body,
          sound: 'default',
          data: { plantIds: item.plantIds },
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DATE,
          date: item.fireAt,
          channelId: Platform.OS === 'android' ? ANDROID_CHANNEL_ID : undefined,
        },
      });
      scheduled += 1;
    } catch {
      // One bad slot should not cost us the rest of the schedule.
    }
  }

  return scheduled;
}

export async function cancelAllNotifications(): Promise<void> {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
  } catch {
    // Nothing scheduled, or notifications unavailable on this platform.
  }
}

export async function countScheduled(): Promise<number> {
  try {
    const pending = await Notifications.getAllScheduledNotificationsAsync();
    return pending.length;
  } catch {
    return 0;
  }
}
