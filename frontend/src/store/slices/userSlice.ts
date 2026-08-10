/**
 * User slice.
 * Holds reusable user management state (currently minimal).
 */

import { createSlice } from "@reduxjs/toolkit";
import { UserProfile } from "@/types/user";

interface UserState {
  byId: Record<string, UserProfile>;
}

const initialState: UserState = {
  byId: {},
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    /** Cache a user profile by id. */
    cacheUser(state, action) {
      const profile = action.payload as UserProfile;
      state.byId[profile._id] = profile;
    },
  },
});

export const { cacheUser } = userSlice.actions;

export default userSlice.reducer;
