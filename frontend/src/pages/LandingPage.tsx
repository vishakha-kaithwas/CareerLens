import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ShieldCheck,
  Sparkles,
  GitBranch,
  Search,
  FileCheck2,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FAF5F0] border border-[#C6A6A4] text-[#432348] text-xs font-semibold shadow-xs">
            <Sparkles className="w-4 h-4 text-[#9A7185]" />
            <span>Student-First Career Intelligence</span>
            <span className="text-[#C6A6A4]">•</span>
            <span className="text-[#68445F] font-normal">Zero LLM Hallucinations</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-6xl font-extrabold text-[#261329] tracking-tight leading-[1.15]">
            Understand Your Career Gaps.{' '}
            <span className="text-[#432348] underline decoration-[#C6A6A4] decoration-4 underline-offset-8">
              Build Your Next Move.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-[#68445F] font-normal leading-relaxed">
            CareerLens is designed for students and early-career candidates. It uncovers what skills you demonstrate,
            what needs deeper project evidence, and maps what you should learn next without arbitrary percentage scores.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/analyze"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] font-semibold text-base px-8 py-3.5 rounded-xl shadow-md hover:shadow-lg transition-all"
            >
              <span>Analyze My Resume</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-[#FFFFFF] hover:bg-[#FAF5F0] text-[#261329] font-semibold text-base px-6 py-3.5 rounded-xl border border-[#C6A6A4] shadow-xs transition-all"
            >
              How It Works
            </a>
          </div>

          {/* Privacy Guarantee Pill */}
          <div className="flex items-center justify-center gap-2 text-xs font-medium text-[#68445F] pt-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Strict In-Memory Processing: Your PDF resume is never stored on disk or database.</span>
          </div>
        </div>
      </section>

      {/* 4-Step Analysis Process */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
        <div className="text-center space-y-3 mb-16">
          <h2 className="text-xs font-bold text-[#9A7185] uppercase tracking-widest">
            Clear, Understandable Process
          </h2>
          <p className="text-3xl font-extrabold text-[#261329] tracking-tight">The 4-Step Career Intelligence Lifecycle</p>
          <p className="text-[#68445F] text-sm max-w-xl mx-auto">
            Every recommendation is grounded in your actual experience and target job criteria.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Step 1 */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs hover:border-[#C6A6A4] transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] flex items-center justify-center text-[#432348] font-bold">
              1
            </div>
            <h3 className="text-base font-bold text-[#261329]">Ingestion & Extraction</h3>
            <p className="text-xs text-[#68445F] leading-relaxed">
              PyMuPDF and spaCy extract contact info, experience, skills, and projects in RAM, retaining verbatim evidence for every entry.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs hover:border-[#C6A6A4] transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] flex items-center justify-center text-[#432348] font-bold">
              2
            </div>
            <h3 className="text-base font-bold text-[#261329]">Multi-Tier Skill Matching</h3>
            <p className="text-xs text-[#68445F] leading-relaxed">
              Exact matches, taxonomy aliases, and SentenceTransformers vector proximity uncover conceptual overlap with safety guards.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs hover:border-[#C6A6A4] transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] flex items-center justify-center text-[#432348] font-bold">
              3
            </div>
            <h3 className="text-base font-bold text-[#261329]">Explainable Gap Analysis</h3>
            <p className="text-xs text-[#68445F] leading-relaxed">
              Classifies skills into Demonstrated, Needs Evidence, and Missing, providing transparent rationales instead of fake ATS percentages.
            </p>
          </div>

          {/* Step 4 */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs hover:border-[#C6A6A4] transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#FAF5F0] border border-[#C6A6A4] flex items-center justify-center text-[#432348] font-bold">
              4
            </div>
            <h3 className="text-base font-bold text-[#261329]">DAG Roadmap & Polish</h3>
            <p className="text-xs text-[#68445F] leading-relaxed">
              Directed acyclic graph discovers foundational prerequisites, topological order, and suggests honest bullet refinements.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Highlights Section */}
      <section className="bg-[#261329] text-[#F5EDE5] py-20 border-y border-[#432348]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mb-14 space-y-3">
            <h2 className="text-xs font-bold text-[#C6A6A4] uppercase tracking-widest">Platform Capabilities</h2>
            <p className="text-3xl font-extrabold tracking-tight">Built for Students and Early-Career Engineers</p>
            <p className="text-[#E4D1C9] text-sm">
              Actionable guidance focused on what to build and learn, rather than arbitrary numbers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-3 bg-[#432348]/60 p-6 rounded-2xl border border-[#68445F]">
              <div className="w-10 h-10 rounded-lg bg-[#261329] text-[#C6A6A4] flex items-center justify-center border border-[#68445F]">
                <Search className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-[#F5EDE5]">Semantic Match Verification</h3>
              <p className="text-xs text-[#E4D1C9] leading-relaxed">
                Connects project phrasing like "REST APIs with FastAPI" to "Backend web service development" using dense vectors while preventing false matches.
              </p>
            </div>

            <div className="space-y-3 bg-[#432348]/60 p-6 rounded-2xl border border-[#68445F]">
              <div className="w-10 h-10 rounded-lg bg-[#261329] text-[#C6A6A4] flex items-center justify-center border border-[#68445F]">
                <GitBranch className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-[#F5EDE5]">Prerequisite Learning Order</h3>
              <p className="text-xs text-[#E4D1C9] leading-relaxed">
                Recommends learning foundational technologies before advanced ones (e.g. Docker before Kubernetes) using topological sorting.
              </p>
            </div>

            <div className="space-y-3 bg-[#432348]/60 p-6 rounded-2xl border border-[#68445F]">
              <div className="w-10 h-10 rounded-lg bg-[#261329] text-[#C6A6A4] flex items-center justify-center border border-[#68445F]">
                <FileCheck2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-[#F5EDE5]">Zero-Hallucination Polish</h3>
              <p className="text-xs text-[#E4D1C9] leading-relaxed">
                Converts passive phrases into active verbs and asks you clarification questions for outcomes instead of inventing fake metrics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA card */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-[#432348] rounded-3xl p-8 sm:p-12 text-[#F5EDE5] shadow-xl border border-[#68445F] flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-3 text-center md:text-left">
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Ready to see your honest skill gap?</h2>
            <p className="text-[#E4D1C9] text-sm max-w-lg">
              Upload your resume in PDF format, paste a target job description, and get immediate, student-friendly feedback.
            </p>
          </div>
          <Link
            to="/analyze"
            className="shrink-0 inline-flex items-center gap-2 bg-[#F5EDE5] text-[#261329] hover:bg-white font-bold px-7 py-3.5 rounded-xl shadow-md transition-all"
          >
            <span>Start Free Analysis</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
};
