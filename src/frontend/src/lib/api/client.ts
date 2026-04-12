import type { Chest, ChestCreate, ChestUpdate } from '$lib/models/schemas';
import type { Source, SourceCreate, SourceUpdate } from '$lib/models/schemas';
import type { RAGQuery, RAGResponse } from '$lib/models/schemas';

// Base URL for API - in production, this would come from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Chest API functions
export const chestAPI = {
	getAll: async (): Promise<Chest[]> => {
		const response = await fetch(`${API_BASE_URL}/api/chests/`);
		if (!response.ok) {
			throw new Error(`Failed to fetch chests: ${response.status}`);
		}
		return response.json();
	},
	
	create: async (chestData: ChestCreate): Promise<Chest> => {
		const response = await fetch(`${API_BASE_URL}/api/chests/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(chestData),
		});
		if (!response.ok) {
			throw new Error(`Failed to create chest: ${response.status}`);
		}
		return response.json();
	},
	
	getById: async (id: number): Promise<Chest> => {
		const response = await fetch(`${API_BASE_URL}/api/chests/${id}`);
		if (!response.ok) {
			throw new Error(`Failed to fetch chest: ${response.status}`);
		}
		return response.json();
	},
	
	update: async (id: number, chestData: ChestUpdate): Promise<Chest> => {
		const response = await fetch(`${API_BASE_URL}/api/chests/${id}`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(chestData),
		});
		if (!response.ok) {
			throw new Error(`Failed to update chest: ${response.status}`);
		}
		return response.json();
	},
	
	delete: async (id: number): Promise<void> => {
		const response = await fetch(`${API_BASE_URL}/api/chests/${id}`, {
			method: 'DELETE',
		});
		if (!response.ok) {
			throw new Error(`Failed to delete chest: ${response.status}`);
		}
	}
};

// Source API functions
export const sourceAPI = {
	getByChest: async (chestId: number): Promise<Source[]> => {
		const response = await fetch(`${API_BASE_URL}/api/sources/?chest_id=${chestId}`);
		if (!response.ok) {
			throw new Error(`Failed to fetch sources: ${response.status}`);
		}
		return response.json();
	},
	
	create: async (sourceData: SourceCreate): Promise<Source> => {
		const response = await fetch(`${API_BASE_URL}/api/sources/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(sourceData),
		});
		if (!response.ok) {
			throw new Error(`Failed to create source: ${response.status}`);
		}
		return response.json();
	},
	
	getById: async (id: number): Promise<Source> => {
		const response = await fetch(`${API_BASE_URL}/api/sources/${id}`);
		if (!response.ok) {
			throw new Error(`Failed to fetch source: ${response.status}`);
		}
		return response.json();
	},
	
	update: async (id: number, sourceData: SourceUpdate): Promise<Source> => {
		const response = await fetch(`${API_BASE_URL}/api/sources/${id}`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(sourceData),
		});
		if (!response.ok) {
			throw new Error(`Failed to update source: ${response.status}`);
		}
		return response.json();
	},
	
	delete: async (id: number): Promise<void> => {
		const response = await fetch(`${API_BASE_URL}/api/sources/${id}`, {
			method: 'DELETE',
		});
		if (!response.ok) {
			throw new Error(`Failed to delete source: ${response.status}`);
		}
	}
};

// Chat/RAG API functions
export const chatAPI = {
	query: async (query: RAGQuery): Promise<RAGResponse> => {
		const response = await fetch(`${API_BASE_URL}/api/chat/query`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(query),
		});
		if (!response.ok) {
			throw new Error(`Failed to process query: ${response.status}`);
		}
		return response.json();
	}
};