import React, { useEffect, useState } from "react";
import { useApp } from "../context/AppContext";
import {
  Calendar,
  Flame,
  BookOpen,
  Mail,
  Bookmark,
  CheckCircle2,
  Circle,
  Trash2,
  Sparkles,
  ShieldCheck,
  Lock,
  Edit2,
  Check,
  AlertCircle,
  Loader2,
  Send,
  UserCheck
} from "lucide-react";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";
import {
  apiGetSavedRecommendations,
  apiDeleteSavedRecommendation,
  apiToggleSavedRecommendation,
  apiUpdateProfile,
  apiChangePassword,
  apiResendVerification,
  apiVerifyEmail
} from "../services/api";

export function Profile() {
  const { user, setUser, dashboardData, historyTotal, isDemoMode } = useApp();
  const [savedRecs, setSavedRecs] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(true);

  // Age editing state
  const [isEditingAge, setIsEditingAge] = useState(false);
  const [ageInput, setAgeInput] = useState(user?.age || 18);
  const [ageSaving, setAgeSaving] = useState(false);
  const [ageMsg, setAgeMsg] = useState({ error: "", success: "" });

  // Email verification state
  const [isResending, setIsResending] = useState(false);
  const [verifyNotice, setVerifyNotice] = useState({ text: "", link: "", isSuccess: false });

  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwSaving, setPwSaving] = useState(false);
  const [pwMsg, setPwMsg] = useState({ error: "", success: "" });

  const streak = dashboardData?.streak_days ?? user?.streak_days ?? 0;
  const total = dashboardData?.total_entries ?? historyTotal ?? 0;
  const created = user?.created_at
    ? new Date(user.created_at).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric"
      })
    : "—";

  const fetchRecs = async () => {
    if (isDemoMode) {
      setSavedRecs([
        {
          id: 1,
          title: "Mindful 5-Minute Pause",
          description: "Step away from work and ground your awareness in sensory surroundings.",
          category: "Mindfulness",
          is_completed: 0
        },
        {
          id: 2,
          title: "Box Breathing Cycle",
          description: "Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4. Repeat 4 times.",
          category: "Restoration",
          is_completed: 1
        }
      ]);
      setLoadingRecs(false);
      return;
    }
    try {
      const data = await apiGetSavedRecommendations();
      setSavedRecs(data.items || []);
    } catch (err) {
      console.warn("Could not load recommendations:", err);
    } finally {
      setLoadingRecs(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, [isDemoMode]);

  const handleToggle = async (id, currentStatus) => {
    try {
      setSavedRecs(prev =>
        prev.map(r => (r.id === id ? { ...r, is_completed: r.is_completed ? 0 : 1 } : r))
      );
      if (!isDemoMode) {
        await apiToggleSavedRecommendation(id);
      }
    } catch (err) {
      console.error("Toggle failed:", err);
      fetchRecs();
    }
  };

  const handleDelete = async (id) => {
    try {
      setSavedRecs(prev => prev.filter(r => r.id !== id));
      if (!isDemoMode) {
        await apiDeleteSavedRecommendation(id);
      }
    } catch (err) {
      console.error("Delete failed:", err);
      fetchRecs();
    }
  };

  const handleSaveAge = async () => {
    setAgeMsg({ error: "", success: "" });
    const parsed = parseInt(ageInput, 10);
    if (isNaN(parsed) || parsed < 18) {
      setAgeMsg({ error: "Age must be 18 or older.", success: "" });
      return;
    }
    if (parsed > 125) {
      setAgeMsg({ error: "Please enter a realistic age.", success: "" });
      return;
    }
    if (isDemoMode) {
      setUser(prev => ({ ...prev, age: parsed }));
      setIsEditingAge(false);
      setAgeMsg({ error: "", success: "Age updated in demo profile." });
      return;
    }
    setAgeSaving(true);
    try {
      const res = await apiUpdateProfile({ age: parsed });
      setUser(res.user);
      setIsEditingAge(false);
      setAgeMsg({ error: "", success: "Age updated successfully!" });
      setTimeout(() => setAgeMsg({ error: "", success: "" }), 3500);
    } catch (e) {
      setAgeMsg({ error: e.message || "Failed to update age.", success: "" });
    } finally {
      setAgeSaving(false);
    }
  };

  const handleResendEmail = async () => {
    if (isDemoMode) {
      setVerifyNotice({
        text: "Sample demo accounts do not require verification.",
        link: "",
        isSuccess: true
      });
      return;
    }
    setIsResending(true);
    setVerifyNotice({ text: "", link: "", isSuccess: false });
    try {
      const res = await apiResendVerification();
      setVerifyNotice({
        text: res.message || "Verification email initiated.",
        link: res.verification_link || "",
        isSuccess: true
      });
    } catch (e) {
      setVerifyNotice({ text: e.message || "Failed to send verification link.", link: "", isSuccess: false });
    } finally {
      setIsResending(false);
    }
  };

  const handleSimulatedVerify = async (link) => {
    try {
      const url = new URL(link);
      const token = url.searchParams.get("token");
      if (token) {
        const res = await apiVerifyEmail(token);
        setUser(res.user);
        setVerifyNotice({ text: "Email verified successfully!", link: "", isSuccess: true });
      }
    } catch (e) {
      alert("Verification failed: " + e.message);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPwMsg({ error: "", success: "" });

    if (!currentPw) {
      setPwMsg({ error: "Please enter your current password.", success: "" });
      return;
    }
    if (newPw.length < 6) {
      setPwMsg({ error: "New password must be at least 6 characters.", success: "" });
      return;
    }
    if (newPw !== confirmPw) {
      setPwMsg({ error: "New passwords do not match.", success: "" });
      return;
    }
    if (isDemoMode) {
      setPwMsg({ error: "", success: "Demo account password changed (preview mode)." });
      setCurrentPw("");
      setNewPw("");
      setConfirmPw("");
      return;
    }

    setPwSaving(true);
    try {
      await apiChangePassword(currentPw, newPw, confirmPw);
      setPwMsg({ error: "", success: "Password changed successfully!" });
      setCurrentPw("");
      setNewPw("");
      setConfirmPw("");
      setTimeout(() => setShowPasswordForm(false), 2000);
    } catch (err) {
      setPwMsg({ error: err.message || "Failed to change password.", success: "" });
    } finally {
      setPwSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900">Your Profile</h1>
        <p className="text-sm text-slate-500 mt-1">
          Your account details, verified age, and saved wellness practices.
        </p>
      </div>

      {/* User Card */}
      <div className="bg-white rounded-3xl p-7 border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-brand-600 to-brand-400 text-white flex items-center justify-center font-extrabold text-2xl shadow-md shrink-0">
            {user?.name?.[0]?.toUpperCase() || "?"}
          </div>
          <div className="text-center sm:text-left space-y-2">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">{user?.name || "Your account"}</h2>
              <div className="flex items-center gap-2 mt-1 flex-wrap justify-center sm:justify-start">
                <span className="text-xs text-slate-500 flex gap-1.5 items-center">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  {user?.email || "—"}
                </span>

                {user?.is_email_verified ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Verified
                  </span>
                ) : (
                  <div className="inline-flex items-center gap-1.5">
                    <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                      Unverified
                    </span>
                    <button
                      onClick={handleResendEmail}
                      disabled={isResending}
                      className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold underline disabled:opacity-50"
                    >
                      {isResending ? "Sending..." : "Verify email"}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Age display & edit */}
            <div className="flex items-center gap-2 pt-1 text-xs text-slate-600 justify-center sm:justify-start">
              <span className="font-semibold text-slate-700">Age:</span>
              {isEditingAge ? (
                <div className="inline-flex items-center gap-2">
                  <input
                    type="number"
                    min="18"
                    max="120"
                    value={ageInput}
                    onChange={(e) => setAgeInput(e.target.value)}
                    className="w-16 px-2 py-1 rounded-lg border border-slate-300 text-xs text-slate-900 outline-none focus:border-indigo-500"
                  />
                  <button
                    onClick={handleSaveAge}
                    disabled={ageSaving}
                    className="px-2.5 py-1 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {ageSaving ? "..." : "Save"}
                  </button>
                  <button
                    onClick={() => {
                      setIsEditingAge(false);
                      setAgeInput(user?.age || 18);
                      setAgeMsg({ error: "", success: "" });
                    }}
                    className="px-2 py-1 text-slate-500 hover:text-slate-800 text-xs"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2">
                  <span className="font-bold text-slate-900">{user?.age || 18} years old</span>
                  <span className="text-[11px] text-emerald-600 font-medium bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100">
                    Age Eligible (18+)
                  </span>
                  <button
                    onClick={() => setIsEditingAge(true)}
                    className="text-indigo-600 hover:text-indigo-800 text-xs font-semibold inline-flex items-center gap-0.5 ml-1"
                  >
                    <Edit2 className="w-3 h-3" />
                    <span>Edit</span>
                  </button>
                </div>
              )}
            </div>

            {ageMsg.error && <p className="text-xs text-rose-600 font-medium">{ageMsg.error}</p>}
            {ageMsg.success && <p className="text-xs text-emerald-600 font-medium">{ageMsg.success}</p>}

            <p className="text-xs text-slate-400 flex gap-1.5 items-center justify-center sm:justify-start pt-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              Account created {created}
            </p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="flex flex-col sm:flex-row md:flex-col gap-2 w-full md:w-auto">
          <button
            onClick={() => setShowPasswordForm(!showPasswordForm)}
            className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all flex items-center justify-center gap-1.5"
          >
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            <span>{showPasswordForm ? "Hide Password Form" : "Change Password"}</span>
          </button>
        </div>
      </div>

      {/* Verification Notice Banner */}
      {verifyNotice.text && (
        <div className={`p-4 rounded-2xl border text-xs leading-relaxed flex items-start gap-3 ${
          verifyNotice.isSuccess ? "bg-indigo-50 border-indigo-200 text-indigo-900" : "bg-rose-50 border-rose-200 text-rose-900"
        }`}>
          <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">{verifyNotice.text}</p>
            {verifyNotice.link && (
              <p className="text-slate-600">
                Local dev simulator:{" "}
                <button
                  onClick={() => handleSimulatedVerify(verifyNotice.link)}
                  className="font-bold underline text-indigo-700 hover:text-indigo-900"
                >
                  Click here to verify email now →
                </button>
              </p>
            )}
          </div>
        </div>
      )}

      {/* Change Password Form (Collapsible) */}
      {showPasswordForm && (
        <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs space-y-4 animate-in fade-in">
          <div className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Change Account Password</h3>
          </div>

          {pwMsg.error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-100 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{pwMsg.error}</span>
            </div>
          )}
          {pwMsg.success && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-100 text-xs text-emerald-700 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{pwMsg.success}</span>
            </div>
          )}

          <form onSubmit={handleChangePassword} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Current Password
              </label>
              <input
                type="password"
                value={currentPw}
                onChange={(e) => setCurrentPw(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm outline-none focus:border-indigo-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                New Password (6+ chars)
              </label>
              <input
                type="password"
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm outline-none focus:border-indigo-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm outline-none focus:border-indigo-600"
              />
            </div>

            <div className="sm:col-span-3 flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setShowPasswordForm(false);
                  setPwMsg({ error: "", success: "" });
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={pwSaving}
                className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5"
              >
                {pwSaving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>{pwSaving ? "Updating..." : "Update Password"}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reflection Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 text-center shadow-xs">
          <BookOpen className="w-6 h-6 text-brand-600 mx-auto mb-2" />
          <p className="text-3xl font-black text-slate-900">{total}</p>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mt-1">
            Total Reflections
          </p>
        </div>
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 text-center shadow-xs">
          <Flame className="w-6 h-6 text-amber-500 mx-auto mb-2" />
          <p className="text-3xl font-black text-slate-900">{streak || "—"}{streak ? " days" : ""}</p>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mt-1">
            Current Streak
          </p>
        </div>
      </div>

      {/* Saved Practices & Recommendations */}
      <section className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center">
              <Bookmark className="w-4 h-4 text-brand-600" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Saved Practices & Gentle Suggestions
              </h2>
              <p className="text-xs text-slate-400">
                Techniques and actions you bookmarked from your reflection results
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
            {savedRecs.length} saved
          </span>
        </div>

        {loadingRecs ? (
          <div className="py-8 text-center text-xs text-slate-400">Loading saved practices...</div>
        ) : savedRecs.length === 0 ? (
          <div className="py-10 text-center space-y-2">
            <Sparkles className="w-8 h-8 text-slate-300 mx-auto" />
            <p className="text-xs font-medium text-slate-600">No saved recommendations yet.</p>
            <p className="text-[11px] text-slate-400 max-w-sm mx-auto">
              When you finish a reflection, tap <strong>Save Recommendations</strong> to keep helpful practices here.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {savedRecs.map((rec) => {
              const isDone = Boolean(rec.is_completed);
              return (
                <div
                  key={rec.id}
                  className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                    isDone
                      ? "bg-slate-50/70 border-slate-200 text-slate-400"
                      : "bg-white border-slate-200/90 hover:border-brand-300 shadow-xs text-slate-800"
                  }`}
                >
                  <button
                    onClick={() => handleToggle(rec.id, rec.is_completed)}
                    className="mt-0.5 text-slate-400 hover:text-brand-600 transition-colors shrink-0"
                    title={isDone ? "Mark as in-progress" : "Mark as completed"}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    ) : (
                      <Circle className="w-5 h-5 text-slate-300 hover:text-brand-500" />
                    )}
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-brand-50 text-brand-700">
                        {rec.category || "Mindfulness"}
                      </span>
                      <h4 className={`text-sm font-bold truncate ${isDone ? "line-through text-slate-400" : "text-slate-900"}`}>
                        {rec.title}
                      </h4>
                    </div>
                    <p className={`text-xs leading-relaxed ${isDone ? "text-slate-400" : "text-slate-600"}`}>
                      {rec.description}
                    </p>
                  </div>

                  <button
                    onClick={() => handleDelete(rec.id)}
                    className="p-1.5 text-slate-300 hover:text-rose-500 transition-colors rounded-lg hover:bg-rose-50 shrink-0"
                    title="Remove from saved practices"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <SafetyDisclaimer />
    </div>
  );
}
