import { ApiError } from './types';

const API_BASE_URL = '/api'; // Relative path, rewritten by Next.js to backend

class ApiClient {
    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('token');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        return headers;
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const error: ApiError = {
                error_code: errorData.error_code || 'UNKNOWN_ERROR',
                message: errorData.message || response.statusText,
                details: errorData.details,
            };
            throw error;
        }
        // Return empty object for 204 No Content
        if (response.status === 204) return {} as T;
        return response.json();
    }

    async get<T>(endpoint: string): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse<T>(response);
    }

    async post<T>(endpoint: string, body?: any): Promise<T> {
        const headers = this.getHeaders();
        // Don't set Content-Type for FormData
        if (body instanceof FormData) {
            delete (headers as any)['Content-Type'];
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: body instanceof FormData ? body : JSON.stringify(body),
        });
        return this.handleResponse<T>(response);
    }

    async put<T>(endpoint: string, body: any): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(body),
        });
        return this.handleResponse<T>(response);
    }

    async delete<T>(endpoint: string): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });
        return this.handleResponse<T>(response);
    }
}

export const api = new ApiClient();
