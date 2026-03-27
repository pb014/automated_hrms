import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import Recruitment from "./pages/Recruitment";
import Leave from "./pages/Leave";
import Performance from "./pages/Performance";
import Onboarding from "./pages/Onboarding";

export const App = () => {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path='employees' element={<Employees />} />
          <Route path='recruitment' element={<Recruitment />} />
          <Route path='leave' element={<Leave />} />
          <Route path='performance' element={<Performance />} />
          <Route path='onboarding' element={<Onboarding />} />
        </Route>
      </Routes>
    </Router>
  );
};
