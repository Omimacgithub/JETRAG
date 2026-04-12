// These schemas mirror the backend Pydantic models for TypeScript type safety
export interface ChestBase {
	name: string;
}

export interface ChestCreate extends ChestBase {
}

export interface ChestUpdate {
	name?: string;
}

export interface Chest extends ChestBase {
	id: number;
	created_at: string; // ISO date string
	updated_at: string | null;
}

export interface SourceBase {
	name: string;
	type: 'TXT' | 'URL' | 'FILE';
	content?: string;
	is_enabled?: boolean;
}

export interface SourceCreate extends SourceBase {
	chest_id: number;
}

export interface SourceUpdate {
	name?: string;
	type?: 'TXT' | 'URL' | 'FILE';
	content?: string;
	is_enabled?: boolean;
}

export interface Source extends SourceBase {
	id: number;
	chest_id: number;
	content_hash?: string | null;
	created_at: string;
}

export interface ChatMessageBase {
	role: 'USER' | 'ASSISTANT';
	content: string;
	sources_used?: number[] | null;
}

export interface ChatMessageCreate extends ChatMessageBase {
	chest_id: number;
}

export interface ChatMessage extends ChatMessageBase {
	id: number;
	chest_id: number;
	created_at: string;
}

export interface RAGQuery {
	question: string;
	chest_id: number;
}

export interface RAGResponse {
	answer: string;
	sources_used: number[];
}