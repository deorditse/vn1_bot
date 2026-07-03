import { configureStore } from '@reduxjs/toolkit';
import type { ReducersMapObject, UnknownAction } from '@reduxjs/toolkit';
import type { ThunkDispatch } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

import { baseApiSlice } from '@shared/api';
import { createReducerManager } from './createReducerManager';
import type { ReduxStoreWithManager, StateSchema } from './StateSchema';

export function createReduxStore(
  initialState?: StateSchema,
  asyncReducers?: ReducersMapObject<StateSchema>,
) {
  const staticReducers: ReducersMapObject<StateSchema> = {
    [baseApiSlice.reducerPath]: baseApiSlice.reducer,
  };

  const reducerManager = createReducerManager({
    ...staticReducers,
    ...asyncReducers,
  });

  const store = configureStore({
    reducer: reducerManager.reduce,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(baseApiSlice.middleware),
    devTools: import.meta.env.DEV,
    preloadedState: initialState,
  }) as ReduxStoreWithManager;

  store.reducerManager = reducerManager;
  setupListeners(store.dispatch);

  return store;
}

export const store = createReduxStore();

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = ThunkDispatch<StateSchema, unknown, UnknownAction>;
