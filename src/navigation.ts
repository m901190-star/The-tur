export type RootStackParamList = {
  Tabs: undefined;
  PlantForm: { plantId?: string } | undefined;
  PlantDetail: { plantId: string };
};

export type TabParamList = {
  Today: undefined;
  Plants: undefined;
  Settings: undefined;
};
