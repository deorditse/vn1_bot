import type { EnhancedStore, Reducer, ReducersMapObject, UnknownAction } from '@reduxjs/toolkit';
import type { ReactNode } from 'react';

import { instructionApi } from '@pages/instruction/api/instructionApi';
import { baseApiSlice } from '@shared/api/baseApi/baseApi';

export interface StateSchema {
  [baseApiSlice.reducerPath]: ReturnType<typeof baseApiSlice.reducer>;

  // Async reducers
  [instructionApi.reducerPath]?: ReturnType<typeof instructionApi.reducer>;
}

export type StateSchemaKey = keyof StateSchema;
export type MountedReducers = Partial<Record<StateSchemaKey, boolean>>;

export interface ReducerManager {
  getReducerMap: () => ReducersMapObject<StateSchema>;
  getMountedReducers: () => MountedReducers;
  reduce: (state: StateSchema | undefined, action: UnknownAction) => StateSchema;
  add: (key: StateSchemaKey, reducer: Reducer) => void;
  remove: (key: StateSchemaKey) => void;
}

export interface ReduxStoreWithManager extends EnhancedStore<StateSchema> {
  reducerManager: ReducerManager;
}

export type ReducersList = {
  [name in StateSchemaKey]?: Reducer<NonNullable<StateSchema[name]>>;
};

export interface DynamicModuleLoaderProps {
  reducers: ReducersList;
  removeAfterUnmount?: boolean;
  children: ReactNode;
}
