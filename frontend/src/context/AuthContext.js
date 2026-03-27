import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../config/supabaseClient';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Get initial session
    const getInitialAuth = async () => {
      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.error('Initial auth error:', error);
        } else {
          setSession(session);
          setUser(session?.user ?? null);
          setUserId(session?.user?.id ?? null);
        }
      } catch (error) {
        console.error('Error getting initial auth:', error);
      } finally {
        setLoading(false);
      }
    };

    getInitialAuth();

    // Listen for auth changes - THIS IS THE MAIN AUTH FLOW
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      console.log(`Auth event: ${event}`);

      setSession(session);
      setUser(session?.user ?? null);
      setUserId(session?.user?.id ?? null);
      setLoading(false);

      // Handle redirects
      if (event === 'SIGNED_IN' && window.location.pathname === '/login') {
        window.location.href = '/';
      } else if (event === 'SIGNED_OUT') {
        window.location.href = '/login';
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const value = {
    user,
    userId,
    session,
    loading,
    isAuthenticated: () => !!user,

    signIn: async (email, password) => {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      return { data, error };
    },

    signUp: async (email, password) => {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: `${window.location.origin}/` },
      });
      return { data, error };
    },

    signOut: async () => {
      const { error } = await supabase.auth.signOut();
      return { error };
    },

    signInWithOAuth: async (provider) => {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: { redirectTo: `${window.location.origin}/` },
      });
      return { data, error };
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
