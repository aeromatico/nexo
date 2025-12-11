import axios from 'axios';

export class NexoAPIClient {
  constructor(baseURL = '/api/method') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response.data.message || response.data,
      (error) => {
        if (error.response?.status === 401) {
          this.handleUnauthorized();
        }
        return Promise.reject(error.response?.data || error);
      }
    );
  }

  getToken() {
    try {
      const auth = localStorage.getItem('auth-storage');
      if (auth) {
        const parsed = JSON.parse(auth);
        return parsed.state?.token;
      }
    } catch (error) {
      console.error('Failed to get token:', error);
    }
    return null;
  }

  handleUnauthorized() {
    localStorage.removeItem('auth-storage');
    window.location.href = '/login';
  }

  async get(endpoint, params = {}) {
    const response = await this.client.get(endpoint, { params });
    return response;
  }

  async post(endpoint, body) {
    const response = await this.client.post(endpoint, body);
    return response;
  }

  async put(endpoint, body) {
    const response = await this.client.put(endpoint, body);
    return response;
  }

  async delete(endpoint) {
    const response = await this.client.delete(endpoint);
    return response;
  }
}

export default new NexoAPIClient();
