import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function OAuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token') || params.get('access_token');
    const role = params.get('role') || 'user';
    const redirect = params.get('redirect') || '/';

    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('role', role);
      navigate(redirect, { replace: true });
    } else {
      navigate('/login', { replace: true });
    }
  }, [location.search, navigate]);

  return (
    <div className="loading-screen">
      <div className="loader"></div>
      <p>Completing sign-in…</p>
    </div>
  );
}
