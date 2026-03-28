import { useState, useEffect } from "react";
import {
  applyLeave,
  getLeaveRequests,
  approveLeave,
  getLeaveBalances,
  initLeaveBalances,
  markAttendance,
  getLeavePatterns,
} from "../api";

const LEAVE_TYPES = ["sick", "casual", "earned", "wfh"];
const ATT_STATUSES = ["present", "wfh", "half_day", "absent"];

export const Leave = () => {
  const [tab, setTab] = useState("apply"); // apply | approve | attendance | ai
  const [requests, setRequests] = useState([]);
  const [balances, setBalances] = useState([]);
  const [patterns, setPatterns] = useState(null);
  const [patternsLoading, setPatternsLoading] = useState(false);
  const [leaveForm, setLeaveForm] = useState({
    employee_id: "",
    leave_type: "sick",
    start_date: "",
    end_date: "",
    reason: "",
  });
  const [attForm, setAttForm] = useState({
    employee_id: "",
    date: "",
    status: "present",
  });
  const [balanceEmpId, setBalanceEmpId] = useState("");

  const tabs = [
    { id: "apply", label: "Apply Leave" },
    { id: "approve", label: "Pending Approvals" },
    { id: "attendance", label: "Mark Attendance" },
    { id: "ai", label: "AI Patterns" },
  ];

  // Load pending requests when approve tab is selected
  useEffect(() => {
    if (tab === "approve") {
      getLeaveRequests({ status: "pending" })
        .then((r) => setRequests(r.data))
        .catch(() => {});
    }
  }, [tab]);

  const handleApplyLeave = async (e) => {
    e.preventDefault();
    try {
      await applyLeave({
        ...leaveForm,
        employee_id: parseInt(leaveForm.employee_id),
      });
      alert("Leave request submitted!");
      setLeaveForm({
        employee_id: "",
        leave_type: "sick",
        start_date: "",
        end_date: "",
        reason: "",
      });
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to submit");
    }
  };

  const handleApproval = async (id, status) => {
    const comment =
      status === "rejected" ? prompt("Rejection reason (optional):") : "";
    try {
      await approveLeave(id, { status, manager_comment: comment || "" });
      setRequests(requests.filter((r) => r.id !== id));
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleFetchBalances = async () => {
    if (!balanceEmpId) return;
    try {
      const res = await getLeaveBalances(balanceEmpId);
      setBalances(res.data);
    } catch {
      // If no balances, we try to initialize first
      try {
        await initLeaveBalances(balanceEmpId);
        const res = await getLeaveBalances(balanceEmpId);
        setBalances(res.data);
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to load balances");
      }
    }
  };

  const handleMarkAttendance = async (e) => {
    e.preventDefault();
    try {
      await markAttendance({
        ...attForm,
        employee_id: parseInt(attForm.employee_id),
      });
      alert("Attendance marked!");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleLeavePatterns = async () => {
    setPatternsLoading(true);
    try {
      const res = await getLeavePatterns();
      setPatterns(res.data);
    } catch {
      alert("Pattern analysis failed. Check Gemini API key.");
    }
    setPatternsLoading(false);
  };

  return (
    <div className='space-y-6'>
      <h1 className='text-2xl font-bold text-gray-800'>Leave & Attendance</h1>

      <div className='flex gap-1 bg-gray-100 rounded-lg p-1 w-fit'>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm rounded-md transition-colors ${
              tab === t.id
                ? "bg-white text-indigo-700 font-medium shadow-sm"
                : "text-gray-600 hover:text-gray-800"
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Apply Leave Tab */}
      {tab === "apply" && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          <form
            onSubmit={handleApplyLeave}
            className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
            <h3 className='font-semibold text-gray-700'>New Leave Request</h3>
            <input
              type='number'
              placeholder='Employee ID'
              value={leaveForm.employee_id}
              onChange={(e) =>
                setLeaveForm({ ...leaveForm, employee_id: e.target.value })
              }
              required
              className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            />
            <select
              value={leaveForm.leave_type}
              onChange={(e) =>
                setLeaveForm({ ...leaveForm, leave_type: e.target.value })
              }
              className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'>
              {LEAVE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </option>
              ))}
            </select>
            <div className='grid grid-cols-2 gap-3'>
              <input
                type='date'
                value={leaveForm.start_date}
                onChange={(e) =>
                  setLeaveForm({ ...leaveForm, start_date: e.target.value })
                }
                required
                className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
              <input
                type='date'
                value={leaveForm.end_date}
                onChange={(e) =>
                  setLeaveForm({ ...leaveForm, end_date: e.target.value })
                }
                required
                className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
            </div>
            <textarea
              placeholder='Reason (optional)'
              value={leaveForm.reason}
              rows={2}
              onChange={(e) =>
                setLeaveForm({ ...leaveForm, reason: e.target.value })
              }
              className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            />
            <button
              type='submit'
              className='w-full px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
              Submit Request
            </button>
          </form>

          {/* Leave Balances */}
          <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
            <h3 className='font-semibold text-gray-700'>Check Leave Balance</h3>
            <div className='flex gap-2'>
              <input
                type='number'
                placeholder='Employee ID'
                value={balanceEmpId}
                onChange={(e) => setBalanceEmpId(e.target.value)}
                className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
              <button
                onClick={handleFetchBalances}
                className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
                Check
              </button>
            </div>
            {balances.length > 0 && (
              <div className='space-y-2 mt-2'>
                {balances.map((b) => (
                  <div
                    key={b.id}
                    className='flex justify-between items-center text-sm'>
                    <span className='capitalize text-gray-700'>
                      {b.leave_type}
                    </span>
                    <div className='flex items-center gap-3'>
                      <span className='text-gray-500'>
                        Used: {b.used}/{b.total}
                      </span>
                      <span className='font-medium text-indigo-600'>
                        Left: {b.total - b.used}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "approve" && (
        <div className='space-y-3'>
          {requests.length ? (
            requests.map((r) => (
              <div
                key={r.id}
                className='bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-gray-800'>
                    Employee #{r.employee_id} —{" "}
                    <span className='capitalize'>{r.leave_type}</span>
                  </p>
                  <p className='text-xs text-gray-500'>
                    {r.start_date} to {r.end_date} · {r.reason || "No reason"}
                  </p>
                </div>
                <div className='flex gap-2'>
                  <button
                    onClick={() => handleApproval(r.id, "approved")}
                    className='px-3 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700'>
                    Approve
                  </button>
                  <button
                    onClick={() => handleApproval(r.id, "rejected")}
                    className='px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700'>
                    Reject
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className='text-gray-400 text-sm bg-white rounded-xl border border-gray-200 p-6 text-center'>
              No pending requests
            </p>
          )}
        </div>
      )}

      {tab === "attendance" && (
        <form
          onSubmit={handleMarkAttendance}
          className='bg-white rounded-xl border border-gray-200 p-5 space-y-3 max-w-md'>
          <h3 className='font-semibold text-gray-700'>Mark Attendance</h3>
          <input
            type='number'
            placeholder='Employee ID'
            value={attForm.employee_id}
            onChange={(e) =>
              setAttForm({ ...attForm, employee_id: e.target.value })
            }
            required
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <input
            type='date'
            value={attForm.date}
            onChange={(e) => setAttForm({ ...attForm, date: e.target.value })}
            required
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <select
            value={attForm.status}
            onChange={(e) => setAttForm({ ...attForm, status: e.target.value })}
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'>
            {ATT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace("_", " ").charAt(0).toUpperCase() +
                  s.replace("_", " ").slice(1)}
              </option>
            ))}
          </select>
          <button
            type='submit'
            className='w-full px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
            Mark Attendance
          </button>
        </form>
      )}

      {/* AI Leave Patterns Analyis Tab */}
      {tab === "ai" && (
        <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-4'>
          <div className='flex items-center justify-between'>
            <h3 className='font-semibold text-gray-700'>
              AI Leave Pattern Analysis
            </h3>
            <button
              onClick={handleLeavePatterns}
              disabled={patternsLoading}
              className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50'>
              {patternsLoading ? "Analyzing..." : "Analyze Patterns"}
            </button>
          </div>
          {patterns ? (
            <div className='space-y-3'>
              {patterns.unusual_patterns?.length > 0 && (
                <div>
                  <h4 className='text-sm font-medium text-red-700 mb-2'>
                    Unusual Patterns Found
                  </h4>
                  {patterns.unusual_patterns.map((p, i) => (
                    <div
                      key={i}
                      className='text-sm text-gray-600 bg-red-50 rounded-lg p-3 mb-2'>
                      <span className='font-medium'>{p.employee}</span>:{" "}
                      {p.pattern}
                      <span
                        className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                          p.severity === "high"
                            ? "bg-red-200 text-red-800"
                            : "bg-amber-200 text-amber-800"
                        }`}>
                        {p.severity}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {patterns.recommendations?.length > 0 && (
                <div>
                  <h4 className='text-sm font-medium text-gray-700 mb-2'>
                    Recommendations
                  </h4>
                  {patterns.recommendations.map((r, i) => (
                    <p key={i} className='text-sm text-gray-600'>
                      • {r}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <p className='text-gray-400 text-sm'>
              Click "Analyze Patterns" to detect unusual leave behavior
            </p>
          )}
        </div>
      )}
    </div>
  );
};
