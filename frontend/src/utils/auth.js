// src/utils/auth.js
import { supabase } from '../config/supabaseClient';

// Register a new user
export const registerUser = async (email, password, options = {}) => {
  console.log(`Attempting registration with: ${email}`);
  console.log('Calling Supabase for registration...');

  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        redirectTo: options.redirectTo || window.location.origin + '/dashboard',
        ...options,
      },
    });

    console.log('Registration response:', data);

    if (error) {
      console.error('Registration error:', error);
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

// Login user
export const loginUser = async (email, password) => {
  console.log(`Attempting login with: ${email}`);

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.error('Login error:', error);
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// Logout user
export const logout = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    // Redirect will happen automatically via AuthContext listener
  } catch (error) {
    console.error('Error during logout:', error);
    // Fallback in case of error
    localStorage.removeItem('testUser');
    window.location.href = '/login';
  }
};

// Get current session
export const getCurrentSession = async () => {
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    return data.session;
  } catch (error) {
    console.error('Error getting session:', error);
    return null;
  }
};

// Get current user
export const getCurrentUser = async () => {
  try {
    const { data, error } = await supabase.auth.getUser();
    if (error) throw error;
    return data.user;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
};

// Refresh session
export const refreshSession = async () => {
  try {
    const { data, error } = await supabase.auth.refreshSession();
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error refreshing session:', error);
    return null;
  }
};
