import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import Results from './components/Results';
import Landing from './components/Landing';
import './styles.css';

function App() {
  const [screen, setScreen] = useState('landing'); // landing, quiz, results
  const [quizData, setQuizData] = useState(null);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);

  // Load all data on mount
  useEffect(() => {
    async function loadData() {
      const [structure, stages, prevalence, prevalenceByStage, cooccurrences, specialists, severity, stats] =
        await Promise.all([
          fetch('/data/quiz_structure.json').then(r => r.json()),
          fetch('/data/life_stages.json').then(r => r.json()),
          fetch('/data/prevalence_overall.json').then(r => r.json()),
          fetch('/data/prevalence_by_stage.json').then(r => r.json()),
          fetch('/data/cooccurrences.json').then(r => r.json()),
          fetch('/data/specialists.json').then(r => r.json()),
          fetch('/data/severity.json').then(r => r.json()),
          fetch('/data/stats.json').then(r => r.json()),
        ]);

      setQuizData({ structure, stages, prevalence, prevalenceByStage, cooccurrences, specialists, severity, stats });
    }
    loadData();
  }, []);

  const handleQuizComplete = (symptoms, stage) => {
    setSelectedSymptoms(symptoms);
    setSelectedStage(stage);
    setScreen('results');
    window.scrollTo(0, 0);
  };

  const handleRestart = () => {
    setSelectedSymptoms([]);
    setSelectedStage(null);
    setScreen('landing');
  };

  if (!quizData) {
    return (
      <div className="loading-screen">
        <div className="loading-pulse" />
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {screen === 'landing' && (
        <Landing onStart={() => setScreen('quiz')} totalResponses={quizData.stats.total_responses} />
      )}
      {screen === 'quiz' && (
        <Quiz
          categories={quizData.structure}
          stages={quizData.stages}
          onComplete={handleQuizComplete}
          onBack={() => setScreen('landing')}
        />
      )}
      {screen === 'results' && (
        <Results
          selectedSymptoms={selectedSymptoms}
          selectedStage={selectedStage}
          data={quizData}
          onRestart={handleRestart}
        />
      )}
    </div>
  );
}

export default App;