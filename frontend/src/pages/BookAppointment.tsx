import { useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { CalendarClock, CheckCircle2, Loader2, Stethoscope } from "lucide-react";
import { claimBookingSlot, getBookingPage } from "../api/client";
import type { BookingPage } from "../types";

function formatSlot(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function BookAppointment() {
  const { referralId } = useParams<{ referralId: string }>();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [data, setData] = useState<BookingPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [claimingId, setClaimingId] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState("");

  const rid = referralId ? parseInt(referralId, 10) : NaN;

  const load = useCallback(async () => {
    if (!Number.isFinite(rid) || !token) {
      setError("Missing booking link. Open the full link from your email.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const page = await getBookingPage(rid, token);
      setData(page);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load booking page");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [rid, token]);

  useEffect(() => {
    load();
  }, [load]);

  async function onPickSlot(slotId: number) {
    if (!Number.isFinite(rid) || !token) return;
    setClaimingId(slotId);
    setError("");
    try {
      const res = await claimBookingSlot(rid, { token, slot_id: slotId });
      setSuccessMessage(res.message);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Booking failed");
    } finally {
      setClaimingId(null);
    }
  }

  const openSlots = data?.slots.filter((s) => !s.booked) ?? [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-teal-600 rounded-2xl mb-3">
            <Stethoscope className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Book your visit</h1>
          <p className="text-gray-500 text-sm mt-1">MedRelay · specialist appointment</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          {loading && (
            <div className="flex items-center justify-center gap-2 text-teal-700 py-12">
              <Loader2 className="w-6 h-6 animate-spin" />
              Loading available times…
            </div>
          )}

          {!loading && error && (
            <p className="text-red-600 text-sm text-center py-4">{error}</p>
          )}

          {!loading && !error && data && (
            <>
              <p className="text-gray-700 mb-1">
                Hi <span className="font-semibold">{data.patient_name}</span>,
              </p>
              <p className="text-gray-600 text-sm mb-6">
                Choose a time with{" "}
                <span className="font-medium text-gray-800">{data.specialist_name}</span>
                {data.specialty
                  ? ` (${data.specialty.replace(/_/g, " ")})`
                  : null}
                . Times already taken are hidden.
              </p>

              {successMessage && (
                <div className="mb-4 flex gap-2 items-start rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-sm p-3">
                  <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
                  <span>{successMessage}</span>
                </div>
              )}

              {data.booked_slot && (
                <div className="mb-6 rounded-xl bg-teal-50 border border-teal-100 p-4">
                  <div className="flex items-center gap-2 text-teal-900 font-medium text-sm mb-1">
                    <CalendarClock className="w-4 h-4" />
                    Your appointment
                  </div>
                  <p className="text-teal-800">{formatSlot(data.booked_slot.starts_at)}</p>
                </div>
              )}

              {!data.booked_slot && openSlots.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-6">
                  No open slots right now. Please contact the clinic.
                </p>
              )}

              {!data.booked_slot && openSlots.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                    Available times
                  </p>
                  <ul className="grid gap-2 sm:grid-cols-2">
                    {openSlots.map((s) => (
                      <li key={s.id}>
                        <button
                          type="button"
                          disabled={claimingId !== null}
                          onClick={() => onPickSlot(s.id)}
                          className="w-full text-left px-4 py-3 rounded-xl border border-teal-200 bg-white hover:bg-teal-50 hover:border-teal-300 text-gray-900 text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {claimingId === s.id ? (
                            <span className="flex items-center gap-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              Booking…
                            </span>
                          ) : (
                            formatSlot(s.starts_at)
                          )}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
