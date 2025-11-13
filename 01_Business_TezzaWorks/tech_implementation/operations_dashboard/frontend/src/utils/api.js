import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Clients API
export const clientsAPI = {
  getAll: (params) => api.get('/clients', { params }),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  getInteractions: (id) => api.get(`/clients/${id}/interactions`),
  createInteraction: (id, data) => api.post(`/clients/${id}/interactions`, data),
  getStats: (id) => api.get(`/clients/${id}/stats`),
}

// Products API
export const productsAPI = {
  getAll: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  calculatePricing: (id, data) => api.post(`/products/${id}/pricing`, data),
  getLowStock: () => api.get('/products/low-stock'),
  getCategories: () => api.get('/products/categories'),
}

// Orders API
export const ordersAPI = {
  getAll: (params) => api.get('/orders', { params }),
  getById: (id) => api.get(`/orders/${id}`),
  create: (data) => api.post('/orders', data),
  update: (id, data) => api.put(`/orders/${id}`, data),
  delete: (id) => api.delete(`/orders/${id}`),
  updateStatus: (id, status) => api.put(`/orders/${id}/status`, { status }),
  getKanban: () => api.get('/orders/kanban'),
  getAnalytics: (params) => api.get('/orders/analytics', { params }),
  generateQuote: (data) => api.post('/orders/quote', data),
}

// Export functions
export const exportAPI = {
  exportOrders: (params) => api.get('/export/orders', { params, responseType: 'blob' }),
  exportClients: (params) => api.get('/export/clients', { params, responseType: 'blob' }),
  exportProducts: (params) => api.get('/export/products', { params, responseType: 'blob' }),
}

export default api
