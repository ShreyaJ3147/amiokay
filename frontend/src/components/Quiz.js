import React, { useState } from 'react';

function Quiz({ categories, stages, onComplete, onBack }) {
  const [step, setStep] = useState('stage'); // stage, symptoms, review
  const [selectedStage, setSelectedStage] = useState(null);
  const [selectedSymptoms, setSelectedSymptoms] = useState(new Set());
  const [currentCategory, setCurrentCategory] = useState(0);

  const toggleSymptom = (id) => {
    setSelectedSymptoms(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // ── Stage Selection ──
  if (step === 'stage') {
    return (
      <div className="quiz">
        <button className="back-button" onClick={onBack}>← Back</button>
        <div className="quiz-header">
          <span className="quiz-step">Step 1 of 2</span>
          <h2>What's your life stage?</h2>
          <p>This helps us show you the most relevant comparisons.</p>
        </div>
        <div className="stage-grid">
          {stages.map(stage => (
            <button
              key={stage.stage_id}
              className={`stage-card ${selectedStage?.stage_id === stage.stage_id ? 'selected' : ''}`}
              onClick={() => setSelectedStage(stage)}
            >
              <span className="stage-name">{stage.stage_name}</span>
            </button>
          ))}
        </div>
        {selectedStage && (
          <button className="cta-button" onClick={() => setStep('symptoms')}>
            Next → Select Symptoms
          </button>
        )}
      </div>
    );
  }

  // ── Symptom Selection ──
  if (step === 'symptoms') {
    const category = categories[currentCategory];
    const progress = ((currentCategory + 1) / categories.length) * 100;

    return (
      <div className="quiz">
        <button className="back-button" onClick={() => {
          if (currentCategory > 0) setCurrentCategory(currentCategory - 1);
          else setStep('stage');
        }}>← Back</button>

        <div className="quiz-header">
          <span className="quiz-step">Step 2 of 2</span>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <h2>{category.icon} {category.category_name}</h2>
          <p>Select any symptoms you experience. Skip if none apply.</p>
        </div>

        <div className="symptom-grid">
          {category.symptoms.map(symptom => (
            <button
              key={symptom.symptom_id}
              className={`symptom-card ${selectedSymptoms.has(symptom.symptom_id) ? 'selected' : ''}`}
              onClick={() => toggleSymptom(symptom.symptom_id)}
            >
              <span className="symptom-name">{symptom.symptom_name}</span>
              <span className="symptom-desc">{symptom.description}</span>
            </button>
          ))}
        </div>

        <div className="quiz-nav">
          {currentCategory < categories.length - 1 ? (
            <button className="cta-button" onClick={() => setCurrentCategory(currentCategory + 1)}>
              Next Category →
            </button>
          ) : (
            <button
              className="cta-button"
              disabled={selectedSymptoms.size === 0}
              onClick={() => onComplete(Array.from(selectedSymptoms), selectedStage)}
            >
              See My Results ({selectedSymptoms.size} symptoms selected)
            </button>
          )}
          <p className="symptom-count">
            {selectedSymptoms.size} symptom{selectedSymptoms.size !== 1 ? 's' : ''} selected so far
          </p>
        </div>
      </div>
    );
  }
}

export default Quiz;