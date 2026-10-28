import React, { useState } from 'react';
import { requestLoginOtp, verifyLoginOtp } from '../services/api';
import { AuthContext } from './context';

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const requestOtp = (email) => requestLoginOtp(email);
  const verifyOtp = async (email, code) => {
    const result = await verifyLoginOtp(email, code);
    setSession(result);
    return result;
  };
  const signOut = () => setSession(null);
  return <AuthContext.Provider value={{ session, requestOtp, verifyOtp, signOut }}>{children}</AuthContext.Provider>;
}

