import React, { createContext, useState, useEffect } from 'react';

export const DegreeWorksContext = createContext();

export function DegreeWorksProvider({ children }) {
  const [hasTranscript, setHasTranscript] = useState(false);
  const [summary, setSummary] = useState(null);
  const [gpa, setGpa] = useState(null);
  const [completedCredits, setCompletedCredits] = useState(0);
  const [inProgressCredits, setInProgressCredits] = useState(0);
  const [remainingCredits, setRemainingCredits] = useState(0);
  const [classification, setClassification] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const refresh = async () => {
    const token = localStorage.getItem('token');
    if (!token || token === 'guest') {
      setHasTranscript(false);
      return;
    }

    setRefreshing(true);
    try {
      const response = await fetch('http://localhost:8000/api/degree-works/summary', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.has_degree_works) {
          setHasTranscript(true);
          setSummary(data.summary);
          setGpa(data.summary?.gpa);
          setCompletedCredits(data.summary?.completed_credits || 0);
          setInProgressCredits(data.summary?.in_progress_credits || 0);
          setRemainingCredits(data.summary?.remaining_credits || 0);
          setClassification(data.summary?.classification || '');
          setLastUpdated(data.last_updated);
        } else {
          setHasTranscript(false);
        }
      } else {
        setHasTranscript(false);
      }
    } catch (error) {
      console.error('Error fetching Degree Works summary:', error);
      setHasTranscript(false);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <DegreeWorksContext.Provider value={{
      hasTranscript,
      summary,
      gpa,
      completedCredits,
      inProgressCredits,
      remainingCredits,
      classification,
      lastUpdated,
      refreshing,
      refresh
    }}>
      {children}
    </DegreeWorksContext.Provider>
  );
}
