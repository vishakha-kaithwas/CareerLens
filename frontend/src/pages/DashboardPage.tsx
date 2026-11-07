import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Sparkles,
  Map,
  Compass,
  FolderGit2,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
  Target,
  FileCheck2,
  ArrowUpRight,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';

export const DashboardPage: React.FC = () => {
  const { gapAnalysis, roadmap, parsedJob } = useWorkflow();
  const [showScoringDetails, setShowScoringDetails] = useState<boolean>(false);

  if (!gapAnalysis) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-[#E4D1C9] text-[#432348] flex items-center justify-center mx-auto border border-[#C6A6A4]">
          <Compass className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold text-[#261329]">No Active Career Gap Analysis</h2>
        <p className="text-[#68445F] text-sm max-w-md mx-auto">
          Upload your resume and paste your target job posting to see which skills you demonstrate and what you should build next.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] text-sm font-semibold px-6 py-3 rounded-xl shadow-sm transition-all"
        >
          <span>Go to Intake</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const {
    overall_coverage,
    required_coverage,
    preferred_coverage,
    matched_requirements,
    partially_demonstrated_requirements,
    not_demonstrated_requirements,
    results,
  } = gapAnalysis;

  // Split not demonstrated into mandatory vs preferred
  const missingMandatory = not_demonstrated_requirements.filter(
    (item) => item.requirement_type === 'required'
  );
  const missingPreferred = not_demonstrated_requirements.filter(
    (item) => item.requirement_type === 'preferred'
  );

  // Map roadmap steps by skill name for actionable next steps
  const roadmapStepMap: Record<string, any> = {};
  if (roadmap?.roadmap) {
    roadmap.roadmap.forEach((step) => {
      roadmapStepMap[step.skill_name.toLowerCase()] = step;
    });
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* 1. Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E4D1C9] pb-6">
        <div className="space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-widest flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#9A7185]" />
            Career Intelligence Summary
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#261329] tracking-tight">
            Your Career Gap Analysis
          </h1>
          <p className="text-[#68445F] text-sm">
            Target Role: <span className="font-semibold text-[#261329]">{parsedJob?.title || 'Target Job Role'}</span>
          </p>
        </div>

        {/* Quick action buttons */}
        <div className="flex items-center gap-3">
          <Link
            to="/roadmap"
            className="inline-flex items-center gap-2 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] text-xs sm:text-sm font-semibold px-4 py-2.5 rounded-xl shadow-xs transition-colors"
          >
            <Map className="w-4 h-4 text-[#C6A6A4]" />
            <span>Learning Roadmap</span>
          </Link>
          <Link
            to="/improvement"
            className="inline-flex items-center gap-2 bg-[#FAF5F0] hover:bg-[#E4D1C9] text-[#432348] text-xs sm:text-sm font-semibold px-4 py-2.5 rounded-xl border border-[#C6A6A4] transition-colors"
          >
            <Sparkles className="w-4 h-4 text-[#9A7185]" />
            <span>Resume Polish</span>
          </Link>
        </div>
      </div>

      {/* 2. Three Actionable Category Cards (Student-First Overview) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Category 1: Skills You Can Demonstrate */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">
              Verified Strengths
            </span>
            <span className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-sm border border-emerald-200">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>

          <div>
            <span className="text-4xl font-extrabold text-[#261329]">{matched_requirements.length}</span>
            <span className="text-xs text-[#68445F] font-medium ml-2">skills supported</span>
          </div>

          <h3 className="text-sm font-bold text-[#261329]">Skills you can demonstrate</h3>
          <p className="text-xs text-[#68445F] leading-relaxed">
            Direct, verifiable evidence exists in your resume through work experience, listed technical skills, or completed projects.
          </p>
        </div>

        {/* Category 2: Skills That Need Stronger Evidence */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">
              Needs Evidence Depth
            </span>
            <span className="w-8 h-8 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center font-bold text-sm border border-amber-200">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>

          <div>
            <span className="text-4xl font-extrabold text-[#261329]">{partially_demonstrated_requirements.length}</span>
            <span className="text-xs text-[#68445F] font-medium ml-2">skills partially shown</span>
          </div>

          <h3 className="text-sm font-bold text-[#261329]">Skills needing stronger evidence</h3>
          <p className="text-xs text-[#68445F] leading-relaxed">
            You mentioned this skill or a closely related concept, but lack concrete project implementations or measurable outcomes to prove proficiency.
          </p>
        </div>

        {/* Category 3: Skills You Need to Learn */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">
              Actionable Gap
            </span>
            <span className="w-8 h-8 rounded-full bg-rose-50 text-rose-700 flex items-center justify-center font-bold text-sm border border-rose-200">
              <XCircle className="w-4 h-4" />
            </span>
          </div>

          <div>
            <span className="text-4xl font-extrabold text-[#261329]">{not_demonstrated_requirements.length}</span>
            <span className="text-xs text-[#68445F] font-medium ml-2">skills to build</span>
          </div>

          <h3 className="text-sm font-bold text-[#261329]">Skills you need to learn</h3>
          <p className="text-xs text-[#68445F] leading-relaxed">
            No recognizable evidence found on your resume. These represent your highest-impact learning priorities to become job-ready.
          </p>
        </div>
      </div>

      {/* 3. What You Should Focus On Next (Priority Skills from Missing Mandatory) */}
      <section className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#FAF5F0] pb-4">
          <div className="space-y-1">
            <span className="text-xs font-bold text-[#9A7185] uppercase tracking-widest flex items-center gap-1.5">
              <Target className="w-4 h-4 text-[#432348]" />
              Actionable Student Guidance
            </span>
            <h2 className="text-xl sm:text-2xl font-extrabold text-[#261329]">
              What you should focus on next
            </h2>
            <p className="text-xs sm:text-sm text-[#68445F]">
              Missing mandatory requirements prioritized with practical next steps to build portfolio evidence.
            </p>
          </div>
          <Link
            to="/roadmap"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#432348] hover:text-[#68445F] transition-colors"
          >
            <span>View Full Timeline Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>

        {missingMandatory.length === 0 ? (
          <div className="p-6 rounded-xl bg-emerald-50/60 border border-emerald-200 text-center space-y-1 text-emerald-800">
            <CheckCircle2 className="w-6 h-6 mx-auto text-emerald-600 mb-2" />
            <p className="font-bold text-sm">Great job! All mandatory requirements are demonstrated or partially demonstrated.</p>
            <p className="text-xs text-emerald-700">Check the preferred skills below or explore resume polishing opportunities.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {missingMandatory.map((item, idx) => {
              const roadmapItem = roadmapStepMap[item.requirement.toLowerCase()];

              return (
                <div
                  key={idx}
                  className="p-5 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] hover:border-[#C6A6A4] transition-all space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-lg bg-[#432348] text-[#F5EDE5] font-bold text-xs flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <h3 className="text-base font-bold text-[#261329]">{item.requirement}</h3>
                    </div>
                    <span className="text-[11px] font-semibold text-rose-700 bg-rose-50 px-2.5 py-0.5 rounded-full border border-rose-200 w-fit">
                      Mandatory Requirement
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                    <div className="space-y-1">
                      <span className="font-semibold text-[#432348]">Why the job requires it:</span>
                      <p className="text-[#68445F] leading-relaxed">
                        {item.job_evidence || `This role lists ${item.requirement} as a core qualification for daily deliverables.`}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <span className="font-semibold text-[#432348]">Current evidence status:</span>
                      <p className="text-slate-500 font-mono text-[11px]">
                        No identifiable evidence found in uploaded resume.
                      </p>
                    </div>
                  </div>

                  {roadmapItem && (
                    <div className="p-3.5 rounded-lg bg-[#FFFFFF] border border-[#E4D1C9] text-xs space-y-1.5">
                      <div className="flex items-center gap-2 text-[#432348] font-bold">
                        <FolderGit2 className="w-3.5 h-3.5 text-[#9A7185]" />
                        <span>Recommended Practical Project to Build:</span>
                      </div>
                      <p className="text-[#261329] font-medium">{roadmapItem.practical_project}</p>
                      <p className="text-[11px] text-[#68445F]">
                        <strong>Expected Artifact:</strong> {roadmapItem.expected_deliverable} ({roadmapItem.estimated_hours} hrs estimated)
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* 4. Demonstrated Strengths & Skills Needing More Evidence (Side-by-side) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Left: Demonstrated Strengths */}
        <section className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#FAF5F0] pb-3">
            <h2 className="text-base font-bold text-[#261329] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Demonstrated Strengths ({matched_requirements.length})</span>
            </h2>
            <span className="text-xs text-[#68445F] font-medium">Verified by evidence</span>
          </div>

          <p className="text-xs text-[#68445F]">
            These qualifications match the job description and are substantiated by your resume.
          </p>

          <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
            {matched_requirements.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No direct matches identified yet.</p>
            ) : (
              matched_requirements.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-1.5">
                  <div className="flex items-center justify-between font-bold text-[#261329]">
                    <span>{item.requirement}</span>
                    <span className="text-[10px] font-normal uppercase text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      {item.match_method} match
                    </span>
                  </div>
                  {item.resume_evidence && (
                    <p className="text-[11px] text-[#68445F] font-mono leading-relaxed bg-[#FFFFFF] p-2 rounded border border-[#E4D1C9]">
                      "{item.resume_evidence}"
                    </p>
                  )}
                  <p className="text-[11px] text-slate-500">{item.explanation}</p>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Right: Skills Requiring More Evidence */}
        <section className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#FAF5F0] pb-3">
            <h2 className="text-base font-bold text-[#261329] flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Skills Needing Evidence ({partially_demonstrated_requirements.length})</span>
            </h2>
            <span className="text-xs text-[#68445F] font-medium">Mentioned but unproven</span>
          </div>

          <p className="text-xs text-[#68445F]">
            You have exposure to these skills, but lack deep implementation details or measurable outcomes.
          </p>

          <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
            {partially_demonstrated_requirements.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No partially demonstrated skills found.</p>
            ) : (
              partially_demonstrated_requirements.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-amber-50/40 border border-amber-200/80 text-xs space-y-1.5">
                  <div className="flex items-center justify-between font-bold text-[#261329]">
                    <span>{item.requirement}</span>
                    <span className="text-[10px] font-normal uppercase text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                      Partial Demonstration
                    </span>
                  </div>
                  {item.resume_evidence && (
                    <p className="text-[11px] text-[#68445F] font-mono bg-[#FFFFFF] p-2 rounded border border-amber-200/60">
                      "{item.resume_evidence}"
                    </p>
                  )}
                  <p className="text-[11px] text-[#432348] font-medium">
                    <strong>What is missing:</strong> {item.explanation}
                  </p>
                  {item.suggested_improvement && (
                    <p className="text-[11px] text-[#68445F] italic">
                      💡 {item.suggested_improvement}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* 5. Missing Requirements Separated: Mandatory vs. Preferred */}
      <section className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs p-6 sm:p-8 space-y-6">
        <div className="space-y-1 border-b border-[#FAF5F0] pb-4">
          <h2 className="text-xl font-bold text-[#261329]">
            Missing Requirements Breakdown
          </h2>
          <p className="text-xs sm:text-sm text-[#68445F]">
            Distinguishes mandatory deal-breakers from preferred bonus qualifications.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Mandatory Gaps */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#261329] uppercase tracking-wider flex items-center justify-between">
              <span>Mandatory Requirements ({missingMandatory.length})</span>
              <span className="text-[10px] text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                Must-Have
              </span>
            </h3>

            {missingMandatory.length === 0 ? (
              <p className="text-xs text-emerald-600 font-medium p-4 bg-emerald-50 rounded-xl">
                Zero missing mandatory qualifications.
              </p>
            ) : (
              <div className="space-y-2">
                {missingMandatory.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-rose-50/40 border border-rose-200/70 text-xs space-y-1">
                    <span className="font-bold text-[#261329] block">{item.requirement}</span>
                    <p className="text-[11px] text-[#68445F]">
                      {item.suggested_improvement || `Gain practical project experience with ${item.requirement}.`}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Preferred Gaps */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#261329] uppercase tracking-wider flex items-center justify-between">
              <span>Preferred / Bonus Skills ({missingPreferred.length})</span>
              <span className="text-[10px] text-[#68445F] bg-[#FAF5F0] px-2 py-0.5 rounded border border-[#E4D1C9]">
                Nice-to-Have
              </span>
            </h3>

            {missingPreferred.length === 0 ? (
              <p className="text-xs text-slate-500 italic p-4 bg-[#FAF5F0] rounded-xl">
                No missing preferred criteria.
              </p>
            ) : (
              <div className="space-y-2">
                {missingPreferred.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-1">
                    <span className="font-bold text-[#261329] block">{item.requirement}</span>
                    <p className="text-[11px] text-[#68445F]">
                      {item.suggested_improvement || `Optional bonus skill. Can be picked up after core requirements.`}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 6. Expandable Coverage Scoring Section (De-emphasized Math & Honest Disclaimer) */}
      <section className="bg-[#FAF5F0] rounded-2xl border border-[#E4D1C9] p-6 space-y-4">
        <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowScoringDetails(!showScoringDetails)}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#E4D1C9] text-[#432348] flex items-center justify-center font-bold">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#261329]">
                Evidence Coverage Score:{' '}
                <span className="text-base font-extrabold text-[#432348]">
                  {overall_coverage.overall_score !== null ? `${overall_coverage.overall_score}%` : 'N/A'}
                </span>
              </h3>
              <p className="text-xs text-[#68445F]">
                Measures observable text evidence across requirements. Click to {showScoringDetails ? 'hide' : 'view'} scoring details.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="p-2 text-[#432348] hover:bg-[#E4D1C9] rounded-lg transition-colors"
          >
            {showScoringDetails ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>

        {showScoringDetails && (
          <div className="pt-4 border-t border-[#E4D1C9] space-y-4 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-[#FFFFFF] border border-[#E4D1C9] space-y-1">
                <span className="font-bold text-[#432348] block">Mandatory Criteria Score</span>
                <p className="text-base font-bold text-[#261329]">
                  {required_coverage.coverage_score !== null ? `${required_coverage.coverage_score}%` : 'N/A'}
                </p>
                <p className="text-[11px] text-[#68445F]">{required_coverage.calculation_explanation}</p>
              </div>

              <div className="p-3 rounded-lg bg-[#FFFFFF] border border-[#E4D1C9] space-y-1">
                <span className="font-bold text-[#432348] block">Preferred Criteria Score</span>
                <p className="text-base font-bold text-[#261329]">
                  {preferred_coverage.coverage_score !== null ? `${preferred_coverage.coverage_score}%` : 'N/A'}
                </p>
                <p className="text-[11px] text-[#68445F]">{preferred_coverage.calculation_explanation}</p>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-amber-50/60 border border-amber-200/70 text-amber-900 flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                <strong>Non-Misleading Disclosure:</strong> {overall_coverage.disclaimer}
              </p>
            </div>
          </div>
        )}
      </section>

      {/* 7. Comprehensive Itemized Requirements Table */}
      <section className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs overflow-hidden">
        <div className="p-6 border-b border-[#FAF5F0] flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-base font-bold text-[#261329]">Full Requirement Verification Table</h2>
            <p className="text-xs text-[#68445F]">
              Every evaluated job requirement with evidence and transparent justification.
            </p>
          </div>
          <span className="text-xs font-semibold text-[#68445F]">{results.length} total requirements</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FAF5F0] text-[#432348] font-bold border-b border-[#E4D1C9]">
                <th className="py-3 px-4">Requirement</th>
                <th className="py-3 px-3">Type</th>
                <th className="py-3 px-3">Classification</th>
                <th className="py-3 px-3">Match Method</th>
                <th className="py-3 px-4">Resume Evidence</th>
                <th className="py-3 px-4">Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#FAF5F0]">
              {results.map((row, idx) => (
                <tr key={idx} className="hover:bg-[#FAF5F0]/60 transition-colors">
                  <td className="py-3 px-4 font-bold text-[#261329]">{row.requirement}</td>
                  <td className="py-3 px-3 capitalize text-[#68445F]">{row.requirement_type}</td>
                  <td className="py-3 px-3">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                      row.classification === 'matched' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                      row.classification === 'partially_demonstrated' ? 'bg-amber-50 text-amber-800 border border-amber-200' :
                      'bg-rose-50 text-rose-800 border border-rose-200'
                    }`}>
                      {row.classification === 'matched' ? <CheckCircle2 className="w-3 h-3 text-emerald-600" /> :
                       row.classification === 'partially_demonstrated' ? <AlertTriangle className="w-3 h-3 text-amber-600" /> :
                       <XCircle className="w-3 h-3 text-rose-600" />}
                      <span className="capitalize">{row.classification.replace('_', ' ')}</span>
                    </span>
                  </td>
                  <td className="py-3 px-3 text-[#68445F] capitalize">{row.match_method}</td>
                  <td className="py-3 px-4 text-[#68445F] font-mono text-[11px] max-w-xs">
                    {row.resume_evidence ? (
                      <span className="bg-[#FAF5F0] p-1 rounded border border-[#E4D1C9] block truncate">
                        {row.resume_evidence}
                      </span>
                    ) : (
                      <span className="text-slate-400 italic">None</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-[#68445F] max-w-sm leading-relaxed">{row.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
