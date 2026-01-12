export interface User {
  id: string;
  username: string;
  // Add other user fields as needed
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Document {
  id: string;
  kb_id: string;
  filename: string;
  path?: string;
  file_type?: string;
  size?: number;
  status: 'processing' | 'ready' | 'failed';
  created_at: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at?: string;
}

export interface Citation {
  doc_id: string;
  filename: string;
  chunk_id: string;
  text: string;
  score?: number;
  page_number?: number; // For PDF
  line_range?: string; // For MD/TXT
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  kb_id: string;
  title: string;
  created_at: string;
  messages?: Message[];
}

export interface ApiError {
  error_code: string;
  message: string;
  details?: any;
}
