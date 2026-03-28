export interface Doctor {
  doctor_id: number;
  name: string;
  role: "referring" | "specialist";
  specialty: string | null;
}

export interface Patient {
  id: number;
  health_card_id: string;
  name: string;
  email: string;
  date_of_birth: string;
}

export interface Referral {
  id: number;
  patient_id: number;
  referring_doctor_id: number;
  specialist_type: string;
  urgency: number;
  clinical_note: string;
  status: "pending" | "accepted";
  created_at: string;
  accepted_at: string | null;
  accepted_by_doctor_id: number | null;
  patient_name: string | null;
  referring_doctor_name: string | null;
  is_overdue: boolean;
}

export interface CareThreadEntry {
  id: number;
  patient_id: number;
  referral_id: number | null;
  doctor_id: number;
  entry_type: "referral_created" | "referral_accepted" | "note";
  content: string;
  created_at: string;
  doctor_name: string | null;
}

export interface TranscriptResponse {
  clinical_summary: string;
  suggested_specialist: string;
  suggested_urgency: number;
  key_symptoms: string[];
}

export interface AuthState {
  doctor_id: number;
  name: string;
  role: "referring" | "specialist";
  specialty: string | null;
}

export interface Appointment {
  time: string;
  patientName: string;
  patientId: number;
  type: string;
  duration: string;
}

export interface BookingSlot {
  id: number;
  starts_at: string;
  booked: boolean;
}

export interface BookingPage {
  patient_name: string;
  specialist_name: string;
  specialty: string | null;
  booked_slot: BookingSlot | null;
  slots: BookingSlot[];
}

export interface BookingClaimResult {
  starts_at: string;
  specialist_name: string;
  message: string;
}
