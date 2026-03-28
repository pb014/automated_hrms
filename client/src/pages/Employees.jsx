import { useState, useEffect } from "react";
import {
  getEmployees,
  createEmployee,
  generateBio,
  deactivateEmployee,
  exportCSV,
} from "../api";

export const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [bioLoading, setBioLoading] = useState(null); // tracks which employee's bio is generating
  const [form, setForm] = useState({
    name: "",
    email: "",
    designation: "",
    department: "",
    joining_date: "",
    contact: "",
  });

  const fetchEmployees = async () => {
    try {
      const res = await getEmployees({ search: search || undefined });
      setEmployees(res.data);
    } catch {
      console.error("Failed to fetch employees");
    }
  };

  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const res = await getEmployees();
        setEmployees(res.data);
      } catch {
        console.error("Failed to fetch employees");
      }
    };
    loadEmployees();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchEmployees();
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createEmployee(form);
      setForm({
        name: "",
        email: "",
        designation: "",
        department: "",
        joining_date: "",
        contact: "",
      });
      setShowForm(false);
      fetchEmployees();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create employee");
    }
    setLoading(false);
  };

  const handleGenerateBio = async (id) => {
    setBioLoading(id);
    try {
      const res = await generateBio(id);
      alert(`Bio generated: ${res.data.bio}`);
      fetchEmployees();
    } catch {
      alert("Bio generation failed. Check Gemini API key.");
    }
    setBioLoading(null);
  };

  const handleDeactivate = async (id, name) => {
    if (!confirm(`Deactivate ${name}?`)) return;
    try {
      await deactivateEmployee(id);
      fetchEmployees();
    } catch {
      alert("Failed to deactivate");
    }
  };

  const handleExportCSV = async () => {
    try {
      const res = await exportCSV();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "employees.csv";
      a.click();
    } catch {
      alert("Export failed");
    }
  };

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold text-gray-800'>Employees</h1>
        <div className='flex gap-2'>
          <button
            onClick={handleExportCSV}
            className='px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50'>
            Export CSV
          </button>
          <button
            onClick={() => setShowForm(!showForm)}
            className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
            {showForm ? "Cancel" : "Add Employee"}
          </button>
        </div>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className='bg-white rounded-xl border border-gray-200 p-5 grid grid-cols-1 md:grid-cols-3 gap-4'>
          {["name", "email", "designation", "department", "contact"].map(
            (field) => (
              <input
                key={field}
                type='text'
                placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
                value={form[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                required={field !== "contact"}
                className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
            ),
          )}
          <input
            type='date'
            value={form.joining_date}
            onChange={(e) => setForm({ ...form, joining_date: e.target.value })}
            required
            className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <button
            type='submit'
            disabled={loading}
            className='px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50'>
            {loading ? "Creating..." : "Create Employee"}
          </button>
        </form>
      )}

      {/* Search Bar */}
      <form onSubmit={handleSearch} className='flex gap-2'>
        <input
          type='text'
          placeholder='Search by name, email, department, designation...'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className='flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
        />
        <button
          type='submit'
          className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
          Search
        </button>
      </form>

      {/* Employee Table */}
      <div className='bg-white rounded-xl border border-gray-200 overflow-hidden'>
        <table className='w-full text-sm'>
          <thead className='bg-gray-50 border-b border-gray-200'>
            <tr className='text-left text-gray-500'>
              <th className='px-4 py-3'>Name</th>
              <th className='px-4 py-3'>Email</th>
              <th className='px-4 py-3'>Designation</th>
              <th className='px-4 py-3'>Department</th>
              <th className='px-4 py-3'>Joined</th>
              <th className='px-4 py-3'>Status</th>
              <th className='px-4 py-3'>Actions</th>
            </tr>
          </thead>
          <tbody>
            {employees.length ? (
              employees.map((emp) => (
                <tr
                  key={emp.id}
                  className='border-b border-gray-50 hover:bg-gray-50'>
                  <td className='px-4 py-3 font-medium text-gray-800'>
                    {emp.name}
                  </td>
                  <td className='px-4 py-3 text-gray-600'>{emp.email}</td>
                  <td className='px-4 py-3 text-gray-600'>{emp.designation}</td>
                  <td className='px-4 py-3 text-gray-600'>{emp.department}</td>
                  <td className='px-4 py-3 text-gray-600'>
                    {emp.joining_date}
                  </td>
                  <td className='px-4 py-3'>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        emp.is_active
                          ? "bg-green-50 text-green-700"
                          : "bg-red-50 text-red-700"
                      }`}>
                      {emp.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className='px-4 py-3'>
                    <div className='flex gap-2'>
                      <button
                        onClick={() => handleGenerateBio(emp.id)}
                        disabled={bioLoading === emp.id}
                        className='text-xs px-2 py-1 bg-indigo-50 text-indigo-600 rounded hover:bg-indigo-100'>
                        {bioLoading === emp.id ? "..." : "AI Bio"}
                      </button>
                      {emp.is_active && (
                        <button
                          onClick={() => handleDeactivate(emp.id, emp.name)}
                          className='text-xs px-2 py-1 bg-red-50 text-red-600 rounded hover:bg-red-100'>
                          Deactivate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className='px-4 py-8 text-center text-gray-400'>
                  No employees found. Add your first employee above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
