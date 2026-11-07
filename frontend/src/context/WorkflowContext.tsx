import React, { createContext, useContext, useState, ReactNode } from 'react';
import {
  ExtractedResumeData,
  GapAnalysisResponse,
  ParsedJobDescription,
  ParsedResume,
  ResumeImprovementResponse,
  RoadmapResponse,
  SkillMatchingResponse,
} from '../types/api';

export interface WorkflowState {
  // Inputs
  resumeFile: File | null;
  jobDescriptionText: string;

  // Extracted & Parsed Data
  extractedResume: ExtractedResumeData | null;
  parsedResume: ParsedResume | null;
  parsedJob: ParsedJobDescription | null;

  // Analysis Artifacts
  skillMatches: SkillMatchingResponse | null;
  gapAnalysis: GapAnalysisResponse | null;
  roadmap: RoadmapResponse | null;
  resumeImprovements: ResumeImprovementResponse | null;

  // Workflow Status
  isAnalyzing: boolean;
  analysisProgress: string;
  error: string | null;
}

interface WorkflowContextType extends WorkflowState {
  setResumeFile: (file: File | null) => void;
  setJobDescriptionText: (text: string) => void;
  setExtractedResume: (data: ExtractedResumeData | null) => void;
  setParsedResume: (data: ParsedResume | null) => void;
  setParsedJob: (data: ParsedJobDescription | null) => void;
  setSkillMatches: (data: SkillMatchingResponse | null) => void;
  setGapAnalysis: (data: GapAnalysisResponse | null) => void;
  setRoadmap: (data: RoadmapResponse | null) => void;
  setResumeImprovements: (data: ResumeImprovementResponse | null) => void;
  setIsAnalyzing: (loading: boolean) => void;
  setAnalysisProgress: (msg: string) => void;
  setError: (err: string | null) => void;
  resetWorkflow: () => void;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescriptionText, setJobDescriptionText] = useState<string>('');
  const [extractedResume, setExtractedResume] = useState<ExtractedResumeData | null>(null);
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [parsedJob, setParsedJob] = useState<ParsedJobDescription | null>(null);
  const [skillMatches, setSkillMatches] = useState<SkillMatchingResponse | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysisResponse | null>(null);
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [resumeImprovements, setResumeImprovements] = useState<ResumeImprovementResponse | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const resetWorkflow = () => {
    setResumeFile(null);
    setJobDescriptionText('');
    setExtractedResume(null);
    setParsedResume(null);
    setParsedJob(null);
    setSkillMatches(null);
    setGapAnalysis(null);
    setRoadmap(null);
    setResumeImprovements(null);
    setIsAnalyzing(false);
    setAnalysisProgress('');
    setError(null);
  };

  return (
    <WorkflowContext.Provider
      value={{
        resumeFile,
        jobDescriptionText,
        extractedResume,
        parsedResume,
        parsedJob,
        skillMatches,
        gapAnalysis,
        roadmap,
        resumeImprovements,
        isAnalyzing,
        analysisProgress,
        error,
        setResumeFile,
        setJobDescriptionText,
        setExtractedResume,
        setParsedResume,
        setParsedJob,
        setSkillMatches,
        setGapAnalysis,
        setRoadmap,
        setResumeImprovements,
        setIsAnalyzing,
        setAnalysisProgress,
        setError,
        resetWorkflow,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  );
};

export const useWorkflow = (): WorkflowContextType => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
};
