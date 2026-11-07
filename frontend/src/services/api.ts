import axios, { AxiosError } from 'axios';
import {
  APIResponse,
  ExtractedResumeData,
  GapAnalysisResponse,
  ParsedJobDescription,
  ParsedResume,
  ResumeImprovementResponse,
  RoadmapResponse,
  SkillMatchingResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

/**
 * Helper to extract error message from Axios errors.
 */
export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<APIResponse<any>>;
    if (axiosErr.response?.data?.message) {
      return axiosErr.response.data.message;
    }
    if (axiosErr.response?.data?.errors) {
      if (typeof axiosErr.response.data.errors === 'string') {
        return axiosErr.response.data.errors;
      }
      return JSON.stringify(axiosErr.response.data.errors);
    }
    if (axiosErr.message) {
      return axiosErr.message;
    }
  }
  return 'An unexpected error occurred while communicating with the CareerLens API.';
}

export const apiService = {
  /**
   * Health check
   */
  async checkHealth(): Promise<{ status: string }> {
    const res = await apiClient.get<APIResponse<{ status: string }>>('/health');
    return res.data.data || { status: 'healthy' };
  },

  /**
   * M1: Extract PDF text and metadata in-memory
   */
  async extractResumePdf(file: File): Promise<ExtractedResumeData> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<APIResponse<ExtractedResumeData>>('/resumes/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to extract PDF text');
    }
    return res.data.data;
  },

  /**
   * M2: Parse uploaded PDF resume into structured sections
   */
  async parseResumePdf(file: File): Promise<ParsedResume> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<APIResponse<ParsedResume>>('/resumes/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to parse resume');
    }
    return res.data.data;
  },

  /**
   * M2: Parse pasted job description text
   */
  async parseJobDescription(text: string): Promise<ParsedJobDescription> {
    const res = await apiClient.post<APIResponse<ParsedJobDescription>>('/jobs/parse', { text });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to parse job description');
    }
    return res.data.data;
  },

  /**
   * M3: Skill matching with semantic similarity and evidence retention
   */
  async matchSkills(resume: ParsedResume, jobDescription: ParsedJobDescription): Promise<SkillMatchingResponse> {
    const res = await apiClient.post<APIResponse<SkillMatchingResponse>>('/matching/skills', {
      resume,
      job_description: jobDescription,
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to match skills');
    }
    return res.data.data;
  },

  /**
   * M4: Career gap analysis and explainable coverage scoring
   */
  async analyzeGaps(resume: ParsedResume, jobDescription: ParsedJobDescription): Promise<GapAnalysisResponse> {
    const res = await apiClient.post<APIResponse<GapAnalysisResponse>>('/analysis/gaps', {
      resume,
      job_description: jobDescription,
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to analyze career gaps');
    }
    return res.data.data;
  },

  /**
   * M5: Personalized improvement roadmap based on dependency graph
   */
  async generateRoadmap(resume: ParsedResume, jobDescription: ParsedJobDescription): Promise<RoadmapResponse> {
    const res = await apiClient.post<APIResponse<RoadmapResponse>>('/roadmap/generate', {
      resume,
      job_description: jobDescription,
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to generate learning roadmap');
    }
    return res.data.data;
  },

  /**
   * M6: Evidence-based resume improvement suggestions
   */
  async improveResume(
    resume: ParsedResume,
    jobDescription: ParsedJobDescription,
    gapAnalysis?: GapAnalysisResponse,
    roadmap?: RoadmapResponse
  ): Promise<ResumeImprovementResponse> {
    const res = await apiClient.post<APIResponse<ResumeImprovementResponse>>('/resume/improve', {
      resume,
      job_description: jobDescription,
      gap_analysis: gapAnalysis,
      roadmap: roadmap,
    });
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.message || 'Failed to generate resume improvements');
    }
    return res.data.data;
  },
};
