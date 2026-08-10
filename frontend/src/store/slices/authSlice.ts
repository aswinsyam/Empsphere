/**
 * Auth slice.
 * Manages the current user's authentication state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { authService } from "@/services/auth.service";
import { userService } from "@/services/user.service";
import { TokenUtil } from "@/utils/token";
import {
  LoginPayload,
  LoginResult,
  RegisterPayload,
  User,
} from "@/types/auth";

interface AuthState {
  user: User | null;
  loading: boolean;
  initializing: boolean;
  error: string | null;
}

/** Convert a login/register result into a partial User for the store. */
function userFromLogin(result: {
  user_id: string;
  email: string;
  role: string;
}): User {
  return {
    _id: result.user_id,
    email: result.email,
    role: result.role,
  };
}

const initialState: AuthState = {
  user: null,
  loading: false,
  initializing: true,
  error: null,
};

/** Log in and persist tokens. */
export const login = createAsyncThunk<LoginResult, LoginPayload>(
  "auth/login",
  async (payload) => {
    const result = await authService.login(payload);
    TokenUtil.setTokens(result.access_token, result.refresh_token);
    return result;
  }
);

/** Register a new account. */
export const register = createAsyncThunk<{ user_id: string }, RegisterPayload>(
  "auth/register",
  async (payload) => {
    return authService.register(payload);
  }
);

/** Fetch the current user profile. */
export const fetchMe = createAsyncThunk<User, void>(
  "auth/fetchMe",
  async () => {
    return userService.getMe();
  }
);

/** Log out. */
export const logoutUser = createAsyncThunk<void, void>(
  "auth/logout",
  async () => {
    const refreshToken = TokenUtil.getRefreshToken();
    try {
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } finally {
      TokenUtil.clear();
    }
  }
);

/** Log in with a Google ID token. */
export const googleLogin = createAsyncThunk<LoginResult, string>(
  "auth/googleLogin",
  async (idToken) => {
    const result = await authService.googleLogin(idToken);
    TokenUtil.setTokens(result.access_token, result.refresh_token);
    return result;
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    /** Clear auth state (used when token refresh fails). */
    clearAuth(state) {
      state.user = null;
      state.error = null;
    },
    /** Set the user directly (e.g. after login when no profile call needed). */
    setUser(state, action: PayloadAction<User | null>) {
      state.user = action.payload;
    },
    /** Mark initialization as complete. */
    setInitialized(state) {
      state.initializing = false;
    },
  },
  extraReducers: (builder) => {
    // login
    builder.addCase(login.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(login.fulfilled, (state, action) => {
      state.loading = false;
      state.error = null;
      state.user = userFromLogin(action.payload);
    });
    builder.addCase(login.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Login failed.";
    });

    // google login
    builder.addCase(googleLogin.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(googleLogin.fulfilled, (state, action) => {
      state.loading = false;
      state.error = null;
      state.user = userFromLogin(action.payload);
    });
    builder.addCase(googleLogin.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Google login failed.";
    });

    // register
    builder.addCase(register.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(register.fulfilled, (state) => {
      state.loading = false;
      state.error = null;
    });
    builder.addCase(register.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Registration failed.";
    });

    // fetchMe
    builder.addCase(fetchMe.pending, (state) => {
      state.loading = true;
      state.initializing = true;
    });
    builder.addCase(fetchMe.fulfilled, (state, action) => {
      state.loading = false;
      state.initializing = false;
      state.user = action.payload;
    });
    builder.addCase(fetchMe.rejected, (state, action) => {
      state.loading = false;
      state.initializing = false;
      state.user = null;
      state.error = action.error.message || "Failed to load profile.";
    });

    // logout
    builder.addCase(logoutUser.fulfilled, (state) => {
      state.user = null;
      state.error = null;
    });
    builder.addCase(logoutUser.rejected, (state) => {
      // Always clear local auth state even if the backend call fails.
      state.user = null;
      state.error = null;
    });
  },
});

export const { clearAuth, setUser, setInitialized } = authSlice.actions;

export default authSlice.reducer;
