import axios from 'axios';

// API configuration - Replace with your actual Django server URL
// For ngrok: const API_BASE_URL = 'https://your-ngrok-url.ngrok.io/api';
// For local network: const API_BASE_URL = 'http://YOUR_LOCAL_IP:8000/api';
const API_BASE_URL = 'http://localhost/api';
console.log('API_BASE_URL configured as:', API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const getToken = () => localStorage.getItem('access_token');
export const getRefreshToken = () => localStorage.getItem('refresh_token');
export const setTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};
export const setToken = (token: string) => localStorage.setItem('access_token', token);
export const removeTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
export const removeToken = () => removeTokens();

// Request interceptor to add auth header
api.interceptors.request.use((config) => {
  console.log('Making API request to:', config.baseURL + config.url);
  console.log('Request config:', config);
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.log('API Error:', error.response?.data);
    
    if (error.response?.status === 401) {
      const refreshToken = getRefreshToken();
      
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        
        try {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          setToken(access);
          
          // Retry the original request
          error.config.headers.Authorization = `Bearer ${access}`;
          return api.request(error.config);
        } catch (refreshError) {
          console.log('Token refresh failed:', refreshError);
          removeTokens();
          window.location.href = '/login';
        }
      } else {
        removeTokens();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/login/', credentials),
  register: (userData: { username: string; email: string; password: string }) =>
    api.post('/register/', userData),
  logout: () => api.post('/logout/'),
  refreshToken: (refreshToken: string) =>
    api.post('/token/refresh/', { refresh: refreshToken }),
  changePassword: (passwords: { old_password: string; new_password: string }) =>
    api.post('/change-password/', passwords),
};

export const eventsAPI = {
  list: (params?: string) => api.get(`/events/${params || ''}`),
  create: (data: any) => api.post('/events/', data),
  detail: (id: string) => api.get(`/events/${id}/`),
  update: (id: string, data: any) => api.patch(`/events/${id}/`, data),
  delete: (id: string) => api.delete(`/events/${id}/`),
};

export const budgetAPI = {
  list: (eventId?: string, params?: string) => 
    api.get('/budget-items/', { params: { event: eventId, ...(params ? Object.fromEntries(new URLSearchParams(params)) : {}) } }),
  create: (data: any) => api.post('/budget-items/', data),
  update: (id: string, data: any) => api.patch(`/budget-items/${id}/`, data),
  delete: (id: string) => api.delete(`/budget-items/${id}/`),
};

export const pledgesAPI = {
  list: (eventId?: string, params?: string) => 
    api.get('/pledges/', { params: { event: eventId, ...(params ? Object.fromEntries(new URLSearchParams(params)) : {}) } }),
  create: (data: any) => api.post('/pledges/', data),
  update: (id: string, data: any) => api.patch(`/pledges/${id}/`, data),
  delete: (id: string) => api.delete(`/pledges/${id}/`),
};

export const manualPaymentsAPI = {
  list: (params?: string) => api.get(`/manual-payments/${params || ''}`),
  listByPledge: (pledgeId: string) => api.get(`/pledges/${pledgeId}/manual-payments/`),
  create: (pledgeId: string, data: any) => api.post(`/pledges/${pledgeId}/manual-payments/`, data),
  detail: (id: string) => api.get(`/manual-payments/${id}/`),
  update: (id: string, data: any) => api.put(`/manual-payments/${id}/`, data),
  delete: (id: string) => api.delete(`/manual-payments/${id}/`),
};

export const mpesaPaymentsAPI = {
  list: (params?: string) => api.get(`/mpesa-payments/${params || ''}`),
  create: (data: any) => api.post('/mpesa-payments/', data),
  detail: (id: string) => api.get(`/mpesa-payments/${id}/`),
  update: (id: string, data: any) => api.put(`/mpesa-payments/${id}/`, data),
  delete: (id: string) => api.delete(`/mpesa-payments/${id}/`),
};

export const serviceProvidersAPI = {
  list: (params?: string) => api.get(`/service-providers/${params || ''}`),
  create: (data: any) => api.post('/service-providers/', data),
  detail: (id: string) => api.get(`/service-providers/${id}/`),
  update: (id: string, data: any) => api.patch(`/service-providers/${id}/`, data),
  delete: (id: string) => api.delete(`/service-providers/${id}/`),
};

export const vendorPaymentsAPI = {
  list: (params?: string) => api.get(`/vendor-payments/${params || ''}`),
  create: (data: any) => api.post('/vendor-payments/', data),
  detail: (id: string) => api.get(`/vendor-payments/${id}/`),
  update: (id: string, data: any) => api.patch(`/vendor-payments/${id}/`, data),
  delete: (id: string) => api.delete(`/vendor-payments/${id}/`),
};

export const tasksAPI = {
  list: (params?: { budget_item?: number }) => api.get('/tasks/', { params }),
  create: (data: any) => api.post('/tasks/', data),
  detail: (id: number) => api.get(`/tasks/${id}/`),
  update: (id: number, data: any) => api.patch(`/tasks/${id}/`, data),
  delete: (id: number) => api.delete(`/tasks/${id}/`),
};

export const dashboardAPI = {
  general: () => api.get('/dashboard/'),
  event: (eventId: string) => api.get(`/dashboard/${eventId}/`),
  recentActivities: () => api.get('/recent-activities/'),
};