/**
 * VerifyEmailForm.
 * Lets a user enter an OTP sent to their email to verify their account.
 * Also supports resending the OTP.
 */

import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";

interface VerifyEmailFormProps {
  email?: string;
}

export function VerifyEmailForm({ email = "" }: VerifyEmailFormProps) {
  const navigate = useNavigate();
  const [emailValue, setEmailValue] = useState(email);
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sending, setSending] = useState(false);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSending(true);
    try {
      await authService.sendOtp({ email: emailValue });
      setMessage("OTP sent. Please check your inbox.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSubmitting(true);
    try {
      await authService.verifyOtp({ email: emailValue, otp });
      navigate("/login", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      {message ? (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      ) : null}

      {/* Send OTP */}
      <form onSubmit={handleSendOtp} className="space-y-4">
        <Input
          label="Email"
          name="email"
          type="email"
          value={emailValue}
          onChange={(e) => setEmailValue(e.target.value)}
          placeholder="you@company.com"
          autoComplete="email"
          required
        />
        <Button type="submit" className="w-full" variant="ghost" loading={sending}>
          Send OTP
        </Button>
      </form>

      <div className="border-t border-slate-200 pt-6">
        <form onSubmit={handleVerify} className="space-y-4">
          <Input
            label="Verification code"
            name="otp"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit code"
            inputMode="numeric"
            maxLength={6}
            required
          />
          <Button type="submit" className="w-full" loading={submitting}>
            Verify email
          </Button>
        </form>
      </div>
    </div>
  );
}
