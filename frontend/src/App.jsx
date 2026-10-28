import { Navigate, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import BottomNav from './components/Layout/BottomNav';
import HomePage from './pages/HomePage';
import SearchResultsPage from './pages/SearchResultsPage';
import AnalyzePage from './pages/AnalyzePage';
import DetailsPage from './pages/DetailsPage';
import WatchlistPage from './pages/WatchlistPage';
import AlertsPage from './pages/AlertsPage';
import PreferencesPage from './pages/PreferencesPage';
import HowItWorksPage from './pages/HowItWorksPage';
import NotFoundPage from './pages/NotFoundPage';
import LoginPage from './pages/LoginPage';
import OtpPage from './pages/OtpPage';
import { AuthProvider } from './auth/AuthContext';
import { useAuth } from './auth/context';
import './index.css';

function ProtectedRoute({ children }) {
  const { session } = useAuth();
  const location = useLocation();
  return session ? children : <Navigate to="/login" replace state={{ returnTo: location.pathname }} />;
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <BottomNav />
      <div className="app-content">
        <Routes>
          <Route path='/' element={<HomePage />} />
          <Route path='/search' element={<SearchResultsPage />} />
          <Route path='/login' element={<LoginPage />} />
          <Route path='/login/otp' element={<OtpPage />} />
          <Route path='/analyze/:id' element={<AnalyzePage />} />
          <Route path='/analyze/:id/details' element={<DetailsPage />} />
          <Route path='/watchlist' element={<ProtectedRoute><WatchlistPage /></ProtectedRoute>} />
          <Route path='/alerts' element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
          <Route path='/preferences' element={<ProtectedRoute><PreferencesPage /></ProtectedRoute>} />
          <Route path='/how-it-works' element={<HowItWorksPage />} />
          <Route path='*' element={<NotFoundPage />} />
        </Routes>
      </div>
    </>
  );
}

export default function App() {
  return <AuthProvider><AppRoutes /></AuthProvider>;
}

