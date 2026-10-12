import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { fetchSearchResults, analyzeProduct } from '../services/api';
import PageContainer from '../components/Layout/PageContainer';
import SearchBar from '../components/Search/SearchBar';
import SearchResults from '../components/Search/SearchResults';

export default function SearchResultsPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (query) {
      setIsSearching(true);
      fetchSearchResults(query)
        .then((res) => {
          if (isMounted) {
            setResults(res || []);
            setIsSearching(false);
          }
        })
        .catch((err) => {
          console.error('Search failed', err);
          if (isMounted) {
            setResults([]);
            setIsSearching(false);
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [query]);

  const handleSearch = async (newQuery) => {
    if (!newQuery) return;
    const trimmed = newQuery.trim();
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      try {
        const analysis = await analyzeProduct(trimmed);
        const product = await analysis.execute(() => {});
        if (product && product.id) {
          navigate(`/analyze/${encodeURIComponent(product.id)}`);
          return;
        }
      } catch (err) {
        console.error('URL analysis failed', err);
      }
    }
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <PageContainer>
      <div className="max-w-md w-full fade-in" style={{ paddingTop: '16px' }}>
        <button className="btn-text" style={{ marginBottom: '16px' }} onClick={() => navigate('/')}>
          ← Back to Search
        </button>
        <SearchBar onSubmit={handleSearch} />
        
        <div style={{ marginTop: '32px' }}>
          {isSearching ? (
            <p className="text-secondary" style={{ textAlign: 'center' }}>Searching for "{query}"...</p>
          ) : (
            <SearchResults results={results} onSelect={(product) => navigate('/analyze/' + product.id)} />
          )}
        </div>
      </div>
    </PageContainer>
  );
}
