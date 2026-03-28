import { useState, useEffect } from "react";
import {
  HiOutlineUsers,
  HiOutlineBriefcase,
  HiOutlineCalendar,
  HiOutlineTrendingDown,
} from "react-icons/hi";
import StatsCard from "../components/StatsCard";
import {
  getHeadcount,
  getAttrition,
  getPositions,
  getLeaveUtilisation,
  getAISummary,
} from "../api";

export const Dashboard = () => {
  const [headcount, setHeadcount] = useState(null);
  const [attrition, setAttrition] = useState(null);
  const [positions, setPositions] = useState(null);
  const [leaveUtil, setLeaveUtil] = useState([]);
  const [aiSummary, setAiSummary] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    // Fetching all analytics data at the starting
    getHeadcount()
      .then((r) => setHeadcount(r.data))
      .catch(() => {});
    getAttrition()
      .then((r) => setAttrition(r.data))
      .catch(() => {});
    getPositions()
      .then((r) => setPositions(r.data))
      .catch(() => {});
    getLeaveUtilisation()
      .then((r) => setLeaveUtil(r.data))
      .catch(() => {});
  }, []);

  const handleAISummary = async () => {
    setLoadingSummary(true);
    try {
      const res = await getAISummary();
      setAiSummary(res.data.ai_summary);
    } catch {
      setAiSummary("Failed to generate summary. Check your Gemini API key.");
    }
    setLoadingSummary(false);
  };

  return (
    <div className='space-y-6'>
      <h1 className='text-2xl font-bold text-gray-800'>HR Dashboard</h1>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        <StatsCard
          title='Total Employees'
          value={headcount?.total ?? "—"}
          icon={HiOutlineUsers}
          color='indigo'
        />
        <StatsCard
          title='Attrition Rate'
          value={attrition ? `${attrition.attrition_rate_pct}%` : "—"}
          icon={HiOutlineTrendingDown}
          color='red'
        />
        <StatsCard
          title='Open Positions'
          value={positions?.open_positions ?? "—"}
          icon={HiOutlineBriefcase}
          color='amber'
        />
        <StatsCard
          title='Filled Positions'
          value={positions?.filled_positions ?? "—"}
          icon={HiOutlineBriefcase}
          color='green'
        />
      </div>

      <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
        <div className='bg-white rounded-xl border border-gray-200 p-5'>
          <h3 className='font-semibold text-gray-700 mb-3'>
            Headcount by Department
          </h3>
          {headcount?.by_department?.length ? (
            <table className='w-full text-sm'>
              <thead>
                <tr className='text-left text-gray-500 border-b'>
                  <th className='pb-2'>Department</th>
                  <th className='pb-2 text-right'>Count</th>
                </tr>
              </thead>
              <tbody>
                {headcount.by_department.map((d) => (
                  <tr key={d.department} className='border-b border-gray-50'>
                    <td className='py-2 text-gray-700'>{d.department}</td>
                    <td className='py-2 text-right font-medium'>{d.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className='text-gray-400 text-sm'>No employee data yet</p>
          )}
        </div>

        <div className='bg-white rounded-xl border border-gray-200 p-5'>
          <h3 className='font-semibold text-gray-700 mb-3'>
            Leave Utilisation
          </h3>
          {leaveUtil.length ? (
            <div className='space-y-3'>
              {leaveUtil.map((l) => (
                <div key={l.leave_type}>
                  <div className='flex justify-between text-sm mb-1'>
                    <span className='text-gray-600 capitalize'>
                      {l.leave_type}
                    </span>
                    <span className='text-gray-500'>{l.utilisation_pct}%</span>
                  </div>
                  <div className='w-full bg-gray-100 rounded-full h-2'>
                    <div
                      className='bg-indigo-500 h-2 rounded-full transition-all'
                      style={{ width: `${Math.min(l.utilisation_pct, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className='text-gray-400 text-sm'>No leave data yet</p>
          )}
        </div>
      </div>

      <div className='bg-white rounded-xl border border-gray-200 p-5'>
        <div className='flex items-center justify-between mb-3'>
          <h3 className='font-semibold text-gray-700'>AI Monthly Summary</h3>
          <button
            onClick={handleAISummary}
            disabled={loadingSummary}
            className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50'>
            {loadingSummary ? "Generating..." : "Generate Summary"}
          </button>
        </div>
        {aiSummary ? (
          <p className='text-sm text-gray-600 leading-relaxed whitespace-pre-line'>
            {aiSummary}
          </p>
        ) : (
          <p className='text-gray-400 text-sm'>
            Click "Generate Summary" to get an AI-powered monthly HR report
          </p>
        )}
      </div>
    </div>
  );
};
