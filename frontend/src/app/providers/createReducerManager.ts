import { combineReducers } from '@reduxjs/toolkit';
import type { Reducer, ReducersMapObject, UnknownAction } from '@reduxjs/toolkit';

import type { MountedReducers, ReducerManager, StateSchema, StateSchemaKey } from './StateSchema';

export function createReducerManager(initialReducers: ReducersMapObject<StateSchema>): ReducerManager {
  const reducers = { ...initialReducers };
  let combinedReducer = combineReducers(reducers) as Reducer<StateSchema>;
  const staticReducers: StateSchemaKey[] = ['api'];
  let keysToRemove: StateSchemaKey[] = [];
  const mountedReducers: MountedReducers = {};

  return {
    getReducerMap: () => reducers,
    getMountedReducers: () => mountedReducers,
    reduce: (state: StateSchema | undefined, action: UnknownAction) => {
      if (!state) {
        return combinedReducer(state, action);
      }

      if (keysToRemove.length > 0) {
        const nextState: Partial<StateSchema> = { ...state };
        keysToRemove.forEach((key) => {
          delete nextState[key];
        });
        state = nextState as StateSchema;
        keysToRemove = [];
      }

      return combinedReducer(state, action);
    },
    add: (key: StateSchemaKey, reducer: Reducer) => {
      if (!key || reducers[key]) {
        return;
      }

      reducers[key] = reducer;
      mountedReducers[key] = true;
      combinedReducer = combineReducers(reducers) as Reducer<StateSchema>;
    },
    remove: (key: StateSchemaKey) => {
      if (!key || !reducers[key] || staticReducers.includes(key)) {
        return;
      }

      delete (reducers as Partial<ReducersMapObject<StateSchema>>)[key];
      keysToRemove.push(key);
      mountedReducers[key] = false;
      combinedReducer = combineReducers(reducers) as Reducer<StateSchema>;
    },
  };
}
