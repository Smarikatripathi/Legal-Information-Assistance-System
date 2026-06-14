import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Lawyers from "./pages/Lawyers";
import Profile from "./pages/Profile";
import ProtectedRoute from "./components/ProtectedRoute";

const App = () => {
  return (
  <BrowserRouter>
      <Routes>
        {/* Public */}

        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />

        <Route
          path="/lawyers"
          element={
            <ProtectedRoute>
              <Lawyers />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};


export default App;