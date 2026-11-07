// API Common Types
export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
  errors?: any;
}

// PDF Extraction (M1)
export interface PageTextContent {
  page_number: number;
  text: string;
  character_count: number;
  word_count: number;
}

export interface PDFMetadata {
  title?: string | null;
  author?: string | null;
  creator?: string | null;
  producer?: string | null;
  creation_date?: string | null;
  modification_date?: string | null;
  is_encrypted: boolean;
}

export interface ExtractedResumeData {
  filename: string;
  total_pages: number;
  total_characters: number;
  total_words: number;
  is_scanned: boolean;
  metadata: PDFMetadata;
  pages: PageTextContent[];
  full_text: string;
}

// Parsed Resume (M2)
export interface ContactInfo {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin?: string | null;
  github?: string | null;
  portfolio?: string | null;
}

export interface EducationEntry {
  institution?: string | null;
  degree?: string | null;
  field_of_study?: string | null;
  dates?: string | null;
  raw_text: string;
}

export interface ExperienceEntry {
  title?: string | null;
  company?: string | null;
  dates?: string | null;
  responsibilities: string[];
  raw_text: string;
}

export interface ProjectEntry {
  title?: string | null;
  description?: string | null;
  technologies: string[];
  raw_text: string;
}

export interface CertificationEntry {
  name: string;
  issuer?: string | null;
  raw_text: string;
}

export interface ExtracurricularEntry {
  title: string;
  role_or_organization?: string | null;
  description?: string | null;
  raw_text: string;
}

export interface ParsedResume {
  contact: ContactInfo;
  summary?: string | null;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  extracurriculars?: ExtracurricularEntry[];
  raw_text: string;
}

// Parsed Job Description (M2)
export interface ParsedJobDescription {
  title?: string | null;
  required_skills: string[];
  preferred_skills: string[];
  tools_and_technologies: string[];
  soft_skills: string[];
  experience_requirements: string[];
  education_requirements: string[];
  responsibilities: string[];
  raw_text: string;
}

// Skill Matching (M3)
export type MatchMethod = 'exact' | 'normalized' | 'semantic' | 'none';

export interface SkillMatchItem {
  job_requirement: string;
  is_required: boolean;
  is_matched: boolean;
  match_method: MatchMethod;
  similarity_score: number;
  matched_resume_skill?: string | null;
  resume_evidence?: string | null;
  job_evidence?: string | null;
}

export interface SkillMatchingResponse {
  required_matches: SkillMatchItem[];
  preferred_matches: SkillMatchItem[];
  total_required_count: number;
  total_preferred_count: number;
  matched_required_count: number;
  matched_preferred_count: number;
}

// Gap Analysis (M4)
export type RequirementClassification = 'matched' | 'partially_demonstrated' | 'not_demonstrated';
export type RequirementType = 'required' | 'preferred';

export interface GapAnalysisItem {
  requirement: string;
  requirement_type: RequirementType;
  classification: RequirementClassification;
  match_method: MatchMethod;
  similarity_score: number;
  resume_evidence?: string | null;
  job_evidence?: string | null;
  explanation: string;
  suggested_improvement?: string | null;
}

export interface CoverageBreakdown {
  total_count: number;
  matched_count: number;
  partial_count: number;
  not_demonstrated_count: number;
  coverage_score: number | null;
  calculation_explanation: string;
}

export interface OverallCoverage {
  overall_score: number | null;
  required_weight_percent: number;
  preferred_weight_percent: number;
  explanation: string;
  disclaimer: string;
}

export interface GapAnalysisResponse {
  results: GapAnalysisItem[];
  matched_requirements: GapAnalysisItem[];
  partially_demonstrated_requirements: GapAnalysisItem[];
  not_demonstrated_requirements: GapAnalysisItem[];
  required_coverage: CoverageBreakdown;
  preferred_coverage: CoverageBreakdown;
  overall_coverage: OverallCoverage;
}

// Personalized Roadmap (M5)
export type RoadmapPriority = 'critical' | 'high' | 'medium' | 'low';

export interface RoadmapStep {
  step_number: number;
  skill_name: string;
  category: string;
  priority: RoadmapPriority;
  is_prerequisite_for?: string | null;
  why_it_matters: string;
  current_evidence?: string | null;
  learning_topics: string[];
  practical_project: string;
  expected_deliverable: string;
  estimated_hours: number;
}

export interface RoadmapSummary {
  total_steps: number;
  critical_steps_count: number;
  high_steps_count: number;
  medium_steps_count: number;
  low_steps_count: number;
  total_estimated_hours: number;
}

export interface RoadmapResponse {
  summary: RoadmapSummary;
  roadmap: RoadmapStep[];
  gap_summary: string;
}

// Resume Improvement (M6)
export type SuggestionConfidence = 'high' | 'medium' | 'low';

export interface EvidenceReference {
  source_section: string;
  evidence_text: string;
  related_job_requirement?: string | null;
}

export interface CandidateQuestion {
  context: string;
  question: string;
  why_needed: string;
}

export interface BulletImprovement {
  id: string;
  section_name: string;
  original_text: string;
  suggested_text: string;
  why_useful: string;
  relevant_job_requirement?: string | null;
  evidence: EvidenceReference[];
  confidence: SuggestionConfidence;
  needs_candidate_info: boolean;
  candidate_questions: CandidateQuestion[];
}

export interface SectionRecommendation {
  section_name: string;
  status: string;
  recommendations: string[];
  skills_to_highlight: string[];
  irrelevant_or_repetitive_notes: string[];
}

export interface JobRelevanceAnalysis {
  top_aligned_strengths: string[];
  buried_skills: string[];
  missing_critical_evidence: string[];
  honesty_guardrails_applied: string[];
}

export interface ImprovementSummary {
  total_bullet_improvements: number;
  high_confidence_improvements: number;
  questions_for_candidate: number;
  overall_readiness: string;
}

export interface ResumeImprovementResponse {
  summary: ImprovementSummary;
  bullet_improvements: BulletImprovement[];
  section_recommendations: SectionRecommendation[];
  job_relevance: JobRelevanceAnalysis;
  candidate_questions: CandidateQuestion[];
}
