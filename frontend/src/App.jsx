import { Routes, Route } from 'react-router-dom';
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
import './index.css';

export default function App() {
  return (
    <>
      <Navbar />
      <BottomNav />
      <main>
        <Routes>
          <Route path='/' element={<HomePage />} />
          <Route path='/search' element={<SearchResultsPage />} />
          <Route path='/analyze/:id' element={<AnalyzePage />} />
          <Route path='/analyze/:id/details' element={<DetailsPage />} />
          <Route path='/watchlist' element={<WatchlistPage />} />
          <Route path='/alerts' element={<AlertsPage />} />
          <Route path='/preferences' element={<PreferencesPage />} />
          <Route path='/how-it-works' element={<HowItWorksPage />} />
          <Route path='*' element={<NotFoundPage />} />
        </Routes>
      </main>
    </>
  );
}

