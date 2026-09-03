/**
 * User API service.
 */

import { http } from "./api";
import { UserProfile } from "@/types/user";

/** Editable profile fields for the current user. */
export interface UpdateProfilePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
}

/** Client for current-user profile and account actions. */
export const userService = {
  /** Fetch the current user's profile. */
  async getMe(): Promise<UserProfile> {
    return http.get<UserProfile>("/auth/me/");
  },

  /** Update the current user's editable profile fields. */
  async updateProfile(payload: UpdateProfilePayload): Promise<UserProfile> {
    return http.patch<UserProfile>("/auth/profile/", payload);
  },

  /** Upload the current user's profile image. */
  async uploadProfileImage(file: File): Promise<UserProfile> {
    const formData = new FormData();
    formData.append("profile_image", file);
    return http.post<UserProfile>("/auth/profile/image/", formData);
  },

  /** Change the current user's password. */
  async changePassword(
    oldPassword: string,
    newPassword: string
  ): Promise<null> {
    return http.post<null>("/auth/change-password/", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
