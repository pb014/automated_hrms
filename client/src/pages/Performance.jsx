import { useState, useEffect } from "react";
import {
  getCycles,
  createCycle,
  addEmployeesToCycle,
  getCycleReviews,
  submitSelfAssessment,
  submitManagerReview,
  generateReviewSummary,
  getReview,
} from "../api";

const RATING_PARAMS = [
  "quality",
  "delivery",
  "communication",
  "initiative",
  "teamwork",
];

export const Performance = () => {
  const [cycles, setCycles] = useState([]);
  const [selectedCycle, setSelectedCycle] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [selectedReview, setSelectedReview] = useState(null);
  const [showCycleForm, setShowCycleForm] = useState(false);
  const [addEmpIds, setAddEmpIds] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [cycleForm, setCycleForm] = useState({
    period_name: "",
    start_date: "",
    end_date: "",
  });
  const [selfForm, setSelfForm] = useState({
    self_assessment: "",
    self_rating: 3,
  });
  const [mgrForm, setMgrForm] = useState({
    manager_ratings: {
      quality: 3,
      delivery: 3,
      communication: 3,
      initiative: 3,
      teamwork: 3,
    },
    manager_comment: "",
  });

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getCycles();
        setCycles(res.data);
      } catch (error) {
        console.error(error);
      }
    };
    load();
  }, []);

  const fetchReviews = async (cycleId) => {
    try {
      const res = await getCycleReviews(cycleId);
      setReviews(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const selectCycle = (cycle) => {
    setSelectedCycle(cycle);
    setSelectedReview(null);
    fetchReviews(cycle.id);
  };

  const handleCreateCycle = async (e) => {
    e.preventDefault();
    try {
      await createCycle(cycleForm);
      setCycleForm({ period_name: "", start_date: "", end_date: "" });
      setShowCycleForm(false);
      const res = await getCycles();
      setCycles(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleAddEmployees = async () => {
    if (!addEmpIds.trim()) return;
    const ids = addEmpIds
      .split(",")
      .map((id) => parseInt(id.trim()))
      .filter((n) => !isNaN(n));
    try {
      const res = await addEmployeesToCycle(selectedCycle.id, ids);
      alert(res.data.message);
      setAddEmpIds("");
      fetchReviews(selectedCycle.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleSelectReview = async (review) => {
    try {
      const res = await getReview(review.id);
      setSelectedReview(res.data);
    } catch {
      setSelectedReview(review);
    }
  };

  const handleSelfAssessment = async () => {
    try {
      await submitSelfAssessment(selectedReview.id, selfForm);
      alert("Self-assessment submitted!");
      handleSelectReview(selectedReview);
      fetchReviews(selectedCycle.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleManagerReview = async () => {
    try {
      await submitManagerReview(selectedReview.id, mgrForm);
      alert("Manager review submitted!");
      handleSelectReview(selectedReview);
      fetchReviews(selectedCycle.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    try {
      await generateReviewSummary(selectedReview.id);
      handleSelectReview(selectedReview);
      fetchReviews(selectedCycle.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Both assessments needed first");
    }
    setSummaryLoading(false);
  };

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold text-gray-800'>
          Performance Reviews
        </h1>
        <button
          onClick={() => setShowCycleForm(!showCycleForm)}
          className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
          {showCycleForm ? "Cancel" : "New Cycle"}
        </button>
      </div>

      {showCycleForm && (
        <form
          onSubmit={handleCreateCycle}
          className='bg-white rounded-xl border border-gray-200 p-5 flex gap-3 items-end'>
          <input
            type='text'
            placeholder='Period (e.g. Q2 2025)'
            value={cycleForm.period_name}
            onChange={(e) =>
              setCycleForm({ ...cycleForm, period_name: e.target.value })
            }
            required
            className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <input
            type='date'
            value={cycleForm.start_date}
            onChange={(e) =>
              setCycleForm({ ...cycleForm, start_date: e.target.value })
            }
            required
            className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <input
            type='date'
            value={cycleForm.end_date}
            onChange={(e) =>
              setCycleForm({ ...cycleForm, end_date: e.target.value })
            }
            required
            className='border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <button
            type='submit'
            className='px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700'>
            Create
          </button>
        </form>
      )}

      <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        {/* Cycles + Reviews List */}
        <div className='space-y-4'>
          <div className='bg-white rounded-xl border border-gray-200 p-4'>
            <h3 className='font-semibold text-gray-700 mb-3'>Review Cycles</h3>
            {cycles.length ? (
              cycles.map((c) => (
                <div
                  key={c.id}
                  onClick={() => selectCycle(c)}
                  className={`p-3 rounded-lg cursor-pointer border text-sm mb-2 transition-colors ${
                    selectedCycle?.id === c.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-100 hover:bg-gray-50"
                  }`}>
                  <p className='font-medium text-gray-800'>{c.period_name}</p>
                  <p className='text-xs text-gray-500'>
                    {c.start_date} to {c.end_date}
                  </p>
                </div>
              ))
            ) : (
              <p className='text-gray-400 text-sm'>No cycles yet</p>
            )}
          </div>

          {selectedCycle && (
            <div className='bg-white rounded-xl border border-gray-200 p-4'>
              <h3 className='font-semibold text-gray-700 mb-2'>
                Add Employees
              </h3>
              <div className='flex gap-2'>
                <input
                  type='text'
                  placeholder='IDs: 1,2,3'
                  value={addEmpIds}
                  onChange={(e) => setAddEmpIds(e.target.value)}
                  className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                />
                <button
                  onClick={handleAddEmployees}
                  className='px-3 py-2 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700'>
                  Add
                </button>
              </div>

              <h3 className='font-semibold text-gray-700 mt-4 mb-2'>Reviews</h3>
              {reviews.length ? (
                reviews.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => handleSelectReview(r)}
                    className={`p-3 rounded-lg cursor-pointer border text-sm mb-2 ${
                      selectedReview?.id === r.id
                        ? "border-indigo-500 bg-indigo-50"
                        : "border-gray-100 hover:bg-gray-50"
                    }`}>
                    <p className='text-gray-800'>Employee #{r.employee_id}</p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        r.status === "completed"
                          ? "bg-green-50 text-green-700"
                          : "bg-amber-50 text-amber-700"
                      }`}>
                      {r.status}
                    </span>
                  </div>
                ))
              ) : (
                <p className='text-gray-400 text-sm'>No employees added yet</p>
              )}
            </div>
          )}
        </div>

        {/* Review Detail Panel */}
        <div className='lg:col-span-2'>
          {selectedReview ? (
            <div className='space-y-4'>
              <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
                <h3 className='font-semibold text-gray-700'>Self Assessment</h3>
                {selectedReview.self_assessment ? (
                  <div className='text-sm text-gray-600 bg-gray-50 rounded-lg p-3'>
                    <p>{selectedReview.self_assessment}</p>
                    <p className='mt-1 font-medium'>
                      Self Rating: {selectedReview.self_rating}/5
                    </p>
                  </div>
                ) : (
                  <>
                    <textarea
                      rows={3}
                      placeholder='Describe your achievements, challenges, and goals...'
                      value={selfForm.self_assessment}
                      onChange={(e) =>
                        setSelfForm({
                          ...selfForm,
                          self_assessment: e.target.value,
                        })
                      }
                      className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                    />
                    <div className='flex items-center gap-3'>
                      <label className='text-sm text-gray-600'>Rating:</label>
                      <input
                        type='range'
                        min='1'
                        max='5'
                        step='0.5'
                        value={selfForm.self_rating}
                        onChange={(e) =>
                          setSelfForm({
                            ...selfForm,
                            self_rating: parseFloat(e.target.value),
                          })
                        }
                        className='flex-1'
                      />
                      <span className='text-sm font-medium w-8'>
                        {selfForm.self_rating}
                      </span>
                    </div>
                    <button
                      onClick={handleSelfAssessment}
                      className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
                      Submit
                    </button>
                  </>
                )}
              </div>

              {/* Manager Review Submission */}
              <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
                <h3 className='font-semibold text-gray-700'>Manager Review</h3>
                {selectedReview.manager_ratings ? (
                  <div className='text-sm text-gray-600 bg-gray-50 rounded-lg p-3 space-y-1'>
                    {Object.entries(selectedReview.manager_ratings).map(
                      ([k, v]) => (
                        <p key={k} className='capitalize'>
                          {k}: <span className='font-medium'>{v}/5</span>
                        </p>
                      ),
                    )}
                    {selectedReview.manager_comment && (
                      <p className='mt-2 italic'>
                        {selectedReview.manager_comment}
                      </p>
                    )}
                  </div>
                ) : (
                  <>
                    {RATING_PARAMS.map((param) => (
                      <div key={param} className='flex items-center gap-3'>
                        <label className='text-sm text-gray-600 capitalize w-32'>
                          {param}
                        </label>
                        <input
                          type='range'
                          min='1'
                          max='5'
                          value={mgrForm.manager_ratings[param]}
                          onChange={(e) =>
                            setMgrForm({
                              ...mgrForm,
                              manager_ratings: {
                                ...mgrForm.manager_ratings,
                                [param]: parseInt(e.target.value),
                              },
                            })
                          }
                          className='flex-1'
                        />
                        <span className='text-sm font-medium w-6'>
                          {mgrForm.manager_ratings[param]}
                        </span>
                      </div>
                    ))}
                    <textarea
                      rows={2}
                      placeholder='Manager comment (optional)'
                      value={mgrForm.manager_comment}
                      onChange={(e) =>
                        setMgrForm({
                          ...mgrForm,
                          manager_comment: e.target.value,
                        })
                      }
                      className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                    />
                    <button
                      onClick={handleManagerReview}
                      className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
                      Submit
                    </button>
                  </>
                )}
              </div>

              <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
                <div className='flex items-center justify-between'>
                  <h3 className='font-semibold text-gray-700'>
                    AI Review Summary
                  </h3>
                  {!selectedReview.ai_summary && (
                    <button
                      onClick={handleGenerateSummary}
                      disabled={summaryLoading}
                      className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50'>
                      {summaryLoading ? "Generating..." : "Generate AI Summary"}
                    </button>
                  )}
                </div>
                {selectedReview.ai_summary ? (
                  <div className='space-y-3'>
                    <p className='text-sm text-gray-600 leading-relaxed'>
                      {selectedReview.ai_summary}
                    </p>
                    {selectedReview.ai_flags &&
                      JSON.parse(selectedReview.ai_flags).length > 0 && (
                        <div>
                          <h4 className='text-sm font-medium text-red-700 mb-1'>
                            Mismatches Flagged
                          </h4>
                          {JSON.parse(selectedReview.ai_flags).map((f, i) => (
                            <p
                              key={i}
                              className='text-sm text-red-600 bg-red-50 rounded-lg p-2 mb-1'>
                              ⚠ {f}
                            </p>
                          ))}
                        </div>
                      )}
                    {selectedReview.ai_development_actions &&
                      JSON.parse(selectedReview.ai_development_actions).length >
                        0 && (
                        <div>
                          <h4 className='text-sm font-medium text-indigo-700 mb-1'>
                            Development Actions
                          </h4>
                          {JSON.parse(
                            selectedReview.ai_development_actions,
                          ).map((a, i) => (
                            <p
                              key={i}
                              className='text-sm text-gray-600 bg-indigo-50 rounded-lg p-2 mb-1'>
                              → {a}
                            </p>
                          ))}
                        </div>
                      )}
                  </div>
                ) : (
                  <p className='text-gray-400 text-sm'>
                    Submit both assessments first, then generate AI summary
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className='bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400'>
              Select a review cycle and an employee to begin
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
