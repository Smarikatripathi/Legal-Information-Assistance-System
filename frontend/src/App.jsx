import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";

import Lawyers from "./pages/Lawyers";
import Profile from "./pages/Profile";
import ProtectedRoute from "./components/ProtectedRoute";
import ChatArea from "./components/ChatArea";

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
          }>
           <Route index element ={<ChatArea/>}/> 
           <Route path=":conversationId" element={<ChatArea />} />
             <Route
          path="profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
       </Route>
        <Route
          path="/lawyers"
          element={
            <ProtectedRoute>
              <Lawyers />
            </ProtectedRoute>
          }
        />


      </Routes>
    </BrowserRouter>
  );
};


export default App;