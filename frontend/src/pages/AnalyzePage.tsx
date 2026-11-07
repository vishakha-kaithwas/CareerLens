import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Compass,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';
import { apiService, formatApiError } from '../services/api';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB

export const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    resumeFile,
    jobDescriptionText,
    isAnalyzing,
    analysisProgress,
    error,
    setResumeFile,
    setJobDescriptionText,
    setParsedResume,
    setParsedJob,
    setSkillMatches,
    setGapAnalysis,
    setRoadmap,
    setResumeImprovements,
    setIsAnalyzing,
    setAnalysisProgress,
    setError,
  } = useWorkflow();

  const [dragActive, setDragActive] = useState<boolean>(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file: File) => {
    setLocalError(null);
    setError(null);

    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setLocalError('Only PDF documents are supported. Please upload a valid text-based PDF resume.');
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setLocalError(`File exceeds the 5 MB limit (${(file.size / (1024 * 1024)).toFixed(2)} MB). Please select a smaller PDF.`);
      return;
    }

    if (file.size === 0) {
      setLocalError('The selected PDF file is completely empty (0 bytes).');
      return;
    }

    setResumeFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setResumeFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleExecuteAnalysis = async () => {
    if (!resumeFile) {
      setLocalError('Please upload a PDF resume before proceeding.');
      return;
    }

    if (!jobDescriptionText.trim() || jobDescriptionText.trim().length < 20) {
      setLocalError('Please paste a job description of at least 20 characters.');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      setLocalError(null);

      // Step 1: Parse resume PDF (M2)
      setAnalysisProgress('Extracting and parsing resume sections in memory...');
      const parsedResumeData = await apiService.parseResumePdf(resumeFile);
      setParsedResume(parsedResumeData);

      // Step 2: Parse Job Description (M2)
      setAnalysisProgress('Parsing job description requirements, skills, and criteria...');
      const parsedJobData = await apiService.parseJobDescription(jobDescriptionText);
      setParsedJob(parsedJobData);

      // Step 3: Skill Matching (M3)
      setAnalysisProgress('Computing exact, taxonomy, and semantic skill matches...');
      const matchData = await apiService.matchSkills(parsedResumeData, parsedJobData);
      setSkillMatches(matchData);

      // Step 4: Career Gap Analysis (M4)
      setAnalysisProgress('Evaluating requirement depth and calculating explainable coverage...');
      const gapData = await apiService.analyzeGaps(parsedResumeData, parsedJobData);
      setGapAnalysis(gapData);

      // Step 5: Learning Roadmap (M5)
      setAnalysisProgress('Building topological DAG dependency graph and learning milestones...');
      const roadmapData = await apiService.generateRoadmap(parsedResumeData, parsedJobData);
      setRoadmap(roadmapData);

      // Step 6: Evidence-Based Resume Improvement (M6)
      setAnalysisProgress('Generating honest bullet improvements and candidate questions...');
      const improvementData = await apiService.improveResume(parsedResumeData, parsedJobData, gapData, roadmapData);
      setResumeImprovements(improvementData);

      setAnalysisProgress('Analysis complete! Redirecting to dashboard...');
      setTimeout(() => {
        setIsAnalyzing(false);
        navigate('/dashboard');
      }, 500);
    } catch (err) {
      setIsAnalyzing(false);
      const formatted = formatApiError(err);
      setError(formatted);
      setLocalError(formatted);
    }
  };

  const isFormValid = Boolean(resumeFile && jobDescriptionText.trim().length >= 20);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-2 text-center sm:text-left">
        <span className="text-xs font-bold text-[#68445F] uppercase tracking-widest flex items-center gap-1.5">
          <Compass className="w-4 h-4 text-[#9A7185]" />
          Intake Step
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#261329] tracking-tight">
          Resume & Job Description Analysis Intake
        </h1>
        <p className="text-[#68445F] text-sm max-w-2xl">
          Upload your resume in PDF format and paste the target job description. CareerLens processes
          everything in-memory to uncover qualification gaps, prerequisites, and actionable improvements.
        </p>
      </div>

      {/* Error alert */}
      {(localError || error) && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Analysis Input Notice</p>
            <p className="text-xs leading-relaxed">{localError || error}</p>
          </div>
        </div>
      )}

      {/* Two-Input Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Left Column: PDF Resume Upload */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-[#261329] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#432348]" />
              <span>1. Resume Document (PDF)</span>
            </h2>
            <span className="text-[11px] font-medium text-[#68445F]">Max 5 MB</span>
          </div>

          {!resumeFile ? (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                dragActive
                  ? 'border-[#432348] bg-[#FAF5F0]'
                  : 'border-[#C6A6A4] hover:border-[#432348] hover:bg-[#FAF5F0]/60'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="w-12 h-12 rounded-full bg-[#E4D1C9] border border-[#C6A6A4] flex items-center justify-center text-[#432348] mx-auto mb-3">
                <UploadCloud className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-[#261329] mb-1">
                Click to upload or drag & drop PDF
              </p>
              <p className="text-xs text-[#68445F]">
                Standard text-based PDF resumes (LaTeX, Word, Docs)
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] flex items-center justify-between">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-10 h-10 rounded-lg bg-[#E4D1C9] text-[#432348] flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div className="truncate">
                  <p className="text-sm font-semibold text-[#261329] truncate">{resumeFile.name}</p>
                  <p className="text-xs text-[#68445F]">
                    {(resumeFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for in-memory parsing
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={handleRemoveFile}
                className="p-2 text-[#68445F] hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                title="Remove file"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-[#68445F] pt-1">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Files are processed strictly in RAM and never written to temporary disk.</span>
          </div>
        </div>

        {/* Right Column: Job Description Text */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-[#261329] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#432348]" />
              <span>2. Target Job Description</span>
            </h2>
            <span className="text-[11px] font-medium text-[#68445F]">
              {jobDescriptionText.length} characters
            </span>
          </div>

          <div>
            <textarea
              rows={9}
              value={jobDescriptionText}
              onChange={(e) => setJobDescriptionText(e.target.value)}
              placeholder="Paste the target job description here... (e.g. required skills, technologies, experience levels, and responsibilities)"
              className="w-full text-xs sm:text-sm p-3.5 rounded-xl border border-[#C6A6A4] bg-[#FAF5F0]/50 text-[#261329] focus:outline-none focus:ring-2 focus:ring-[#432348] focus:border-[#432348] transition-all font-mono placeholder:font-sans placeholder:text-[#9A7185] leading-relaxed resize-none"
            />
          </div>

          <div className="flex items-center justify-between text-xs text-[#68445F]">
            <span>Minimum 20 characters required.</span>
            {jobDescriptionText.trim().length >= 20 ? (
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Valid Description
              </span>
            ) : (
              <span className="text-slate-400">Needs more text</span>
            )}
          </div>
        </div>
      </div>

      {/* Action Card */}
      <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <p className="text-sm font-bold text-[#261329]">Run Comprehensive Career Gap Engine</p>
          <p className="text-xs text-[#68445F]">
            Extracts entities, matches requirements semantically, identifies dependency prerequisites, and generates honest suggestions.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExecuteAnalysis}
          disabled={!isFormValid || isAnalyzing}
          className={`inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-sm ${
            isFormValid && !isAnalyzing
              ? 'bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] cursor-pointer hover:-translate-y-0.5'
              : 'bg-[#E4D1C9]/60 text-[#9A7185] border border-[#C6A6A4] cursor-not-allowed'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-[#F5EDE5]" />
              <span>Analyzing in RAM...</span>
            </>
          ) : (
            <>
              <span>Run Intelligence Engine</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {/* Progress banner */}
      {isAnalyzing && (
        <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] text-[#261329] text-xs sm:text-sm flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-[#432348] animate-spin shrink-0" />
          <div className="space-y-0.5">
            <p className="font-semibold text-[#432348]">Analysis Running</p>
            <p className="text-[#68445F] text-xs">{analysisProgress || 'Processing request...'}</p>
          </div>
        </div>
      )}
    </div>
  );
};
