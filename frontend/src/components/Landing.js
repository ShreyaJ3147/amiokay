import React from 'react';

function Landing({ onStart, totalResponses }) {
  return (
    <div className="landing">
      <div className="landing-content">
        <div className="landing-badge">100% Anonymous</div>
        <h1 className="landing-title">
          Am I <span className="highlight">Okay</span>?
        </h1>
        <p className="landing-subtitle">
          Your body is trying to tell you something. Take a 2-minute anonymous quiz
          and discover that what you're feeling is more common than you think.
        </p>
        <div className="landing-stats">
          <div className="stat-bubble">
            <span className="stat-number">{totalResponses.toLocaleString()}+</span>
            <span className="stat-label">women have shared</span>
          </div>
          <div className="stat-bubble">
            <span className="stat-number">33</span>
            <span className="stat-label">symptoms tracked</span>
          </div>
          <div className="stat-bubble">
            <span className="stat-number">7</span>
            <span className="stat-label">specialist types</span>
          </div>
        </div>
        <button className="cta-button" onClick={onStart}>
          Take the Quiz
          <span className="cta-arrow">→</span>
        </button>
        <p className="landing-note">
          No sign-up. No data stored. Just answers.
        </p>
      </div>
      <div className="landing-decoration">
        <div className="circle circle-1" />
        <div className="circle circle-2" />
        <div className="circle circle-3" />
      </div>
    </div>
  );
}

export default Landing;