export type AuthResponse = {
  authenticated: boolean;
};

export type LoginRequest = {
  username: string;
  password: string;
};

export type UserProfile =
  | {
      auth_enabled: false;
    }
  | {
      sub?: string;
      username?: string;
      email?: string;
      roles: string[];
    };
