import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function Results({ selectedSymptoms, selectedStage, data, onRestart }) {
  const { prevalence, prevalenceByStage, cooccurrences, specialists, severity, stats } = data;

  // ── Compute prevalence for selected symptoms ──
  const stageKey = String(selectedStage.stage_id);
  const stagePrevalence = prevalenceByStage[stageKey] || {};

  const prevalenceResults = selectedSymptoms.map(id => {
    const overall = prevalence[String(id)] || {};
    const byStage = stagePrevalence[String(id)] || {};
    return {
      symptom_id: id,
      symptom_name: overall.symptom_name || `Symptom ${id}`,
      category_icon: overall.category_icon || '',
      percentage: byStage.percentage || overall.percentage || 0,
      overall_percentage: overall.percentage || 0,
    };
  }).sort((a, b) => b.percentage - a.percentage);

  // ── Find co-occurring symptoms user DIDN'T select ──
  const selectedSet = new Set(selectedSymptoms);
  const coocScores = {};

  cooccurrences.forEach(row => {
    if (selectedSet.has(row.symptom_id_a) && !selectedSet.has(row.symptom_id_b)) {
      if (!coocScores[row.symptom_id_b]) coocScores[row.symptom_id_b] = { total: 0, count: 0 };
      coocScores[row.symptom_id_b].total += row.co_occurrence_pct;
      coocScores[row.symptom_id_b].count += 1;
    }
    if (selectedSet.has(row.symptom_id_b) && !selectedSet.has(row.symptom_id_a)) {
      if (!coocScores[row.symptom_id_a]) coocScores[row.symptom_id_a] = { total: 0, count: 0 };
      coocScores[row.symptom_id_a].total += row.co_occurrence_pct;
      coocScores[row.symptom_id_a].count += 1;
    }
  });

  const cooccurringSymptoms = Object.entries(coocScores)
    .filter(([_, v]) => v.count >= 2)
    .map(([id, v]) => ({
      symptom_name: prevalence[id]?.symptom_name || `Symptom ${id}`,
      icon: prevalence[id]?.category_icon || '',
      avg_pct: Math.round(v.total / v.count),
    }))
    .sort((a, b) => b.avg_pct - a.avg_pct)
    .slice(0, 5);

  // ── Match specialists ──
  const specScores = specialists.map(spec => {
    const matched = spec.symptom_ids.filter(id => selectedSet.has(id));
    const matchedNames = matched.map(id => prevalence[String(id)]?.symptom_name || '');
    return { ...spec, matched, matchedNames, score: matched.length };
  })
    .filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  // ── Chart colors ──
  const colors = ['#D4A0A0', '#C4B5A0', '#A0BDB8', '#B5A0C4', '#A0B5D4', '#D4C4A0'];

  return (
    <div className="results">

      {/* ── Header ── */}
      <div className="results-header">
        <h1>You're not alone.</h1>
        <p className="results-subtitle">
          Based on {stats.total_responses.toLocaleString()}+ anonymous responses from women like you.
        </p>
        <div className="results-badge">
          {selectedStage.stage_name} · {selectedSymptoms.length} symptoms
        </div>
      </div>

      {/* ── Section 1: Prevalence ── */}
      <section className="results-section">
        <h2 className="section-title">How common are your symptoms?</h2>
        <p className="section-desc">
          Among women in your age group ({selectedStage.stage_name}):
        </p>

        <div className="prevalence-list">
          {prevalenceResults.map((row, i) => (
            <div key={row.symptom_id} className="prevalence-item" style={{ animationDelay: `${i * 0.1}s` }}>
              <div className="prevalence-info">
                <span className="prevalence-icon">{row.category_icon}</span>
                <span className="prevalence-name">{row.symptom_name}</span>
              </div>
              <div className="prevalence-bar-container">
                <div
                  className="prevalence-bar"
                  style={{ width: `${Math.min(row.percentage, 100)}%`, animationDelay: `${i * 0.1 + 0.3}s` }}
                />
              </div>
              <span className="prevalence-pct">{row.percentage}%</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Section 2: Co-occurrences ── */}
      {cooccurringSymptoms.length > 0 && (
        <section className="results-section">
          <h2 className="section-title">Women with your symptoms also report...</h2>
          <div className="cooc-grid">
            {cooccurringSymptoms.map((row, i) => (
              <div key={i} className="cooc-card" style={{ animationDelay: `${i * 0.1}s` }}>
                <span className="cooc-icon">{row.icon}</span>
                <span className="cooc-name">{row.symptom_name}</span>
                <span className="cooc-pct">{row.avg_pct}% overlap</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── Section 3: Severity Chart ── */}
      <section className="results-section">
        <h2 className="section-title">Severity breakdown</h2>
        <p className="section-desc">How others rate the same symptoms:</p>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={prevalenceResults.map(row => {
              const sev = severity[String(row.symptom_id)] || {};
              return {
                name: row.symptom_name.length > 15 ? row.symptom_name.substring(0, 15) + '…' : row.symptom_name,
                Mild: sev.pct_mild || 0,
                Moderate: sev.pct_moderate || 0,
                Severe: sev.pct_severe || 0,
              };
            })}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="Mild" fill="#A0BDB8" stackId="a" />
              <Bar dataKey="Moderate" fill="#D4C4A0" stackId="a" />
              <Bar dataKey="Severe" fill="#D4A0A0" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* ── Section 4: Specialists ── */}
      <section className="results-section">
        <h2 className="section-title">Your next step</h2>
        <p className="section-desc">Based on your symptoms, consider reaching out to:</p>
        <div className="specialist-list">
          {specScores.map((spec, i) => (
            <div key={spec.specialist_id} className="specialist-card" style={{ animationDelay: `${i * 0.15}s` }}>
              <div className="specialist-header">
                <span className="specialist-icon">{spec.icon}</span>
                <div>
                  <h3 className="specialist-type">{spec.specialist_type}</h3>
                  <span className="specialist-match">{spec.score} symptom match{spec.score !== 1 ? 'es' : ''}</span>
                </div>
              </div>
              <p className="specialist-desc">{spec.description}</p>
              <div className="specialist-symptoms">
                <strong>Your matching symptoms:</strong>{' '}
                {spec.matchedNames.join(', ')}
              </div>
              <div className="specialist-expect">
                <strong>What to expect:</strong> {spec.what_to_expect}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Disclaimer + Restart ── */}
      <section className="results-footer">
        <p className="disclaimer">
          ⚠️ AmIOkay is not a diagnostic tool. This information is educational and based on
          anonymized, simulated survey data. Always consult a qualified healthcare
          professional for medical advice.
        </p>
        <button className="cta-button secondary" onClick={onRestart}>
          ← Take the Quiz Again
        </button>
      </section>
    </div>
  );
}

export default Results;