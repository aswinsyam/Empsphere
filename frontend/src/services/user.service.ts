/**
 * User API service.
 */

import { http } from "./api";
import { api } from "@/config/axios";
import { ApiResponse } from "@/types/api";
import { UserProfile } from "@/types/user";
import { CreateUserPayload } from "@/types/auth";

/** Editable profile fields for the current user. */
export interface UpdateProfilePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
}

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
    const res = await api.post<ApiResponse<UserProfile>>(
      "/auth/profile/",
      formData
    );
    return res.data.data;
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

  /** Create a new user (Admin/HR/Employee) with role-based permission. */
  async createUser(payload: CreateUserPayload): Promise<{ user_id: string }> {
    return http.post<{ user_id: string }>("/auth/users/create/", payload);
  },
};