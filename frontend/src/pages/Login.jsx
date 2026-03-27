// src/pages/Login.jsx
import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { theme } = useContext(ThemeContext);
  const {
    signIn,
    signUp,
    signInWithOAuth,
    user,
    loading: authLoading,
  } = useAuth();
  const isDarkTheme = theme.palette.mode === 'dark';

  // State per il controllo delle tab
  const [activeTab, setActiveTab] = useState('login');
  // State per il controllo delle notifiche
  const [notification, setNotification] = useState({
    show: false,
    message: '',
    type: '',
  });
  // State per i form
  const [loginFormData, setLoginFormData] = useState({
    email: '',
    password: '',
    remember: false,
  });
  const [registerFormData, setRegisterFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    termsAccepted: false,
  });
  const [loading, setLoading] = useState(false);

  // State per i modal
  const [showEmailConfirmModal, setShowEmailConfirmModal] = useState(false);
  const [resetPasswordModal, setResetPasswordModal] = useState({
    show: false,
    email: '',
  });

  // Controlla se l'utente è già autenticato - UPDATED to use simplified auth
  useEffect(() => {
    if (user) {
      console.log('User already authenticated, redirecting to home');
      navigate('/');
    }
  }, [user, navigate]);

  // Applica la classe di scope quando il componente viene montato
  useEffect(() => {
    document.body.classList.add('login-page-scope');

    // Aggiungi dark-theme se necessario
    if (isDarkTheme) {
      document.body.classList.add('dark-theme');
    }

    return () => {
      document.body.classList.remove('login-page-scope');
      if (isDarkTheme) {
        document.body.classList.remove('dark-theme');
      }
    };
  }, [isDarkTheme]);

  // Funzione per mostrare notifiche
  const showNotification = (message, type) => {
    console.log(`Notification: ${type} - ${message}`);
    setNotification({ show: true, message, type });

    setTimeout(() => {
      setNotification((prev) => ({ ...prev, show: false }));
    }, 5000);
  };

  // Cambio tab
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setNotification({ show: false, message: '', type: '' });
  };

  // UPDATED: Simplified login using AuthContext
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    console.log('Tentativo di login con:', loginFormData.email);

    try {
      const { email, password } = loginFormData;

      // Use simplified AuthContext signIn
      const { data, error } = await signIn(email, password);

      if (error) throw error;

      // Save email if remember is checked
      if (loginFormData.remember) {
        localStorage.setItem('savedEmail', email);
      }

      showNotification('Accesso effettuato con successo', 'success');

      // Navigation will be handled by AuthContext
    } catch (error) {
      console.error('Errore login:', error);
      showNotification(error.message || 'Credenziali non valide', 'error');
    } finally {
      setLoading(false);
    }
  };

  // UPDATED: Simplified registration using AuthContext
  const handleRegister = async (e) => {
    e.preventDefault();

    const { email, password, confirmPassword, termsAccepted } =
      registerFormData;
    console.log('Tentativo di registrazione con:', email);

    if (!termsAccepted) {
      showNotification(
        'Per favore accetta i termini e condizioni per continuare',
        'error',
      );
      return;
    }

    if (password !== confirmPassword) {
      showNotification('Le password non corrispondono', 'error');
      return;
    }

    setLoading(true);

    try {
      // Use simplified AuthContext signUp
      const { data, error } = await signUp(email, password);

      if (error) throw error;

      showNotification(
        'Registrazione completata! Ti abbiamo inviato un email di conferma.',
        'success',
      );

      // Mostra il modal di conferma email
      setShowEmailConfirmModal(true);

      setTimeout(() => {
        setActiveTab('login');
        setLoginFormData((prev) => ({ ...prev, email }));

        // Se non è richiesta la verifica dell'email, reindirizza
        if (data?.user && !data?.session) {
          showNotification(
            'Verifica la tua email per completare la registrazione',
            'info',
          );
        } else if (data?.session) {
          // L'utente è già autenticato, reindirizza
          navigate('/');
        }
      }, 2000);
    } catch (error) {
      console.error('Errore registrazione:', error);
      showNotification(
        error.message || 'Errore durante la registrazione',
        'error',
      );
    } finally {
      setLoading(false);
    }
  };

  // UPDATED: Simplified Google sign in using AuthContext
  const handleGoogleSignIn = async () => {
    setLoading(true);
    console.log('Tentativo di login con Google');

    try {
      const { data, error } = await signInWithOAuth('google');

      if (error) throw error;

      // OAuth will redirect automatically, no need to do anything else
    } catch (error) {
      console.error('Errore Google auth:', error);
      showNotification(
        error.message || 'Errore durante il login con Google',
        'error',
      );
      setLoading(false);
    }
  };

  // UPDATED: Simplified forgot password using AuthContext
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    const { email } = loginFormData;
    console.log('Tentativo recupero password per:', email);

    if (!email) {
      showNotification(
        'Inserisci la tua email per reimpostare la password',
        'error',
      );
      return;
    }

    setLoading(true);

    try {
      // We'll need to add this method to AuthContext, or use supabase directly
      const { supabase } = await import('../config/supabaseClient');
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) throw error;

      showNotification(
        'Ti abbiamo inviato un email con le istruzioni per reimpostare la password',
        'success',
      );

      // Mostra il modal di reset password
      setResetPasswordModal({
        show: true,
        email: email,
      });
    } catch (error) {
      console.error('Errore reset password:', error);
      showNotification(
        error.message || 'Errore durante il recupero password',
        'error',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`auth-page ${isDarkTheme ? 'dark-theme' : ''}`}>
      {/* Decorative elements */}
      <div className="decoration decoration-1"></div>
      <div className="decoration decoration-2"></div>
      <div className="legal-pattern"></div>

      <div className="auth-layout">
        {/* Logo */}
        <div className="logo-container">
          <div className="logo">
            <span className="logo-embellishment top-right"></span>
            <div className="logo-main">VALIS</div>
            <span className="logo-embellishment bottom-left"></span>
          </div>
          <div className="logo-tagline">by Lexygraph AI</div>
        </div>

        {/* Main Authentication Container */}
        <div className="auth-container">
          {/* Overlay di caricamento */}
          {loading && (
            <div className="loading-overlay">
              <div className="loading-spinner"></div>
            </div>
          )}

          <div className="tabs">
            <div
              className={`tab-btn ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => handleTabChange('login')}
            >
              Accesso
            </div>
            <div
              className={`tab-btn ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => handleTabChange('register')}
            >
              Registrazione
            </div>
            <div
              className="tab-indicator"
              style={{
                transform: `translateX(${activeTab === 'login' ? '0%' : '100%'})`,
              }}
            ></div>
          </div>

          {notification.show && (
            <div className={`notification ${notification.type}`}>
              <i
                className={`fas ${notification.type === 'success' ? 'fa-check-circle' : notification.type === 'info' ? 'fa-info-circle' : 'fa-exclamation-circle'}`}
              ></i>
              <span>{notification.message}</span>
            </div>
          )}

          {/* Login Form */}
          <div
            className={`tab-content ${activeTab === 'login' ? 'active' : ''}`}
            id="login-content"
          >
            <form id="login-form" onSubmit={handleLogin}>
              <div className="form-group">
                <div className="input-container">
                  <input
                    type="email"
                    className="form-control"
                    id="login-email"
                    placeholder=" "
                    required
                    value={loginFormData.email}
                    onChange={(e) =>
                      setLoginFormData({
                        ...loginFormData,
                        email: e.target.value,
                      })
                    }
                    disabled={loading}
                  />
                  <label className="form-label" htmlFor="login-email">
                    Indirizzo Email
                  </label>
                </div>
              </div>

              <div className="form-group">
                <div className="input-container">
                  <input
                    type="password"
                    className="form-control"
                    id="login-password"
                    placeholder=" "
                    required
                    value={loginFormData.password}
                    onChange={(e) =>
                      setLoginFormData({
                        ...loginFormData,
                        password: e.target.value,
                      })
                    }
                    disabled={loading}
                  />
                  <label className="form-label" htmlFor="login-password">
                    Password
                  </label>
                  <i
                    className="fas fa-eye password-toggle"
                    onClick={() => {
                      const input = document.getElementById('login-password');
                      const icon = document.querySelector(
                        '#login-form .password-toggle',
                      );
                      if (input.type === 'password') {
                        input.type = 'text';
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                      } else {
                        input.type = 'password';
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                      }
                    }}
                  ></i>
                </div>
              </div>

              <div className="remember-forgot">
                <label className="remember-me">
                  <input
                    type="checkbox"
                    className="remember-checkbox"
                    id="remember"
                    checked={loginFormData.remember}
                    onChange={(e) =>
                      setLoginFormData({
                        ...loginFormData,
                        remember: e.target.checked,
                      })
                    }
                    disabled={loading}
                  />
                  <div className="custom-checkbox">
                    <i className="fas fa-check"></i>
                  </div>
                  <span className="remember-text">Ricordami</span>
                </label>

                <button
                  type="button"
                  className="forgot-link"
                  onClick={handleForgotPassword}
                  disabled={loading}
                >
                  Password dimenticata?
                </button>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Caricamento...' : 'Accedi'}
              </button>

              <button
                type="button"
                className="btn btn-social"
                onClick={handleGoogleSignIn}
                disabled={loading}
              >
                <i className="fab fa-google"></i>
                {loading ? 'Caricamento...' : 'Accedi con Google'}
              </button>
            </form>
          </div>

          {/* Register Form */}
          <div
            className={`tab-content ${activeTab === 'register' ? 'active' : ''}`}
            id="register-content"
          >
            <form id="register-form" onSubmit={handleRegister}>
              <div className="form-group">
                <div className="input-container">
                  <input
                    type="email"
                    className="form-control"
                    id="register-email"
                    placeholder=" "
                    required
                    value={registerFormData.email}
                    onChange={(e) =>
                      setRegisterFormData({
                        ...registerFormData,
                        email: e.target.value,
                      })
                    }
                    disabled={loading}
                  />
                  <label className="form-label" htmlFor="register-email">
                    Indirizzo Email
                  </label>
                </div>
              </div>

              <div className="form-group">
                <div className="input-container">
                  <input
                    type="password"
                    className="form-control"
                    id="register-password"
                    placeholder=" "
                    required
                    value={registerFormData.password}
                    onChange={(e) => {
                      setRegisterFormData({
                        ...registerFormData,
                        password: e.target.value,
                      });

                      // Mostra indicatore forza password
                      const passwordStrength =
                        document.querySelector('.password-strength');
                      if (passwordStrength) {
                        passwordStrength.style.display = e.target.value
                          ? 'block'
                          : 'none';
                      }
                    }}
                    disabled={loading}
                  />
                  <label className="form-label" htmlFor="register-password">
                    Password
                  </label>
                  <i
                    className="fas fa-eye password-toggle"
                    onClick={() => {
                      const input =
                        document.getElementById('register-password');
                      const icon = document.querySelector(
                        '#register-form .password-toggle',
                      );
                      if (input.type === 'password') {
                        input.type = 'text';
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                      } else {
                        input.type = 'password';
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                      }
                    }}
                  ></i>
                </div>
                <div
                  className="password-strength"
                  style={{
                    display: registerFormData.password ? 'block' : 'none',
                  }}
                >
                  <div
                    className="password-strength-meter"
                    style={{
                      width: `${registerFormData.password.length > 8 ? 100 : registerFormData.password.length * 12.5}%`,
                      backgroundColor:
                        registerFormData.password.length <= 4
                          ? 'var(--error-color)'
                          : registerFormData.password.length <= 8
                            ? '#ed8936'
                            : 'var(--success-color)',
                    }}
                  ></div>
                </div>
                <div className="form-help">
                  Usa almeno 8 caratteri con lettere, numeri e simboli
                </div>
              </div>

              <div className="form-group">
                <div className="input-container">
                  <input
                    type="password"
                    className="form-control"
                    id="confirm-password"
                    placeholder=" "
                    required
                    value={registerFormData.confirmPassword}
                    onChange={(e) =>
                      setRegisterFormData({
                        ...registerFormData,
                        confirmPassword: e.target.value,
                      })
                    }
                    disabled={loading}
                  />
                  <label className="form-label" htmlFor="confirm-password">
                    Conferma Password
                  </label>
                  <i
                    className="fas fa-eye password-toggle"
                    onClick={() => {
                      const input = document.getElementById('confirm-password');
                      const icon = input.nextElementSibling.nextElementSibling;
                      if (input.type === 'password') {
                        input.type = 'text';
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                      } else {
                        input.type = 'password';
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                      }
                    }}
                  ></i>
                </div>
              </div>

              <label className="terms-checkbox">
                <input
                  type="checkbox"
                  id="terms-accept"
                  required
                  checked={registerFormData.termsAccepted}
                  onChange={(e) =>
                    setRegisterFormData({
                      ...registerFormData,
                      termsAccepted: e.target.checked,
                    })
                  }
                  disabled={loading}
                />
                <div className="terms-custom-checkbox">
                  <i className="fas fa-check"></i>
                </div>
                <span className="terms-text">
                  Accetto i{' '}
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    Termini di Servizio
                  </a>{' '}
                  e la{' '}
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    Privacy Policy
                  </a>
                </span>
              </label>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Caricamento...' : 'Registrati'}
              </button>

              <button
                type="button"
                className="btn btn-social"
                onClick={handleGoogleSignIn}
                disabled={loading}
              >
                <i className="fab fa-google"></i>
                {loading ? 'Caricamento...' : 'Registrati con Google'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Modal di conferma email */}
      {showEmailConfirmModal && (
        <div className="email-confirm-modal">
          <div className="modal-content">
            <div className="modal-icon">
              <i className="fas fa-envelope"></i>
            </div>
            <h3>Controlla la tua email</h3>
            <p>
              Abbiamo inviato un'email di conferma a{' '}
              <strong>{registerFormData.email}</strong>
            </p>
            <p>
              Per completare la registrazione, clicca sul link nell'email che ti
              abbiamo inviato.
            </p>
            <p className="note">
              Non vedi l'email? Controlla nella cartella spam o junk.
            </p>
            <button
              className="btn btn-primary"
              onClick={() => setShowEmailConfirmModal(false)}
            >
              Ho capito
            </button>
          </div>
        </div>
      )}

      {/* Modal di reset password */}
      {resetPasswordModal.show && (
        <div className="email-confirm-modal">
          <div className="modal-content">
            <div className="modal-icon">
              <i className="fas fa-key"></i>
            </div>
            <h3>Reset Password</h3>
            <p>
              Abbiamo inviato un'email con le istruzioni per reimpostare la
              password a <strong>{resetPasswordModal.email}</strong>
            </p>
            <p>
              Segui le istruzioni nell'email per impostare una nuova password.
            </p>
            <p className="note">
              Non vedi l'email? Controlla nella cartella spam or junk.
            </p>
            <button
              className="btn btn-primary"
              onClick={() => setResetPasswordModal({ show: false, email: '' })}
            >
              Ho capito
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
