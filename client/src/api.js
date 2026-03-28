import axios from "axios";

const API = axios.create({ baseURL: import.meta.env.BASE_URL });

//Module-1
export const getEmployees = (params) => API.get("/employees", { params });
export const getEmployee = (id) => API.get(`/employees/${id}`);
export const createEmployee = (data) => API.post("/employees", data);
export const updateEmployee = (id, data) => API.put(`/employees/${id}`, data);
export const deactivateEmployee = (id) => API.delete(`/employees/${id}`);
export const generateBio = (id) => API.post(`/employees/${id}/generate-bio`);
export const getDepartments = () => API.get("/employees/departments");
export const getOrgChart = () => API.get("/employees/org-chart");
export const exportCSV = () =>
  API.get("/employees/export-csv", { responseType: "blob" });
export const checkDuplicates = () => API.get("/employees/duplicates");
export const uploadDocument = (id, formData, docType) =>
  API.post(`/employees/${id}/documents?doc_type=${docType}`, formData);

//Module-2
export const getJobs = (params) => API.get("/recruitment/jobs", { params });
export const createJob = (data) => API.post("/recruitment/jobs", data);
export const getCandidates = (jobId, params) =>
  API.get(`/recruitment/jobs/${jobId}/candidates`, { params });
export const addCandidate = (jobId, data) =>
  API.post(`/recruitment/jobs/${jobId}/candidates`, data);
export const uploadResume = (candidateId, formData) =>
  API.post(`/recruitment/candidates/${candidateId}/upload-resume`, formData);
export const analyzeResume = (candidateId) =>
  API.post(`/recruitment/candidates/${candidateId}/analyze`);
export const updateStage = (candidateId, stage) =>
  API.patch(`/recruitment/candidates/${candidateId}/stage`, { stage });
export const getPipeline = (jobId) =>
  API.get(`/recruitment/jobs/${jobId}/pipeline`);
export const compareCandidates = (jobId, ids) =>
  API.get(`/recruitment/jobs/${jobId}/compare?candidate_ids=${ids}`);

//Module-3
export const applyLeave = (data) => API.post("/leave/requests", data);
export const getLeaveRequests = (params) =>
  API.get("/leave/requests", { params });
export const approveLeave = (id, data) =>
  API.patch(`/leave/requests/${id}/approve`, data);
export const getLeaveBalances = (empId) => API.get(`/leave/balances/${empId}`);
export const initLeaveBalances = (empId) =>
  API.post(`/leave/balances/initialize/${empId}`);
export const markAttendance = (data) => API.post("/leave/attendance", data);
export const getAttendance = (params) =>
  API.get("/leave/attendance", { params });
export const getLeaveCalendar = (year, month, dept) =>
  API.get("/leave/calendar", { params: { year, month, department: dept } });
export const getAttendanceSummary = (empId, year, month) =>
  API.get(`/leave/attendance/summary/${empId}`, { params: { year, month } });
export const getLeavePatterns = (dept) =>
  API.get("/leave/ai/leave-patterns", { params: { department: dept } });
export const getCapacityRisk = (start, end, dept) =>
  API.get("/leave/ai/capacity-risk", {
    params: { start_date: start, end_date: end, department: dept },
  });

//Module-4
export const createCycle = (data) => API.post("/performance/cycles", data);
export const getCycles = () => API.get("/performance/cycles");
export const addEmployeesToCycle = (cycleId, ids) =>
  API.post(`/performance/cycles/${cycleId}/add-employees`, ids);
export const getCycleReviews = (cycleId) =>
  API.get(`/performance/cycles/${cycleId}/reviews`);
export const submitSelfAssessment = (reviewId, data) =>
  API.put(`/performance/reviews/${reviewId}/self-assessment`, data);
export const submitManagerReview = (reviewId, data) =>
  API.put(`/performance/reviews/${reviewId}/manager-review`, data);
export const generateReviewSummary = (reviewId) =>
  API.post(`/performance/reviews/${reviewId}/generate-summary`);
export const getReview = (reviewId) =>
  API.get(`/performance/reviews/${reviewId}`);
export const exportReviewPDF = (reviewId) =>
  API.get(`/performance/reviews/${reviewId}/export-pdf`);

//Module-5
export const createChecklist = (data) =>
  API.post("/onboarding/checklists", data);
export const getChecklists = (role) =>
  API.get("/onboarding/checklists", { params: { role } });
export const assignChecklist = (empId, checklistId) =>
  API.post(`/onboarding/progress/${empId}/${checklistId}`);
export const getProgress = (empId) => API.get(`/onboarding/progress/${empId}`);
export const completeItem = (progressId, itemIndex) =>
  API.patch(
    `/onboarding/progress/${progressId}/complete-item?item_index=${itemIndex}`,
  );
export const uploadPolicy = (formData) =>
  API.post("/onboarding/policies", formData);
export const getPolicies = () => API.get("/onboarding/policies");
export const askChatbot = (data) => API.post("/onboarding/chat", data);
export const getChatLogs = () => API.get("/onboarding/chat-logs");
export const getTopQuestions = () =>
  API.get("/onboarding/chat-logs/top-questions");

//Module-6
export const getHeadcount = () => API.get("/analytics/headcount");
export const getAttrition = () => API.get("/analytics/attrition");
export const getTenure = () => API.get("/analytics/tenure");
export const getPositions = () => API.get("/analytics/positions");
export const getLeaveUtilisation = () =>
  API.get("/analytics/leave-utilisation");
export const getAISummary = () => API.get("/analytics/ai/monthly-summary");
