import { useState, useEffect } from "react";
import {
  getJobs,
  createJob,
  getCandidates,
  addCandidate,
  uploadResume,
  analyzeResume,
  updateStage,
} from "../api";

const STAGES = [
  "applied",
  "screening",
  "interview",
  "offer",
  "hired",
  "rejected",
];

export const Recruitment = () => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [showJobForm, setShowJobForm] = useState(false);
  const [showCandForm, setShowCandForm] = useState(false);
  const [analyzing, setAnalyzing] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [jobForm, setJobForm] = useState({
    role: "",
    description: "",
    required_skills: "",
    experience_level: "",
  });
  const [candForm, setCandForm] = useState({ name: "", email: "" });

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getJobs();
        setJobs(res.data);
      } catch {
        console.error("Failed to get jobs");
      }
    };
    load();
  }, []);

  const fetchCandidates = async (jobId) => {
    try {
      const res = await getCandidates(jobId);
      setCandidates(res.data);
    } catch {
      console.error("Failed to fetch candidates");
    }
  };

  const selectJob = (job) => {
    setSelectedJob(job);
    setAnalysisResult(null);
    fetchCandidates(job.id);
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    try {
      await createJob(jobForm);
      setJobForm({
        role: "",
        description: "",
        required_skills: "",
        experience_level: "",
      });
      setShowJobForm(false);
      const res = await getJobs();
      setJobs(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleAddCandidate = async (e) => {
    e.preventDefault();
    try {
      await addCandidate(selectedJob.id, candForm);
      setCandForm({ name: "", email: "" });
      setShowCandForm(false);
      fetchCandidates(selectedJob.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleResumeUpload = async (candidateId, file) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await uploadResume(candidateId, formData);
      alert("Resume uploaded!");
      fetchCandidates(selectedJob.id);
    } catch {
      alert("Upload failed");
    }
  };

  const handleAnalyze = async (candidateId) => {
    setAnalyzing(candidateId);
    setAnalysisResult(null);
    try {
      const res = await analyzeResume(candidateId);
      setAnalysisResult(res.data);
      fetchCandidates(selectedJob.id);
    } catch (err) {
      alert(
        err.response?.data?.detail || "Analysis failed. Upload a resume first.",
      );
    }
    setAnalyzing(null);
  };

  const handleStageChange = async (candidateId, stage) => {
    try {
      await updateStage(candidateId, stage);
      fetchCandidates(selectedJob.id);
    } catch {
      alert("Stage update failed");
    }
  };

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold text-gray-800'>Recruitment & ATS</h1>
        <button
          onClick={() => setShowJobForm(!showJobForm)}
          className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
          {showJobForm ? "Cancel" : "New Job Posting"}
        </button>
      </div>

      {/* Creating the job Form */}
      {showJobForm && (
        <form
          onSubmit={handleCreateJob}
          className='bg-white rounded-xl border border-gray-200 p-5 space-y-3'>
          <input
            type='text'
            placeholder='Role (e.g. Senior Backend Developer)'
            value={jobForm.role}
            onChange={(e) => setJobForm({ ...jobForm, role: e.target.value })}
            required
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <textarea
            placeholder='Job Description'
            value={jobForm.description}
            rows={3}
            onChange={(e) =>
              setJobForm({ ...jobForm, description: e.target.value })
            }
            required
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <input
            type='text'
            placeholder='Required Skills (comma separated)'
            value={jobForm.required_skills}
            onChange={(e) =>
              setJobForm({ ...jobForm, required_skills: e.target.value })
            }
            required
            className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
          />
          <div className='flex gap-3'>
            <input
              type='text'
              placeholder='Experience Level (e.g. 3-5 years)'
              value={jobForm.experience_level}
              onChange={(e) =>
                setJobForm({ ...jobForm, experience_level: e.target.value })
              }
              className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            />
            <button
              type='submit'
              className='px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700'>
              Create
            </button>
          </div>
        </form>
      )}

      <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        <div className='bg-white rounded-xl border border-gray-200 p-4'>
          <h3 className='font-semibold text-gray-700 mb-3'>Job Postings</h3>
          {jobs.length ? (
            <div className='space-y-2'>
              {jobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => selectJob(job)}
                  className={`p-3 rounded-lg cursor-pointer border text-sm transition-colors ${
                    selectedJob?.id === job.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-100 hover:bg-gray-50"
                  }`}>
                  <p className='font-medium text-gray-800'>{job.role}</p>
                  <p className='text-xs text-gray-500 mt-1'>
                    {job.experience_level} · {job.status}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className='text-gray-400 text-sm'>No job postings yet</p>
          )}
        </div>

        {/* List of Candidates */}
        <div className='lg:col-span-2 space-y-4'>
          {selectedJob ? (
            <>
              <div className='flex items-center justify-between'>
                <h3 className='font-semibold text-gray-700'>
                  Candidates for: {selectedJob.role}
                </h3>
                <button
                  onClick={() => setShowCandForm(!showCandForm)}
                  className='px-3 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700'>
                  {showCandForm ? "Cancel" : "Add Candidate"}
                </button>
              </div>

              {showCandForm && (
                <form
                  onSubmit={handleAddCandidate}
                  className='bg-white rounded-xl border border-gray-200 p-4 flex gap-3'>
                  <input
                    type='text'
                    placeholder='Candidate Name'
                    value={candForm.name}
                    onChange={(e) =>
                      setCandForm({ ...candForm, name: e.target.value })
                    }
                    required
                    className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                  />
                  <input
                    type='email'
                    placeholder='Email'
                    value={candForm.email}
                    onChange={(e) =>
                      setCandForm({ ...candForm, email: e.target.value })
                    }
                    className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                  />
                  <button
                    type='submit'
                    className='px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700'>
                    Add
                  </button>
                </form>
              )}

              {/* Candidate Cards */}
              <div className='space-y-3'>
                {candidates.length ? (
                  candidates.map((c) => (
                    <div
                      key={c.id}
                      className='bg-white rounded-xl border border-gray-200 p-4'>
                      <div className='flex items-center justify-between mb-3'>
                        <div>
                          <p className='font-medium text-gray-800'>{c.name}</p>
                          <p className='text-xs text-gray-500'>{c.email}</p>
                        </div>
                        <div className='flex items-center gap-2'>
                          <select
                            value={c.stage}
                            onChange={(e) =>
                              handleStageChange(c.id, e.target.value)
                            }
                            className='text-xs border border-gray-300 rounded-lg px-2 py-1 focus:outline-none'>
                            {STAGES.map((s) => (
                              <option key={s} value={s}>
                                {s.charAt(0).toUpperCase() + s.slice(1)}
                              </option>
                            ))}
                          </select>
                          {c.match_score && (
                            <span
                              className={`text-xs font-bold px-2 py-1 rounded-full ${
                                c.match_score >= 70
                                  ? "bg-green-50 text-green-700"
                                  : c.match_score >= 40
                                    ? "bg-amber-50 text-amber-700"
                                    : "bg-red-50 text-red-700"
                              }`}>
                              {c.match_score}%
                            </span>
                          )}
                        </div>
                      </div>

                      <div className='flex gap-2'>
                        {/* Resume Upload Section */}
                        <label className='text-xs px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg cursor-pointer hover:bg-gray-200'>
                          {c.resume_path ? "Re-upload Resume" : "Upload Resume"}
                          <input
                            type='file'
                            accept='.pdf'
                            className='hidden'
                            onChange={(e) =>
                              e.target.files[0] &&
                              handleResumeUpload(c.id, e.target.files[0])
                            }
                          />
                        </label>
                        {/* AI Analysis button */}
                        <button
                          onClick={() => handleAnalyze(c.id)}
                          disabled={analyzing === c.id}
                          className='text-xs px-3 py-1.5 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 disabled:opacity-50'>
                          {analyzing === c.id ? "Analyzing..." : "AI Analyze"}
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className='text-gray-400 text-sm'>
                    No candidates yet. Add one above.
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className='bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400'>
              Select a job posting to view candidates
            </div>
          )}
        </div>
      </div>

      {/* AI Analysis Result Panel */}
      {analysisResult && (
        <div className='bg-white rounded-xl border border-indigo-200 p-5 space-y-4'>
          <div className='flex items-center justify-between'>
            <h3 className='font-semibold text-gray-700'>
              AI Resume Analysis: {analysisResult.candidate_name}
            </h3>
            <span
              className={`text-lg font-bold px-3 py-1 rounded-full ${
                analysisResult.match_score >= 70
                  ? "bg-green-50 text-green-700"
                  : analysisResult.match_score >= 40
                    ? "bg-amber-50 text-amber-700"
                    : "bg-red-50 text-red-700"
              }`}>
              {analysisResult.match_score}% Match
            </span>
          </div>

          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <div>
              <h4 className='text-sm font-medium text-green-700 mb-2'>
                Top Strengths
              </h4>
              <ul className='space-y-1'>
                {analysisResult.strengths?.map((s, i) => (
                  <li
                    key={i}
                    className='text-sm text-gray-600 flex items-start gap-2'>
                    <span className='text-green-500 mt-0.5'>✓</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className='text-sm font-medium text-red-700 mb-2'>Gaps</h4>
              <ul className='space-y-1'>
                {analysisResult.gaps?.map((g, i) => (
                  <li
                    key={i}
                    className='text-sm text-gray-600 flex items-start gap-2'>
                    <span className='text-red-500 mt-0.5'>✗</span> {g}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div>
            <h4 className='text-sm font-medium text-gray-700 mb-2'>
              AI-Generated Interview Questions
            </h4>
            <ol className='space-y-1 list-decimal list-inside'>
              {analysisResult.interview_questions?.map((q, i) => (
                <li key={i} className='text-sm text-gray-600'>
                  {q}
                </li>
              ))}
            </ol>
          </div>

          <p className='text-sm text-gray-500 italic'>
            {analysisResult.summary}
          </p>
        </div>
      )}
    </div>
  );
};
