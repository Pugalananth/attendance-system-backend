/**
 * Enterprise API Service Layer
 * AI Face Attendance System
 */

import axios from 'axios';

import AsyncStorage from
'@react-native-async-storage/async-storage';

// =====================================================
// BASE URL
// =====================================================

// ANDROID EMULATOR
// const BASE_URL =
// 'http://10.0.2.2:5000/api';

// PHYSICAL DEVICE

const BASE_URL =
  'http://192.168.0.111:5000/api';

// =====================================================
// AXIOS INSTANCE
// =====================================================

const api = axios.create({

  baseURL: BASE_URL,

  timeout: 60000,

  headers: {

    'Content-Type':
      'application/json',

    Accept:
      'application/json',

  },
});

// =====================================================
// REQUEST INTERCEPTOR
// =====================================================

api.interceptors.request.use(

  async (config) => {

    try {

      const token =
        await AsyncStorage.getItem(
          'access_token'
        );

      if (token) {

        config.headers.Authorization =
          `Bearer ${token}`;
      }

      console.log(
        'API Request:',
        config.method?.toUpperCase(),
        config.url
      );

    } catch (error) {

      console.log(
        'Token Error:',
        error
      );
    }

    return config;
  },

  (error) =>
    Promise.reject(error)
);

// =====================================================
// RESPONSE INTERCEPTOR
// =====================================================

api.interceptors.response.use(

  (response) => {

    console.log(
      'API Response:',
      response.status,
      response.config.url
    );

    return response;
  },

  async (error) => {

    console.log(

      'API Error:',

      error?.response?.data ||

      error.message

    );

    // TOKEN EXPIRED

    if (
      error.response?.status === 401
    ) {

      await AsyncStorage.removeItem(
        'access_token'
      );

      await AsyncStorage.removeItem(
        'refresh_token'
      );

      await AsyncStorage.removeItem(
        'user_data'
      );
    }

    return Promise.reject(error);
  }
);

// =====================================================
// AUTH APIs
// =====================================================

export const authAPI = {

  // REGISTER

  register: async (data) => {

    return await api.post(

      '/auth/register',

      data

    );
  },

  // LOGIN

  login: async (

    email,

    password

  ) => {

    return await api.post(

      '/auth/login',

      {

        email,

        password,

      }

    );
  },

  // PROFILE

  getProfile: async () => {

    return await api.get(
      '/auth/profile'
    );
  },

  // VERIFY TOKEN

  verifyToken: async () => {

    return await api.get(
      '/auth/verify'
    );
  },

  // LOGOUT

  logout: async () => {

    try {

      await api.post(
        '/auth/logout'
      );

    } catch (error) {

      console.log(
        'Logout Error:',
        error
      );
    }

    await AsyncStorage.removeItem(
      'access_token'
    );

    await AsyncStorage.removeItem(
      'refresh_token'
    );

    await AsyncStorage.removeItem(
      'user_data'
    );
  },

  // SAVE AUTH

  saveAuthData: async (

    accessToken,

    refreshToken,

    user

  ) => {

    await AsyncStorage.setItem(

      'access_token',

      accessToken

    );

    await AsyncStorage.setItem(

      'refresh_token',

      refreshToken

    );

    await AsyncStorage.setItem(

      'user_data',

      JSON.stringify(user)

    );
  },

  // GET USER

  getStoredUser: async () => {

    const user =
      await AsyncStorage.getItem(
        'user_data'
      );

    return user
      ? JSON.parse(user)
      : null;
  },
};

// =====================================================
// ATTENDANCE APIs
// =====================================================

export const attendanceAPI = {

  // MARK ATTENDANCE

  markAttendance:
    async (data) => {

    return await api.post(

      '/attendance/mark',

      data

    );
  },

  // FACE ATTENDANCE

  faceAttendance:
    async (data) => {

    return await api.post(

      '/attendance/face-mark',

      data,

      {
        timeout: 120000,
      }

    );
  },

  // TODAY ATTENDANCE

  getTodayAttendance:
    async () => {

    return await api.get(
      '/attendance/today'
    );
  },

  // ALL ATTENDANCE

  getAllAttendance:
    async () => {

    return await api.get(
      '/attendance/all'
    );
  },

  // EMPLOYEE ATTENDANCE

  getEmployeeAttendance:
    async (employeeId) => {

    return await api.get(

      `/attendance/employee/${employeeId}`

    );
  },

  // LIVE ATTENDANCE

  getLiveAttendance:
    async () => {

    return await api.get(
      '/attendance/live'
    );
  },

  // TEAM ATTENDANCE

  getTeamAttendance:
    async () => {

    return await api.get(
      '/attendance/team'
    );
  },

  // SUMMARY

  getSummary:
    async () => {

    return await api.get(
      '/attendance/summary'
    );
  },

  // ANALYTICS

  getAnalytics:
    async () => {

    return await api.get(
      '/attendance/analytics'
    );
  },

  // MONTHLY REPORT

  getMonthlyReport:
    async () => {

    return await api.get(
      '/attendance/monthly-report'
    );
  },

  // EXPORT CSV

  exportCSV:
    async () => {

    return await api.get(

      '/attendance/export/csv',

      {

        responseType: 'blob',

      }

    );
  },

  // EXPORT PDF

  exportPDF:
    async () => {

    return await api.get(

      '/attendance/export/pdf',

      {

        responseType: 'blob',

      }

    );
  },
};

// =====================================================
// EMPLOYEE APIs
// =====================================================

export const employeeAPI = {

  getEmployees:
    async () => {

    return await api.get(
      '/employees'
    );
  },

  deleteEmployee:
    async (employeeId) => {

    return await api.delete(

      `/employees/${employeeId}`

    );
  },

};

// =====================================================
// ANALYTICS APIs
// =====================================================

export const analyticsAPI = {

  getAdminAnalytics:
    async () => {

    return await api.get(
      '/attendance/analytics'
    );
  },

  getHRAnalytics:
    async () => {

    return await api.get(
      '/attendance/analytics'
    );
  },

  getTeamAnalytics:
    async () => {

    return await api.get(
      '/attendance/analytics'
    );
  },

};

// =====================================================
// DEFAULT EXPORT
// =====================================================

export default api;