const API_BASE = '/api';

export interface Chest {
	id: string;
	name: string;
	created_at: string;
	updated_at: string;
}

export interface Source {
	id: string;
	chest_id: string;
	name: string;
	type: 'TXT' | 'URL' | 'FILE';
	content: string | null;
	content_hash: string | null;
	is_enabled: boolean;
	created_at: string;
}

export interface ChatMessage {
	id: string;
	chest_id: string;
	role: 'USER' | 'ASSISTANT';
	content: string;
	sources_used: string[] | null;
	created_at: string;
}

export interface SourceInput {
	name: string;
	type: 'TXT' | 'URL' | 'FILE';
	content?: string;
}

class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE) {
		this.baseUrl = baseUrl;
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<T> {
		const url = `${this.baseUrl}${endpoint}`;
		const response = await fetch(url, {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options.headers,
			},
		});

		if (!response.ok) {
			const error = await response.json().catch(() => ({}));
			throw new Error(error.detail || `HTTP ${response.status}`);
		}

		if (response.status === 204) {
			return undefined as T;
		}

		return response.json();
	}

	async getChests(): Promise<Chest[]> {
		return this.request<Chest[]>('/chests');
	}

	async createChest(name: string): Promise<Chest> {
		return this.request<Chest>('/chests', {
			method: 'POST',
			body: JSON.stringify({ name }),
		});
	}

	async updateChest(id: string, name: string): Promise<Chest> {
		return this.request<Chest>(`/chests/${id}`, {
			method: 'PATCH',
			body: JSON.stringify({ name }),
		});
	}

	async deleteChest(id: string): Promise<void> {
		return this.request<void>(`/chests/${id}`, { method: 'DELETE' });
	}

	async getSources(chestId: string): Promise<Source[]> {
		return this.request<Source[]>(`/chests/${chestId}/sources`);
	}

	async createSources(chestId: string, sources: SourceInput[]): Promise<Source[]> {
		return this.request<Source[]>(`/chests/${chestId}/sources/batch`, {
			method: 'POST',
			body: JSON.stringify(sources),
		});
	}

	async updateSource(id: string, data: Partial<Source>): Promise<Source> {
		return this.request<Source>(`/sources/${id}`, {
			method: 'PATCH',
			body: JSON.stringify(data),
		});
	}

	async deleteSource(id: string): Promise<void> {
		return this.request<void>(`/sources/${id}`, { method: 'DELETE' });
	}

	async getMessages(chestId: string): Promise<ChatMessage[]> {
		return this.request<ChatMessage[]>(`/chests/${chestId}/messages`);
	}

	async *chat(chestId: string, message: string) {
		const response = await fetch(`${this.baseUrl}/chests/${chestId}/chat`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ message }),
		});

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}`);
		}

		const reader = response.body?.getReader();
		if (!reader) throw new Error('No response body');

		const decoder = new TextDecoder();
		let buffer = '';

		while (true) {
			const { done, value } = await reader.read();
			if (done) break;

			buffer += decoder.decode(value, { stream: true });
			const lines = buffer.split('\n');
			buffer = lines.pop() || '';

			for (const line of lines) {
				if (line.startsWith('data: ')) {
					try {
						yield JSON.parse(line.slice(6));
					} catch {
						// Skip invalid JSON
					}
				}
			}
		}
	}
}

export const api = new ApiClient();
