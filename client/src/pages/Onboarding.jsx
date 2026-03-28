import { useState, useEffect } from "react";
import {
  createChecklist,
  getChecklists,
  assignChecklist,
  getProgress,
  completeItem,
  uploadPolicy,
  getPolicies,
  askChatbot,
  getTopQuestions,
} from "../api";

export const Onboarding = () => {
  const [tab, setTab] = useState("checklists"); // checklists | chatbot | policies
  const [checklists, setChecklists] = useState([]);
  const [progress, setProgress] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [topQuestions, setTopQuestions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [progressEmpId, setProgressEmpId] = useState("");
  const [showChecklistForm, setShowChecklistForm] = useState(false);
  const [assignForm, setAssignForm] = useState({
    employee_id: "",
    checklist_id: "",
  });
  const [checklistForm, setChecklistForm] = useState({
    role: "",
    itemsText: "",
  });

  const tabs = [
    { id: "checklists", label: "Checklists" },
    { id: "chatbot", label: "AI Chatbot" },
    { id: "policies", label: "Policy Documents" },
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getChecklists();
        setChecklists(res.data);
      } catch (error) {
        console.error(error);
      }
    };
    load();
  }, []);

  const handleCreateChecklist = async (e) => {
    e.preventDefault();
    // Convert comma-separated tasks into JSON items
    const items = checklistForm.itemsText
      .split("\n")
      .filter(Boolean)
      .map((line, i) => ({
        task: line.trim(),
        due_days: (i + 1) * 3,
        assignee: "HR",
      }));
    try {
      await createChecklist({ role: checklistForm.role, items });
      setChecklistForm({ role: "", itemsText: "" });
      setShowChecklistForm(false);
      const res = await getChecklists();
      setChecklists(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleAssign = async () => {
    if (!assignForm.employee_id || !assignForm.checklist_id) return;
    try {
      await assignChecklist(assignForm.employee_id, assignForm.checklist_id);
      alert("Checklist assigned!");
      setAssignForm({ employee_id: "", checklist_id: "" });
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleFetchProgress = async () => {
    if (!progressEmpId) return;
    try {
      const res = await getProgress(progressEmpId);
      setProgress(res.data);
    } catch {
      setProgress([]);
    }
  };

  const handleCompleteItem = async (progressId, itemIndex) => {
    try {
      await completeItem(progressId, itemIndex);
      handleFetchProgress();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed");
    }
  };

  const handleUploadPolicy = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await uploadPolicy(formData);
      alert("Policy uploaded and indexed for chatbot!");
      const res = await getPolicies();
      setPolicies(res.data);
    } catch {
      alert("Upload failed");
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const question = chatInput;
    setChatMessages((prev) => [...prev, { role: "user", text: question }]);
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await askChatbot({ question, employee_id: null });
      setChatMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: res.data.answer,
          could_answer: res.data.could_answer,
        },
      ]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Sorry, something went wrong.",
          could_answer: false,
        },
      ]);
    }
    setChatLoading(false);
  };

  const loadPoliciesTab = async () => {
    setTab("policies");
    try {
      const res = await getPolicies();
      setPolicies(res.data);
      const tq = await getTopQuestions();
      setTopQuestions(tq.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className='space-y-6'>
      <h1 className='text-2xl font-bold text-gray-800'>Onboarding Assistant</h1>

      <div className='flex gap-1 bg-gray-100 rounded-lg p-1 w-fit'>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() =>
              t.id === "policies" ? loadPoliciesTab() : setTab(t.id)
            }
            className={`px-4 py-2 text-sm rounded-md transition-colors ${
              tab === t.id
                ? "bg-white text-indigo-700 font-medium shadow-sm"
                : "text-gray-600 hover:text-gray-800"
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Checklists Tab */}
      {tab === "checklists" && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          <div className='space-y-4'>
            <div className='flex items-center justify-between'>
              <h3 className='font-semibold text-gray-700'>
                Checklist Templates
              </h3>
              <button
                onClick={() => setShowChecklistForm(!showChecklistForm)}
                className='px-3 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700'>
                {showChecklistForm ? "Cancel" : "New Checklist"}
              </button>
            </div>

            {showChecklistForm && (
              <form
                onSubmit={handleCreateChecklist}
                className='bg-white rounded-xl border border-gray-200 p-4 space-y-3'>
                <input
                  type='text'
                  placeholder='Role (e.g. Software Engineer)'
                  value={checklistForm.role}
                  onChange={(e) =>
                    setChecklistForm({ ...checklistForm, role: e.target.value })
                  }
                  required
                  className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                />
                <textarea
                  rows={4}
                  placeholder='One task per line:&#10;Submit ID proof&#10;Set up laptop&#10;Complete compliance training'
                  value={checklistForm.itemsText}
                  onChange={(e) =>
                    setChecklistForm({
                      ...checklistForm,
                      itemsText: e.target.value,
                    })
                  }
                  required
                  className='w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                />
                <button
                  type='submit'
                  className='px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700'>
                  Create
                </button>
              </form>
            )}

            {checklists.map((cl) => (
              <div
                key={cl.id}
                className='bg-white rounded-xl border border-gray-200 p-4'>
                <p className='font-medium text-gray-800'>{cl.role}</p>
                <p className='text-xs text-gray-500 mt-1'>
                  {cl.items?.length || 0} items · ID: {cl.id}
                </p>
              </div>
            ))}

            {/* Assign Checklist */}
            <div className='bg-white rounded-xl border border-gray-200 p-4 space-y-2'>
              <h3 className='font-semibold text-gray-700 text-sm'>
                Assign to Employee
              </h3>
              <div className='flex gap-2'>
                <input
                  type='number'
                  placeholder='Employee ID'
                  value={assignForm.employee_id}
                  onChange={(e) =>
                    setAssignForm({
                      ...assignForm,
                      employee_id: e.target.value,
                    })
                  }
                  className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                />
                <input
                  type='number'
                  placeholder='Checklist ID'
                  value={assignForm.checklist_id}
                  onChange={(e) =>
                    setAssignForm({
                      ...assignForm,
                      checklist_id: e.target.value,
                    })
                  }
                  className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
                />
                <button
                  onClick={handleAssign}
                  className='px-3 py-2 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700'>
                  Assign
                </button>
              </div>
            </div>
          </div>

          {/* Progress Tracking */}
          <div className='space-y-4'>
            <h3 className='font-semibold text-gray-700'>Employee Progress</h3>
            <div className='flex gap-2'>
              <input
                type='number'
                placeholder='Employee ID'
                value={progressEmpId}
                onChange={(e) => setProgressEmpId(e.target.value)}
                className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              />
              <button
                onClick={handleFetchProgress}
                className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700'>
                View
              </button>
            </div>

            {progress.map((p) => (
              <div
                key={p.progress_id}
                className='bg-white rounded-xl border border-gray-200 p-4'>
                <div className='flex justify-between items-center mb-3'>
                  <p className='font-medium text-gray-800'>{p.role}</p>
                  <span className='text-xs text-indigo-600 font-medium'>
                    {p.percentage}% complete
                  </span>
                </div>
                <div className='w-full bg-gray-100 rounded-full h-2 mb-3'>
                  <div
                    className='bg-indigo-500 h-2 rounded-full transition-all'
                    style={{ width: `${p.percentage}%` }}
                  />
                </div>
                <div className='space-y-2'>
                  {p.items?.map((item, idx) => (
                    <label
                      key={idx}
                      className='flex items-center gap-2 text-sm cursor-pointer'>
                      <input
                        type='checkbox'
                        checked={p.completed_items?.includes(idx)}
                        onChange={() => handleCompleteItem(p.progress_id, idx)}
                        className='rounded border-gray-300'
                      />
                      <span
                        className={
                          p.completed_items?.includes(idx)
                            ? "line-through text-gray-400"
                            : "text-gray-700"
                        }>
                        {item.task}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Chatbot Tab */}
      {tab === "chatbot" && (
        <div
          className='bg-white rounded-xl border border-gray-200 flex flex-col'
          style={{ height: "500px" }}>
          {/* Chat Messages */}
          <div className='flex-1 overflow-y-auto p-4 space-y-3'>
            {chatMessages.length === 0 && (
              <p className='text-gray-400 text-sm text-center mt-8'>
                Ask any question about company policies, leave rules, tools,
                etc.
                <br />
                <span className='text-xs'>
                  Make sure to upload policy documents in the Policies tab
                  first.
                </span>
              </p>
            )}
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[75%] px-4 py-2.5 rounded-xl text-sm ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : msg.could_answer === false
                        ? "bg-amber-50 text-amber-800 border border-amber-200"
                        : "bg-gray-100 text-gray-700"
                  }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className='flex justify-start'>
                <div className='bg-gray-100 text-gray-500 px-4 py-2.5 rounded-xl text-sm'>
                  Thinking...
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form
            onSubmit={handleChat}
            className='border-t border-gray-200 p-3 flex gap-2'>
            <input
              type='text'
              placeholder='Ask about policies, leave rules, tools...'
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className='flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            />
            <button
              type='submit'
              disabled={chatLoading}
              className='px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50'>
              Send
            </button>
          </form>
        </div>
      )}

      {/* Policies Tab */}
      {tab === "policies" && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          <div className='bg-white rounded-xl border border-gray-200 p-5 space-y-4'>
            <h3 className='font-semibold text-gray-700'>
              Upload Policy Document
            </h3>
            <label className='block w-full px-4 py-6 border-2 border-dashed border-gray-300 rounded-xl text-center cursor-pointer hover:border-indigo-400'>
              <p className='text-sm text-gray-500'>Click to upload PDF</p>
              <input
                type='file'
                accept='.pdf'
                className='hidden'
                onChange={(e) =>
                  e.target.files[0] && handleUploadPolicy(e.target.files[0])
                }
              />
            </label>

            <h3 className='font-semibold text-gray-700 mt-4'>
              Uploaded Documents
            </h3>
            {policies.length ? (
              policies.map((p) => (
                <div
                  key={p.id}
                  className='flex justify-between items-center text-sm bg-gray-50 rounded-lg p-3'>
                  <span className='text-gray-700'>{p.filename}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      p.embedding_stored
                        ? "bg-green-50 text-green-700"
                        : "bg-amber-50 text-amber-700"
                    }`}>
                    {p.embedding_stored ? "Indexed" : "Pending"}
                  </span>
                </div>
              ))
            ) : (
              <p className='text-gray-400 text-sm'>No policies uploaded yet</p>
            )}
          </div>

          <div className='bg-white rounded-xl border border-gray-200 p-5'>
            <h3 className='font-semibold text-gray-700 mb-3'>
              Most Asked Questions
            </h3>
            {topQuestions.length ? (
              topQuestions.map((q, i) => (
                <div
                  key={i}
                  className='flex justify-between items-center text-sm py-2 border-b border-gray-50'>
                  <span className='text-gray-600'>{q.question}</span>
                  <span className='text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full'>
                    {q.times_asked}x
                  </span>
                </div>
              ))
            ) : (
              <p className='text-gray-400 text-sm'>No questions asked yet</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
