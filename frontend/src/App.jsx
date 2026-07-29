import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Lawyers from "./pages/Lawyers";
import LawyerProfile from "./pages/LawyerProfile";
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import ChatArea from "./components/chat/ChatArea";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        >
          <Route index element={<ChatArea />} />
          <Route path="profile" element={<Profile />} />
          <Route path="lawyers" element={<Lawyers />} />
          <Route path="lawyers/:id" element={<LawyerProfile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
