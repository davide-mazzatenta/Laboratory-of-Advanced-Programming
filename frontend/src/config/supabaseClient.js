import { createClient } from '@supabase/supabase-js';

// Updated Supabase credentials
const supabaseUrl = 'https://sjfdkgzmjaasjtavuhfu.supabase.co';
const supabaseAnonKey =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqZmRrZ3ptamFhc2p0YXZ1aGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE5NDUwNTIsImV4cCI6MjA1NzUyMTA1Mn0.dWBqYF31Ot73oXqf8v2KaMj37Tkzb3dd7Szq1WviDPA';

// JWT Configuration options
const supabaseOptions = {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
};

// Create and export the Supabase client with options
export const supabase = createClient(
  supabaseUrl,
  supabaseAnonKey,
  supabaseOptions,
);

// Export the function to get the Supabase client
export const getSupabaseClient = () => supabase;

// Helper function to get JWT token from session
export const getAuthToken = async () => {
  const { data, error } = await supabase.auth.getSession();
  if (error) {
    console.error('Error retrieving auth session:', error);
    return null;
  }
  return data?.session?.access_token || null;
};
