export type Decision = "allow" | "warn" | "block" | string;

export type Finding = {
  id?: string | null;
  category: string;
  severity: string;
  detector: string;
  title: string;
  description: string;
  evidence?: string | null;
  remediation?: string | null;
  confidence: number;
};

export type ScanContent = {
  title?: string | null;
  text?: string | null;
  content_type?: string | null;
  sanitized_html?: string | null;
};

export type Provenance = {
  retrieved_at?: string | null;
  content_hash?: string | null;
  redirect_chain: string[];
};

export type Scan = {
  scan_id: string;
  status: string;
  submitted_url: string;
  normalized_url?: string | null;
  final_url?: string | null;
  risk_score?: number | null;
  trust_score?: number | null;
  decision?: Decision | null;
  findings: Finding[];
  content?: ScanContent | null;
  provenance?: Provenance | null;
  score_explanation?: Record<string, unknown> | null;
  error_code?: string | null;
  error_message?: string | null;
  created_at?: string | null;
  completed_at?: string | null;
};

export type ScanList = {
  items: Scan[];
  total: number;
};
