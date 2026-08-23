/**
 * ProfilePage.
 *
 * Displays the current user's profile summary and provides forms to
 * update profile fields (first name, last name, phone) and upload a
 * new profile image. Uses Redux to persist updated user state.
 */

import { useCallback, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { AppDispatch } from "@/store";
import { setUser } from "@/store/slices/authSlice";
import { useAuth } from "@/hooks/useAuth";
import { Avatar } from "@/components/common/Avatar";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { PageHeader } from "@/components/common/PageHeader";
import { userService } from "@/services/user.service";
import { getErrorMessage, getProfileImageUrl } from "@/utils/helpers";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

export function ProfilePage() {
  /**
   * Displays the current user's profile summary and provides forms to
   * update profile fields (first name, last name, phone) and upload a
   * new profile image. Uses Redux to persist updated user state.
   */
  const { user } = useAuth();
  const dispatch = useDispatch<AppDispatch>();

  const [first_name, setFirstName] = useState(user?.first_name || "");
  const [last_name, setLastName] = useState(user?.last_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const refreshProfile = useCallback(async () => {
    const profile = await userService.getMe();
    dispatch(setUser(profile));
  }, [dispatch]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await userService.updateProfile({ first_name, last_name, phone });
      await refreshProfile();
      toastSuccess(AuthToasts.profileUpdated);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setSuccess(null);
    setUploading(true);
    try {
      const updatedUser = await userService.uploadProfileImage(file);
      dispatch(setUser(updatedUser));
      toastSuccess(AuthToasts.profileImageUploaded);
      setSuccess("Profile image updated successfully.");
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader
        title="My Profile"
        subtitle="View and manage your personal profile details."
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {success ? (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      ) : null}

      {/* Profile summary card */}
      <div className="card flex flex-col items-center gap-4 p-6 sm:flex-row sm:items-center">
        <div className="relative">
            <Avatar
              name={user?.full_name}
              email={user?.email}
              src={getProfileImageUrl(user?._id, user?.profile_image_id)}
              size="lg"
            />
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <p className="text-lg font-semibold text-slate-900">
            {user?.full_name || user?.email}
          </p>
          <p className="text-sm capitalize text-slate-500">
            {user?.role?.toLowerCase().replace("_", " ") || "User"}
          </p>
          <p className="mt-1 truncate text-sm text-slate-500">{user?.email}</p>
        </div>
        <div className="text-sm">
          <p className="text-xs uppercase tracking-wide text-slate-400">
            Employee Code
          </p>
          <p className="mt-0.5 font-medium text-slate-800">
            {user?.employee_code || "-"}
          </p>
        </div>
      </div>

      {/* Upload profile image */}
      <div className="card flex flex-col items-center gap-3 p-6 sm:flex-row sm:justify-between">
        <div>
          <p className="font-medium text-slate-800">Profile image</p>
          <p className="text-sm text-slate-500">
            Upload a photo to personalize your profile.
          </p>
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />
        <Button
          type="button"
          variant="ghost"
          loading={uploading}
          onClick={() => fileRef.current?.click()}
        >
          Upload image
        </Button>
      </div>

      {/* Edit profile form */}
      <div className="card p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Edit Profile
        </h2>
        <form onSubmit={handleUpdate} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="First name"
              name="first_name"
              value={first_name}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />
            <Input
              label="Last name"
              name="last_name"
              value={last_name}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
          </div>
          <Input
            label="Phone"
            name="phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Optional"
          />
          <Button type="submit" className="w-full sm:w-auto" loading={loading}>
            Save changes
          </Button>
        </form>
      </div>
    </div>
  );
}
