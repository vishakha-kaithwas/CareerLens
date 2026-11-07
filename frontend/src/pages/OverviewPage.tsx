import React from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  User,
  Briefcase,
  FolderGit2,
  ArrowRight,
  Sparkles,
  Compass,
  Trophy,
  GraduationCap,
  Award,
} from 'lucide-react';
import { useWorkflow } from '../context/WorkflowContext';

export const OverviewPage: React.FC = () => {
  const { parsedResume, parsedJob } = useWorkflow();

  if (!parsedResume || !parsedJob) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-[#E4D1C9] text-[#432348] flex items-center justify-center mx-auto border border-[#C6A6A4]">
          <FileText className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold text-[#261329]">No Parsed Entity Data</h2>
        <p className="text-[#68445F] text-sm max-w-md mx-auto">
          Please run the intake analysis to inspect extracted entities and job criteria.
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="border-b border-[#E4D1C9] pb-6 space-y-1">
        <span className="text-xs font-bold text-[#68445F] uppercase tracking-widest flex items-center gap-1.5">
          <Compass className="w-4 h-4 text-[#9A7185]" />
          Structured Entities
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#261329] tracking-tight">
          Extracted Profile & Job Requirements
        </h1>
        <p className="text-[#68445F] text-sm">
          Review extracted structured entities, contact details, normalized technical skills, and target criteria.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Left: Parsed Resume */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold text-[#261329] flex items-center gap-2">
            <User className="w-5 h-5 text-[#432348]" />
            <span>Extracted Resume Data</span>
          </h2>

          {/* Contact Details */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">Candidate Contact</h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-[#68445F] block">Name</span>
                <span className="font-bold text-[#261329]">{parsedResume.contact.name || 'Not detected'}</span>
              </div>
              <div>
                <span className="text-[#68445F] block">Email</span>
                <span className="font-bold text-[#261329] truncate block">{parsedResume.contact.email || 'Not detected'}</span>
              </div>
              <div>
                <span className="text-[#68445F] block">Phone</span>
                <span className="font-bold text-[#261329]">{parsedResume.contact.phone || 'Not detected'}</span>
              </div>
              <div>
                <span className="text-[#68445F] block">Location</span>
                <span className="font-bold text-[#261329]">{parsedResume.contact.location || 'Not detected'}</span>
              </div>
            </div>
          </div>

          {/* Extracted & Normalized Skills */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">
              Normalized Skills ({parsedResume.skills.length})
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {parsedResume.skills.length === 0 ? (
                <p className="text-xs text-[#68445F] italic">No skills extracted</p>
              ) : (
                parsedResume.skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-xs font-semibold bg-[#FAF5F0] text-[#432348] px-2.5 py-1 rounded-lg border border-[#E4D1C9]"
                  >
                    {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Education */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider flex items-center gap-1.5">
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Education ({parsedResume.education.length})</span>
            </h3>

            {parsedResume.education.length === 0 ? (
              <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-center">
                <p className="text-xs text-[#68445F] italic">No education records detected</p>
              </div>
            ) : (
              <div className="space-y-3">
                {parsedResume.education.map((edu, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-1">
                    <div className="flex items-center justify-between font-bold text-[#261329]">
                      <span>{edu.institution || 'Institution'}</span>
                      <span className="text-[11px] font-normal text-[#68445F]">{edu.dates || ''}</span>
                    </div>
                    <p className="text-[#432348] font-medium">
                      {[edu.degree, edu.field_of_study].filter(Boolean).join(' in ') || edu.raw_text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Work Experience */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5" />
              <span>Work Experience ({parsedResume.experience.length})</span>
            </h3>

            {parsedResume.experience.length === 0 ? (
              <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-center">
                <p className="text-xs text-[#68445F] italic">No employment entries detected</p>
              </div>
            ) : (
              <div className="space-y-4">
                {parsedResume.experience.map((exp, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-2">
                    <div className="flex items-center justify-between font-bold text-[#261329]">
                      <span>{exp.title || 'Role'}</span>
                      <span className="text-[11px] font-normal text-[#68445F]">{exp.dates || ''}</span>
                    </div>
                    <p className="text-[#432348] font-bold text-[11px]">{exp.company || 'Company'}</p>
                    <ul className="space-y-1 list-disc list-inside text-[#68445F]">
                      {exp.responsibilities.map((r, ridx) => (
                        <li key={ridx} className="leading-relaxed">{r}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Projects */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider flex items-center gap-1.5">
              <FolderGit2 className="w-3.5 h-3.5" />
              <span>Projects ({parsedResume.projects.length})</span>
            </h3>

            {parsedResume.projects.length === 0 ? (
              <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-center">
                <p className="text-xs text-[#68445F] italic">No projects detected</p>
              </div>
            ) : (
              <div className="space-y-3">
                {parsedResume.projects.map((proj, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-[#261329] text-sm block">
                        {proj.title || `Project ${idx + 1}`}
                      </span>
                    </div>
                    {proj.description && (
                      <p className="text-[#68445F] leading-relaxed whitespace-pre-line">{proj.description}</p>
                    )}
                    {proj.technologies && proj.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {proj.technologies.map((t, tidx) => (
                          <span
                            key={tidx}
                            className="text-[10px] bg-[#FFFFFF] px-2 py-0.5 rounded border border-[#E4D1C9] text-[#432348] font-medium"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Extracurricular Activities & Leadership */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider flex items-center gap-1.5">
              <Trophy className="w-3.5 h-3.5 text-[#9A7185]" />
              <span>Extracurricular & Leadership ({(parsedResume.extracurriculars || []).length})</span>
            </h3>

            {(!parsedResume.extracurriculars || parsedResume.extracurriculars.length === 0) ? (
              <div className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-center">
                <p className="text-xs text-[#68445F] italic">No extracurricular or leadership activities detected</p>
              </div>
            ) : (
              <div className="space-y-3">
                {parsedResume.extracurriculars.map((extra, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs space-y-1.5">
                    <div className="flex items-center justify-between gap-2 font-bold text-[#261329]">
                      <span className="text-sm">{extra.title}</span>
                      {extra.role_or_organization && (
                        <span className="text-[11px] font-semibold text-[#432348] bg-[#FFFFFF] px-2 py-0.5 rounded border border-[#E4D1C9]">
                          {extra.role_or_organization}
                        </span>
                      )}
                    </div>
                    {extra.description && (
                      <p className="text-[#68445F] leading-relaxed whitespace-pre-line">{extra.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Certifications */}
          {parsedResume.certifications && parsedResume.certifications.length > 0 && (
            <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
              <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5" />
                <span>Certifications ({parsedResume.certifications.length})</span>
              </h3>
              <div className="space-y-2">
                {parsedResume.certifications.map((cert, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#FAF5F0] border border-[#E4D1C9] text-xs flex items-center justify-between">
                    <span className="font-bold text-[#261329]">{cert.name}</span>
                    {cert.issuer && <span className="text-[#68445F]">{cert.issuer}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Parsed Job Description */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold text-[#261329] flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#432348]" />
            <span>Target Job Criteria</span>
          </h2>

          {/* Title & Experience */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
            <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">Role Title</h3>
            <p className="text-lg font-extrabold text-[#261329]">{parsedJob.title || 'Role specified in posting'}</p>

            {parsedJob.experience_requirements.length > 0 && (
              <div className="pt-2 border-t border-[#FAF5F0] space-y-1 text-xs">
                <span className="font-bold text-[#432348]">Seniority & Experience Criteria:</span>
                <ul className="list-disc list-inside text-[#68445F] space-y-0.5">
                  {parsedJob.experience_requirements.map((exp, idx) => (
                    <li key={idx}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Required Skills */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">
                Mandatory Required Skills ({parsedJob.required_skills.length})
              </h3>
              <span className="text-[10px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                Must-Have
              </span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {parsedJob.required_skills.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No mandatory skills extracted</p>
              ) : (
                parsedJob.required_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-xs font-bold bg-rose-50 text-rose-800 px-2.5 py-1 rounded-lg border border-rose-200"
                  >
                    {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Preferred Skills */}
          <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">
                Preferred / Bonus Skills ({parsedJob.preferred_skills.length})
              </h3>
              <span className="text-[10px] font-bold text-[#432348] bg-[#FAF5F0] px-2 py-0.5 rounded-full border border-[#E4D1C9]">
                Nice-to-Have
              </span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {parsedJob.preferred_skills.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No preferred skills extracted</p>
              ) : (
                parsedJob.preferred_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-xs font-semibold bg-[#FAF5F0] text-[#432348] px-2.5 py-1 rounded-lg border border-[#E4D1C9]"
                  >
                    {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Responsibilities */}
          {parsedJob.responsibilities.length > 0 && (
            <div className="bg-[#FFFFFF] rounded-2xl p-6 border border-[#E4D1C9] shadow-xs space-y-3">
              <h3 className="text-xs font-bold text-[#9A7185] uppercase tracking-wider">
                Extracted Responsibilities ({parsedJob.responsibilities.length})
              </h3>
              <ul className="space-y-1.5 text-xs text-[#68445F] list-disc list-inside">
                {parsedJob.responsibilities.map((resp, idx) => (
                  <li key={idx} className="leading-relaxed">{resp}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
