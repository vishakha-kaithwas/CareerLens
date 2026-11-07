import React from 'react';
import { Link } from 'react-router-dom';
import {
  Map,
  Clock,
  FolderGit2,
  BookOpen,
  ArrowRight,
  GitBranch,
  Sparkles,
  Compass,
  CheckCircle2,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';

const PRIORITY_STYLES: Record<string, { badge: string; border: string; bg: string }> = {
  critical: {
    badge: 'bg-rose-50 text-rose-800 border-rose-200',
    border: 'border-l-4 border-l-rose-500',
    bg: 'bg-[#FFFFFF]',
  },
  high: {
    badge: 'bg-amber-50 text-amber-800 border-amber-200',
    border: 'border-l-4 border-l-amber-500',
    bg: 'bg-[#FFFFFF]',
  },
  medium: {
    badge: 'bg-[#FAF5F0] text-[#432348] border-[#C6A6A4]',
    border: 'border-l-4 border-l-[#9A7185]',
    bg: 'bg-[#FFFFFF]',
  },
  low: {
    badge: 'bg-[#FAF5F0] text-[#68445F] border-[#E4D1C9]',
    border: 'border-l-4 border-l-[#C6A6A4]',
    bg: 'bg-[#FFFFFF]',
  },
};

export const RoadmapPage: React.FC = () => {
  const { roadmap, parsedJob } = useWorkflow();

  if (!roadmap) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-[#E4D1C9] text-[#432348] flex items-center justify-center mx-auto border border-[#C6A6A4]">
          <Map className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold text-[#261329]">No Active Learning Roadmap</h2>
        <p className="text-[#68445F] text-sm max-w-md mx-auto">
          Run your resume analysis intake to map a personalized, step-by-step learning journey.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] text-sm font-semibold px-6 py-3 rounded-xl shadow-xs transition-all"
        >
          <span>Go to Intake</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const { summary, roadmap: steps, gap_summary } = roadmap;

  // Group steps by Phase for student clarity
  // Phase 1: Foundational Prerequisites & Critical Gaps
  // Phase 2: Missing Core Requirements
  // Phase 3: Depth & Preferred Enhancements
  const phase1Steps = steps.filter((s) => s.priority === 'critical');
  const phase2Steps = steps.filter((s) => s.priority === 'high');
  const phase3Steps = steps.filter((s) => s.priority === 'medium' || s.priority === 'low');

  const phases = [
    {
      phaseNumber: 1,
      title: 'Phase 1: Foundational Prerequisites',
      subtitle: 'Master these dependencies before tackling advanced tools',
      steps: phase1Steps,
    },
    {
      phaseNumber: 2,
      title: 'Phase 2: Missing Core Requirements',
      subtitle: 'Mandatory technical skills required for this job role',
      steps: phase2Steps,
    },
    {
      phaseNumber: 3,
      title: 'Phase 3: Deepening Proficiency & Preferred Skills',
      subtitle: 'Build practical depth and bonus capabilities',
      steps: phase3Steps,
    },
  ].filter((p) => p.steps.length > 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E4D1C9] pb-6">
        <div className="space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-widest flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#9A7185]" />
            Directed Dependency Graph
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#261329] tracking-tight">
            Your Step-by-Step Learning Journey
          </h1>
          <p className="text-[#68445F] text-sm">
            Target Role: <span className="font-semibold text-[#261329]">{parsedJob?.title || 'Target Job Role'}</span>
          </p>
        </div>

        <Link
          to="/improvement"
          className="inline-flex items-center gap-2 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] text-xs sm:text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors"
        >
          <Sparkles className="w-4 h-4 text-[#C6A6A4]" />
          <span>Go to Resume Polish</span>
        </Link>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] rounded-2xl p-4 border border-[#E4D1C9] shadow-xs">
          <span className="text-[11px] font-bold text-[#68445F] uppercase tracking-wider block mb-1">Total Milestones</span>
          <span className="text-3xl font-extrabold text-[#261329]">{summary.total_steps}</span>
        </div>

        <div className="bg-[#FFFFFF] rounded-2xl p-4 border border-rose-200/80 bg-rose-50/20 shadow-xs">
          <span className="text-[11px] font-bold text-rose-700 uppercase tracking-wider block mb-1">Prerequisites</span>
          <span className="text-3xl font-extrabold text-rose-700">{summary.critical_steps_count}</span>
        </div>

        <div className="bg-[#FFFFFF] rounded-2xl p-4 border border-amber-200/80 bg-amber-50/20 shadow-xs">
          <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider block mb-1">Core Gaps</span>
          <span className="text-3xl font-extrabold text-amber-700">{summary.high_steps_count}</span>
        </div>

        <div className="bg-[#FFFFFF] rounded-2xl p-4 border border-[#E4D1C9] bg-[#FAF5F0] shadow-xs">
          <span className="text-[11px] font-bold text-[#432348] uppercase tracking-wider block mb-1">Estimated Hours</span>
          <span className="text-3xl font-extrabold text-[#432348]">
            {summary.total_estimated_hours} <span className="text-xs font-normal text-[#68445F]">hrs</span>
          </span>
        </div>
      </div>

      {/* Synthesis Banner */}
      <div className="p-5 rounded-2xl bg-[#FFFFFF] border border-[#E4D1C9] shadow-xs text-xs sm:text-sm text-[#261329] flex items-start gap-3.5">
        <GitBranch className="w-5 h-5 text-[#432348] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-bold text-[#261329] block">Topological Synthesis</span>
          <p className="text-[#68445F] text-xs leading-relaxed">{gap_summary}</p>
        </div>
      </div>

      {/* Phase-Based Learning Journey */}
      <div className="space-y-10">
        {phases.length === 0 ? (
          <div className="bg-[#FFFFFF] rounded-2xl p-8 border border-emerald-200 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
            <p className="text-base font-bold text-[#261329]">
              All job requirements already demonstrated!
            </p>
            <p className="text-xs text-[#68445F]">
              Your resume evidence currently satisfies the extracted requirements for this role.
            </p>
          </div>
        ) : (
          phases.map((phase) => (
            <div key={phase.phaseNumber} className="space-y-5">
              {/* Phase Header */}
              <div className="flex items-center gap-3 border-b border-[#E4D1C9] pb-3">
                <span className="w-8 h-8 rounded-xl bg-[#432348] text-[#F5EDE5] font-extrabold text-sm flex items-center justify-center">
                  {phase.phaseNumber}
                </span>
                <div>
                  <h2 className="text-lg font-bold text-[#261329]">{phase.title}</h2>
                  <p className="text-xs text-[#68445F]">{phase.subtitle}</p>
                </div>
              </div>

              {/* Phase Steps Grid */}
              <div className="space-y-4">
                {phase.steps.map((step) => {
                  const style = PRIORITY_STYLES[step.priority] || PRIORITY_STYLES.low;

                  return (
                    <div
                      key={step.step_number}
                      className={`rounded-2xl border border-[#E4D1C9] shadow-xs p-6 ${style.border} ${style.bg} hover:border-[#C6A6A4] transition-all space-y-4`}
                    >
                      {/* Step Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#FAF5F0] pb-3">
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-bold text-[#68445F]">
                            Step #{step.step_number}
                          </span>
                          <h3 className="text-lg font-bold text-[#261329]">{step.skill_name}</h3>
                          <span className="text-xs text-[#9A7185] bg-[#FAF5F0] px-2 py-0.5 rounded border border-[#E4D1C9]">
                            {step.category}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border uppercase tracking-wider ${style.badge}`}>
                            {step.priority} Priority
                          </span>
                          <span className="text-xs font-semibold text-[#432348] bg-[#FAF5F0] px-2.5 py-0.5 rounded-full border border-[#E4D1C9] flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-[#9A7185]" />
                            {step.estimated_hours} hrs
                          </span>
                        </div>
                      </div>

                      {/* Prerequisite banner */}
                      {step.is_prerequisite_for && (
                        <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
                          <GitBranch className="w-4 h-4 text-amber-700 shrink-0" />
                          <span>
                            Foundational dependency required before learning: <strong className="font-bold text-[#261329]">{step.is_prerequisite_for}</strong>
                          </span>
                        </div>
                      )}

                      {/* Why it matters & Current evidence */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div className="space-y-1">
                          <span className="font-bold text-[#432348]">Why this matters for the role:</span>
                          <p className="text-[#68445F] leading-relaxed">{step.why_it_matters}</p>
                        </div>
                        <div className="space-y-1">
                          <span className="font-bold text-[#432348]">Current resume evidence:</span>
                          <p className="text-[#68445F] font-mono text-[11px]">
                            {step.current_evidence || 'No evidence detected'}
                          </p>
                        </div>
                      </div>

                      {/* Learning topics */}
                      {step.learning_topics.length > 0 && (
                        <div className="space-y-1.5 pt-2 border-t border-[#FAF5F0]">
                          <span className="text-xs font-bold text-[#432348] flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5 text-[#9A7185]" />
                            <span>Core Topics to Learn:</span>
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {step.learning_topics.map((topic, tidx) => (
                              <span
                                key={tidx}
                                className="text-xs bg-[#FAF5F0] text-[#261329] px-2.5 py-0.5 rounded-md border border-[#E4D1C9]"
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Practical Portfolio Deliverable */}
                      <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-2">
                        <div className="flex items-center gap-2 text-[#432348] font-bold">
                          <FolderGit2 className="w-4 h-4 text-[#9A7185]" />
                          <span>Practical Project to Build & Demonstrate:</span>
                        </div>
                        <p className="text-[#261329] font-medium leading-relaxed">
                          {step.practical_project}
                        </p>
                        <p className="text-[11px] text-[#68445F] pt-0.5">
                          <strong>Expected Deliverable:</strong> {step.expected_deliverable}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
