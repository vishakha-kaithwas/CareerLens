import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Compass,
  FileText,
  BarChart3,
  Map,
  Sparkles,
  Info,
  RotateCcw,
  ShieldCheck,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { gapAnalysis, resetWorkflow } = useWorkflow();
  const hasAnalysis = Boolean(gapAnalysis);

  const navLinks = [
    { to: '/', label: 'Home', icon: Compass },
    { to: '/analyze', label: 'Intake', icon: FileText },
    ...(hasAnalysis
      ? [
          { to: '/dashboard', label: 'Gap Analysis', icon: BarChart3 },
          { to: '/roadmap', label: 'Learning Roadmap', icon: Map },
          { to: '/improvement', label: 'Resume Polish', icon: Sparkles },
          { to: '/overview', label: 'Extracted Profile', icon: Info },
        ]
      : []),
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#261329] text-[#F5EDE5] border-b border-[#432348] shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#432348] to-[#9A7185] flex items-center justify-center text-[#F5EDE5] shadow-md border border-[#68445F] group-hover:scale-105 transition-transform">
              <Compass className="w-5 h-5 text-[#F5EDE5]" />
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight text-[#F5EDE5] group-hover:text-[#C6A6A4] transition-colors">
                Career<span className="text-[#C6A6A4]">Lens</span>
              </span>
              <span className="hidden sm:inline-block ml-2 text-[10px] font-semibold tracking-wider text-[#C6A6A4] uppercase px-2 py-0.5 bg-[#432348] rounded-full border border-[#68445F]">
                Student Edition
              </span>
            </div>
          </Link>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1.5">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#432348] text-[#F5EDE5] font-semibold border border-[#68445F]'
                      : 'text-[#E4D1C9] hover:text-[#F5EDE5] hover:bg-[#432348]/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#C6A6A4]' : 'text-[#9A7185]'}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Action buttons */}
          <div className="flex items-center gap-3">
            <div className="hidden lg:flex items-center gap-1.5 text-xs text-[#E4D1C9] bg-[#432348]/80 font-medium px-2.5 py-1 rounded-full border border-[#68445F]">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>In-Memory Privacy</span>
            </div>

            {hasAnalysis && (
              <button
                onClick={resetWorkflow}
                title="Clear current analysis session from memory"
                className="flex items-center gap-1.5 text-xs font-medium text-[#E4D1C9] hover:text-white hover:bg-[#432348] px-3 py-1.5 rounded-lg border border-[#68445F] transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5 text-[#C6A6A4]" />
                <span className="hidden sm:inline">New Analysis</span>
              </button>
            )}

            {!hasAnalysis && location.pathname !== '/analyze' && (
              <Link
                to="/analyze"
                className="inline-flex items-center gap-2 bg-[#432348] hover:bg-[#68445F] text-[#F5EDE5] text-sm font-semibold px-4 py-2 rounded-lg border border-[#68445F] shadow-sm hover:shadow-md transition-all"
              >
                Start Analysis
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
