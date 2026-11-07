import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Copy,
  Check,
  HelpCircle,
  ShieldCheck,
  AlertCircle,
  ArrowRight,
  Lightbulb,
  Layers,
  Compass,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';

export const ImprovementPage: React.FC = () => {
  const { resumeImprovements, parsedJob } = useWorkflow();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!resumeImprovements) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-[#E4D1C9] text-[#432348] flex items-center justify-center mx-auto border border-[#C6A6A4]">
          <Sparkles className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold text-[#261329]">No Resume Improvements Available</h2>
        <p className="text-[#68445F] text-sm max-w-md mx-auto">
          Please run the intake analysis to evaluate your resume bullets against the target job description.
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

  const {
    summary,
    bullet_improvements,
    section_recommendations,
    job_relevance,
  } = resumeImprovements;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E4D1C9] pb-6">
        <div className="space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-widest flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#9A7185]" />
            Evidence-Based Polish
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#261329] tracking-tight">
            Honest Resume Bullet Improvements
          </h1>
          <p className="text-[#68445F] text-sm">
            Target Role: <span className="font-semibold text-[#261329]">{parsedJob?.title || 'Target Job Role'}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200 font-bold flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Zero Synthetic Metrics
          </span>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">Suggested Bullet Refinements</span>
          <p className="text-3xl font-extrabold text-[#261329]">{summary.total_bullet_improvements}</p>
          <p className="text-xs text-[#68445F]">{summary.high_confidence_improvements} high-confidence evidence matches</p>
        </div>

        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">Clarification Questions</span>
          <p className="text-3xl font-extrabold text-[#432348]">{summary.questions_for_candidate}</p>
          <p className="text-xs text-[#68445F]">Prompted for truthful details rather than guessed</p>
        </div>

        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-1">
          <span className="text-xs font-bold text-[#68445F] uppercase tracking-wider">Strategic Readiness</span>
          <p className="text-xs font-semibold text-[#261329] leading-relaxed pt-1">{summary.overall_readiness}</p>
        </div>
      </div>

      {/* Anti-Hallucination Disclosure */}
      <div className="p-5 rounded-2xl bg-[#FFFFFF] border border-[#E4D1C9] shadow-xs text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-[#432348]">
          <ShieldCheck className="w-4 h-4 text-[#9A7185]" />
          <span>Strict Anti-Hallucination Guardrails:</span>
        </div>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[#68445F] list-disc list-inside">
          {job_relevance.honesty_guardrails_applied.map((rule, idx) => (
            <li key={idx}>{rule}</li>
          ))}
        </ul>
      </div>

      {/* Section Strategic Guidance & Buried Skills */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section Guidance */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
          <h2 className="text-base font-bold text-[#261329] flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#432348]" />
            <span>Section-by-Section Guidance</span>
          </h2>

          <div className="space-y-3">
            {section_recommendations.map((sec, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-1.5">
                <div className="flex items-center justify-between font-bold text-[#261329] capitalize">
                  <span>{sec.section_name} Section</span>
                  <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full font-bold ${
                    sec.status === 'strong' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                    sec.status === 'needs_focus' ? 'bg-amber-50 text-amber-800 border border-amber-200' :
                    'bg-[#E4D1C9] text-[#261329]'
                  }`}>
                    {sec.status.replace('_', ' ')}
                  </span>
                </div>
                {sec.recommendations.map((r, ridx) => (
                  <p key={ridx} className="text-[#68445F] leading-relaxed">• {r}</p>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Buried Skills & Alignment */}
        <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
          <h2 className="text-base font-bold text-[#261329] flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-[#9A7185]" />
            <span>Buried Skills & Direct Alignment</span>
          </h2>

          {job_relevance.buried_skills.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs space-y-1 text-amber-900">
              <span className="font-bold flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-amber-700" />
                <span>Buried Project Skills Found:</span>
              </span>
              <p className="text-slate-700 leading-relaxed">
                You demonstrated <strong className="text-[#261329]">{job_relevance.buried_skills.join(', ')}</strong> in your projects, but left them off your primary skills list. Add them directly for immediate recruiter visibility.
              </p>
            </div>
          )}

          <div className="space-y-2 text-xs">
            <span className="font-bold text-[#261329] block">Top Aligned Strengths for this Posting:</span>
            {job_relevance.top_aligned_strengths.length === 0 ? (
              <p className="text-slate-400 italic">No direct matches identified.</p>
            ) : (
              <ul className="space-y-1.5">
                {job_relevance.top_aligned_strengths.map((s, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-emerald-800 bg-emerald-50/50 p-2.5 rounded-lg border border-emerald-100">
                    <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* Suggested Bullet Point Improvements */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-[#261329]">
          Before & After Bullet Point Refinements
        </h2>

        {bullet_improvements.length === 0 ? (
          <div className="bg-[#FFFFFF] rounded-2xl p-8 border border-[#E4D1C9] text-center text-[#68445F] text-sm">
            Your existing bullets are already clear and use strong engineering action verbs.
          </div>
        ) : (
          <div className="space-y-6">
            {bullet_improvements.map((bullet) => (
              <div
                key={bullet.id}
                className="bg-[#FFFFFF] rounded-2xl border border-[#E4D1C9] shadow-xs p-6 hover:border-[#C6A6A4] transition-all space-y-4"
              >
                {/* Meta header */}
                <div className="flex items-center justify-between text-xs border-b border-[#FAF5F0] pb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#432348] capitalize bg-[#FAF5F0] px-2.5 py-0.5 rounded-full border border-[#E4D1C9]">
                      {bullet.section_name}
                    </span>
                    {bullet.relevant_job_requirement && (
                      <span className="text-[#432348] bg-[#E4D1C9] px-2.5 py-0.5 rounded-full font-semibold">
                        Targets: {bullet.relevant_job_requirement}
                      </span>
                    )}
                  </div>
                  <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                    bullet.confidence === 'high' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-200'
                  }`}>
                    {bullet.confidence} confidence
                  </span>
                </div>

                {/* Before & After Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Original */}
                  <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-2">
                    <span className="font-bold text-rose-700 uppercase tracking-wider text-[10px] block">
                      Original Wording (Passive / Vague)
                    </span>
                    <p className="text-[#261329] font-mono leading-relaxed">
                      "{bullet.original_text}"
                    </p>
                  </div>

                  {/* Improved */}
                  <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] text-xs space-y-2 relative">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#432348] uppercase tracking-wider text-[10px] block">
                        Suggested Refinement (Active Engineering)
                      </span>
                      <button
                        onClick={() => handleCopy(bullet.suggested_text, bullet.id)}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-[#432348] hover:text-[#261329] bg-[#FFFFFF] px-2 py-1 rounded-md border border-[#C6A6A4] shadow-2xs transition-all"
                      >
                        {copiedId === bullet.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span className="text-emerald-700">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-[#261329] font-semibold leading-relaxed">
                      "{bullet.suggested_text}"
                    </p>
                  </div>
                </div>

                {/* Why useful explanation */}
                <div className="text-xs text-[#68445F] space-y-1">
                  <span className="font-bold text-[#432348]">Why this change is helpful:</span>
                  <p className="leading-relaxed">{bullet.why_useful}</p>
                </div>

                {/* Candidate Clarification Questions */}
                {bullet.candidate_questions.length > 0 && (
                  <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs space-y-2 text-amber-900">
                    <div className="flex items-center gap-1.5 font-bold text-amber-800">
                      <HelpCircle className="w-4 h-4 text-amber-700 shrink-0" />
                      <span>Truthful Detail Needed from Candidate:</span>
                    </div>
                    {bullet.candidate_questions.map((q, qidx) => (
                      <div key={qidx} className="space-y-0.5 pl-5">
                        <p className="font-bold text-[#261329]">Q: {q.question}</p>
                        <p className="text-[#68445F] text-[11px]">{q.why_needed}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
