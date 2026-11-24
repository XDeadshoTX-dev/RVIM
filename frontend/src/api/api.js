import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authAPI = {
  signUp: (data) => api.post('/auth/sign-up', data),
  logIn: (data) => api.post('/auth/log-in', data),
  logOut: () => api.post('/auth/log-out'),
  getMe: () => api.get('/auth/me'), // ← ДОДАНО
  getGithubAvatar: (email) => api.get(`/auth/github-avatar?email=${encodeURIComponent(email)}`),
};

export const todoAPI = {
  getLists: () => api.get('/todo/lists'),
  createList: (data) => api.post('/todo/lists/create', data),
  updateList: (id, data) => api.patch(`/todo/lists/${id}`, data),
  deleteList: (id) => api.delete(`/todo/lists/${id}/delete`),
  
  getListItems: (listId) => api.get(`/todo/lists/${listId}/items`),
  createItem: (data) => api.post('/todo/items/create', data),
  updateItem: (id, data) => api.patch(`/todo/items/${id}`, data),
  deleteItem: (id) => api.delete(`/todo/items/${id}/delete`),
};

export default api;