import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import type { AuthState } from "./types";
import Login from "./pages/Login";
import DoctorSession from "./pages/DoctorSession";
import SpecialistFeed from "./pages/SpecialistFeed";
import PatientThread from "./pages/PatientThread";
import BookAppointment from "./pages/BookAppointment";

function getAuth(): AuthState | null {
  const raw = localStorage.getItem("medrelay_auth");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthState;
  } catch {
    return null;
  }
}

export default function App() {
  const [auth, setAuth] = useState<AuthState | null>(getAuth);

  useEffect(() => {
    const handler = () => setAuth(getAuth());
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  function handleLogin(state: AuthState) {
    localStorage.setItem("medrelay_auth", JSON.stringify(state));
    setAuth(state);
  }

  function handleLogout() {
    localStorage.removeItem("medrelay_auth");
    setAuth(null);
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            auth ? (
              <Navigate
                to={auth.role === "referring" ? "/session" : "/feed"}
                replace
              />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/session"
          element={
            auth?.role === "referring" ? (
              <DoctorSession auth={auth} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/feed"
          element={
            auth?.role === "specialist" ? (
              <SpecialistFeed auth={auth} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/patient/:patientId/thread"
          element={
            auth ? (
              <PatientThread auth={auth} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/book/:referralId" element={<BookAppointment />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
