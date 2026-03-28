import { NavLink, Outlet } from "react-router-dom";
import {
  HiOutlineHome,
  HiOutlineUsers,
  HiOutlineBriefcase,
  HiOutlineCalendar,
  HiOutlineStar,
  HiOutlineAcademicCap,
} from "react-icons/hi";

const navItems = [
  { to: "/", icon: HiOutlineHome, label: "Dashboard" },
  { to: "/employees", icon: HiOutlineUsers, label: "Employees" },
  { to: "/recruitment", icon: HiOutlineBriefcase, label: "Recruitment" },
  { to: "/leave", icon: HiOutlineCalendar, label: "Leave" },
  { to: "/performance", icon: HiOutlineStar, label: "Performance" },
  { to: "/onboarding", icon: HiOutlineAcademicCap, label: "Onboarding" },
];

export const Layout = () => {
  return (
    <div className='flex h-screen bg-gray-50'>
      {/* Sidebar */}
      <aside className='w-60 bg-white border-r border-gray-200 flex flex-col'>
        <div className='p-5 border-b border-gray-200'>
          <h1 className='text-xl font-bold text-indigo-600'>AI HRMS</h1>
          <p className='text-xs text-gray-400 mt-1'>HR Management System</p>
        </div>

        <nav className='flex-1 p-3 space-y-1'>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`
              }>
              <item.icon className='w-5 h-5' />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className='p-4 border-t border-gray-200 text-xs text-gray-400'>
          Powered by Gemini AI
        </div>
      </aside>

      <div className='flex-1 flex flex-col overflow-hidden'>
        {/* Top bar */}
        <header className='bg-white border-b border-gray-200 px-6 py-4'>
          <h2 className='text-lg font-semibold text-gray-800'>
            AI-Powered HRMS
          </h2>
        </header>

        <main className='flex-1 overflow-y-auto p-6'>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
