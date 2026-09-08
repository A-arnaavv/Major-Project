import { useEffect, useState } from "react";

import {
  checkHealth,
  getAnalytics,
  startFromResume,
  submitAnswer,
} from "./api";

import "./App.css";

export default function App() {
  const [showProfile, setShowProfile] =
    useState(false);

  const [health, setHealth] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [sessionId, setSessionId] =
    useState("");

  const [topic, setTopic] =
    useState("Machine Learning");

  const [difficulty, setDifficulty] =
    useState("medium");

  const [
    totalQuestions,
    setTotalQuestions,
  ] = useState(3);

  const [jobRole, setJobRole] =
    useState("");

  const [
    companyContext,
    setCompanyContext,
  ] = useState("");

  const [resume, setResume] =
    useState(null);

  const [
    candidateProfile,
    setCandidateProfile,
  ] = useState(null);

  const [question, setQuestion] =
    useState(null);

  const [answer, setAnswer] =
    useState("");

  const [
    evaluation,
    setEvaluation,
  ] = useState(null);

  const [
    finalReport,
    setFinalReport,
  ] = useState(null);

  const [analytics, setAnalytics] =
    useState(null);

  const [
    answeredCount,
    setAnsweredCount,
  ] = useState(0);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  async function handleStart(event) {
    event.preventDefault();

    if (!resume) {
      setError(
        "Please select a PDF resume."
      );
      return;
    }

    const id =
      sessionId.trim() ||
      `demo-${Date.now()}`;

    setSessionId(id);

    setLoading(true);
    setError("");

    setCandidateProfile(null);
    setQuestion(null);
    setEvaluation(null);
    setFinalReport(null);
    setAnalytics(null);
    setAnsweredCount(0);
    setShowProfile(false);

    try {
      const data =
        await startFromResume({
          sessionId: id,
          topic,
          difficulty,
          totalQuestions,
          jobRole,
          companyContext,
          resume,
        });

      setCandidateProfile(
        data.candidate_profile
      );

      setQuestion({
        question: data.question,
        difficulty: data.difficulty,
        topic: data.topic,
        subtopic: data.subtopic,
      });
    } catch (err) {
      setError(
        err.message ||
        "Unable to start interview."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleAnswer(event) {
    event.preventDefault();

    if (!answer.trim()) {
      setError(
        "Please enter an answer."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data =
        await submitAnswer(
          sessionId,
          answer.trim()
        );

      setEvaluation(
        data.evaluation
      );

      setAnsweredCount(
        (count) => count + 1
      );

      setAnswer("");

      if (
        data.status === "completed"
      ) {
        setFinalReport(
          data.final_report
        );

        setQuestion(null);

        try {
          const analyticsData =
            await getAnalytics(
              sessionId
            );

          setAnalytics(
            analyticsData
          );
        } catch (analyticsError) {
          console.error(
            "Analytics fetch failed:",
            analyticsError
          );
        }

        return;
      }

      setQuestion(
        data.next_question
      );
    } catch (err) {
      setError(
        err.message ||
        "Unable to submit answer."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setSessionId("");
    setTopic("Machine Learning");
    setDifficulty("medium");
    setTotalQuestions(3);
    setJobRole("");
    setCompanyContext("");
    setResume(null);

    setCandidateProfile(null);
    setQuestion(null);
    setAnswer("");
    setEvaluation(null);
    setFinalReport(null);
    setAnalytics(null);

    setAnsweredCount(0);
    setShowProfile(false);
    setError("");
  }

  const currentQuestionNumber =
    Math.min(
      answeredCount + 1,
      totalQuestions
    );

  const progress =
    totalQuestions > 0
      ? Math.min(
        (answeredCount /
          totalQuestions) *
        100,
        100
      )
      : 0;

  const interviewStarted =
    Boolean(
      candidateProfile ||
      question ||
      finalReport
    );

  return (
    <div className="app">
      <header>
        <div>
          <h1>InterviewGPT</h1>
        </div>

        <p>
          {health
            ? `API connected · ${health.llm_mode} mode`
            : "API offline"}
        </p>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {!interviewStarted && (
        <form onSubmit={handleStart}>
          <p className="section-label">
            AI Interview Setup
          </p>

          <h2>
            Start AI Interview
          </h2>

          <label>
            Resume PDF

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(event) =>
                setResume(
                  event.target
                    .files?.[0] ||
                  null
                )
              }
            />
          </label>

          <label>
            Session ID

            <input
              value={sessionId}
              onChange={(event) =>
                setSessionId(
                  event.target.value
                )
              }
              placeholder="Optional — generated automatically"
            />
          </label>

          <label>
            Topic

            <input
              value={topic}
              onChange={(event) =>
                setTopic(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            Job Role

            <input
              value={jobRole}
              onChange={(event) =>
                setJobRole(
                  event.target.value
                )
              }
              placeholder="ML Engineer"
            />
          </label>

          <label>
            Company Context

            <input
              value={
                companyContext
              }
              onChange={(event) =>
                setCompanyContext(
                  event.target.value
                )
              }
              placeholder="FinTech startup"
            />
          </label>

          <label>
            Difficulty

            <select
              value={difficulty}
              onChange={(event) =>
                setDifficulty(
                  event.target.value
                )
              }
            >
              <option value="easy">
                Easy
              </option>

              <option value="medium">
                Medium
              </option>

              <option value="hard">
                Hard
              </option>
            </select>
          </label>

          <label>
            Total Questions

            <input
              type="number"
              min="1"
              max="20"
              value={
                totalQuestions
              }
              onChange={(event) =>
                setTotalQuestions(
                  Number(
                    event.target.value
                  )
                )
              }
            />
          </label>

          <button
            disabled={loading}
          >
            {loading
              ? "Processing resume..."
              : "Start Interview"}
          </button>
        </form>
      )}

      {candidateProfile && (
        <section>
          <div className="profile-toggle-header">
            <div>
              <p className="section-label">
                Resume Intelligence
              </p>

              <h2>
                Candidate Profile
              </h2>

              {!showProfile && (
                <p className="profile-summary">
                  Resume analysis
                  completed for{" "}
                  <strong>
                    {candidateProfile.name ||
                      "candidate"}
                  </strong>
                  .
                </p>
              )}
            </div>

            <button
              type="button"
              className="profile-toggle"
              onClick={() =>
                setShowProfile(
                  (value) =>
                    !value
                )
              }
            >
              {showProfile
                ? "Hide Profile"
                : "View Profile"}
            </button>
          </div>

          {showProfile && (
            <>
              <div className="profile-header">
                <div>
                  <h2>
                    {candidateProfile.name ||
                      "Candidate Profile"}
                  </h2>

                  <p className="profile-summary">
                    {
                      candidateProfile.summary
                    }
                  </p>
                </div>
              </div>

              <div className="profile-section">
                <h3>
                  Technical Skills
                </h3>

                <div className="tag-list">
                  {candidateProfile.technical_skills?.map(
                    (skill) => (
                      <span
                        className="tag"
                        key={skill}
                      >
                        {skill}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div className="profile-section">
                <h3>
                  Programming Languages
                </h3>

                <div className="tag-list">
                  {candidateProfile.programming_languages?.map(
                    (language) => (
                      <span
                        className="tag"
                        key={
                          language
                        }
                      >
                        {language}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div className="profile-section">
                <h3>
                  Libraries & Tools
                </h3>

                <div className="tag-list">
                  {candidateProfile.libraries_tools?.map(
                    (tool) => (
                      <span
                        className="tag"
                        key={tool}
                      >
                        {tool}
                      </span>
                    )
                  )}
                </div>
              </div>

              {candidateProfile.databases
                ?.length > 0 && (
                  <div className="profile-section">
                    <h3>
                      Databases
                    </h3>

                    <div className="tag-list">
                      {candidateProfile.databases.map(
                        (
                          database
                        ) => (
                          <span
                            className="tag"
                            key={
                              database
                            }
                          >
                            {
                              database
                            }
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}

              <div className="profile-grid">
                <div>
                  <h3>
                    Strengths
                  </h3>

                  <ul className="profile-list">
                    {candidateProfile.strengths?.map(
                      (item) => (
                        <li
                          key={
                            item
                          }
                        >
                          {
                            item
                          }
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div>
                  <h3>
                    Improvement Areas
                  </h3>

                  <ul className="profile-list">
                    {candidateProfile.improvement_areas?.map(
                      (item) => (
                        <li
                          key={
                            item
                          }
                        >
                          {
                            item
                          }
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </div>

              {candidateProfile.experience
                ?.length >
                0 && (
                  <div className="profile-section">
                    <h3>
                      Experience
                    </h3>

                    <div className="card-list">
                      {candidateProfile.experience.map(
                        (
                          item,
                          index
                        ) => (
                          <div
                            className="info-card"
                            key={
                              index
                            }
                          >
                            <div className="info-card-header">
                              <div>
                                <strong>
                                  {
                                    item.title
                                  }
                                </strong>

                                <span>
                                  {
                                    item.company
                                  }
                                </span>
                              </div>

                              <span>
                                {
                                  item.period
                                }
                              </span>
                            </div>

                            {item.responsibilities
                              ?.length >
                              0 && (
                                <ul className="profile-list">
                                  {item.responsibilities.map(
                                    (
                                      responsibility
                                    ) => (
                                      <li
                                        key={
                                          responsibility
                                        }
                                      >
                                        {
                                          responsibility
                                        }
                                      </li>
                                    )
                                  )}
                                </ul>
                              )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

              {candidateProfile.projects
                ?.length >
                0 && (
                  <div className="profile-section">
                    <h3>
                      Projects
                    </h3>

                    <div className="card-list">
                      {candidateProfile.projects.map(
                        (
                          project,
                          index
                        ) => (
                          <div
                            className="info-card"
                            key={
                              index
                            }
                          >
                            <strong>
                              {
                                project.name
                              }
                            </strong>

                            <p>
                              {
                                project.description
                              }
                            </p>

                            <div className="tag-list">
                              {project.tech_stack?.map(
                                (
                                  tech
                                ) => (
                                  <span
                                    className="tag"
                                    key={
                                      tech
                                    }
                                  >
                                    {
                                      tech
                                    }
                                  </span>
                                )
                              )}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

              {candidateProfile.education
                ?.length >
                0 && (
                  <div className="profile-section">
                    <h3>
                      Education
                    </h3>

                    <div className="card-list">
                      {candidateProfile.education.map(
                        (
                          item,
                          index
                        ) => (
                          <div
                            className="info-card"
                            key={
                              index
                            }
                          >
                            <div className="info-card-header">
                              <div>
                                <strong>
                                  {
                                    item.degree
                                  }
                                </strong>

                                <span>
                                  {
                                    item.institution
                                  }
                                </span>
                              </div>

                              <span>
                                {
                                  item.period
                                }
                              </span>
                            </div>

                            {item.score && (
                              <p className="muted-text">
                                {
                                  item.score
                                }
                              </p>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
            </>
          )}
        </section>
      )}

      {question && (
        <section className="interview-section">
          <div className="interview-progress-header">
            <div>
              <p className="section-label">
                Adaptive Interview
              </p>

              <h2>
                Interview Question
              </h2>
            </div>

            <div className="question-counter">
              Question{" "}
              {currentQuestionNumber}{" "}
              of {totalQuestions}
            </div>
          </div>

          <div className="progress-track">
            <div
              className="progress-fill"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>

          <div className="question-meta-row">
            <span>
              <strong>
                Topic
              </strong>
              {question.topic}
            </span>

            <span>
              <strong>
                Subtopic
              </strong>
              {question.subtopic}
            </span>

            <span>
              <strong>
                Difficulty
              </strong>

              <span className="difficulty-pill">
                {
                  question.difficulty
                }
              </span>
            </span>
          </div>

          <h3 className="question-text">
            {question.question}
          </h3>

          <form
            className="answer-form"
            onSubmit={
              handleAnswer
            }
          >
            <textarea
              rows="8"
              value={answer}
              onChange={(event) =>
                setAnswer(
                  event.target.value
                )
              }
              placeholder="Type your answer..."
            />

            <button
              disabled={loading}
            >
              {loading
                ? "Evaluating..."
                : "Submit Answer"}
            </button>
          </form>
        </section>
      )}

      {evaluation && (
        <section>
          <div className="evaluation-header">
            <div>
              <p className="section-label">
                AI Evaluation
              </p>

              <h2>
                Answer Feedback
              </h2>
            </div>

            <div className="overall-score">
              {Number(
                evaluation.overall_score ??
                0
              ).toFixed(1)}

              <span>/10</span>
            </div>
          </div>

          <div className="score-grid">
            {[
              [
                "Technical Accuracy",
                evaluation.technical_accuracy,
              ],
              [
                "Relevance",
                evaluation.relevance,
              ],
              [
                "Clarity",
                evaluation.clarity,
              ],
              [
                "Completeness",
                evaluation.completeness,
              ],
            ].map(
              ([label, value]) => (
                <div
                  className="score-card"
                  key={label}
                >
                  <span>
                    {label}
                  </span>

                  <strong>
                    {Number(
                      value ?? 0
                    ).toFixed(1)}
                  </strong>

                  <div className="score-track">
                    <div
                      className="score-fill"
                      style={{
                        width: `${Math.min(
                          Number(
                            value ??
                            0
                          ) * 10,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>

          <div className="feedback-columns">
            <div>
              <h3>Strengths</h3>

              <div className="tag-list">
                {evaluation.strengths?.map(
                  (
                    item,
                    index
                  ) => (
                    <span
                      className="tag"
                      key={
                        index
                      }
                    >
                      {item}
                    </span>
                  )
                )}
              </div>
            </div>

            <div>
              <h3>
                Weaknesses
              </h3>

              <div className="tag-list">
                {evaluation.weaknesses?.map(
                  (
                    item,
                    index
                  ) => (
                    <span
                      className="tag"
                      key={
                        index
                      }
                    >
                      {item}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>

          <div className="feedback-box">
            <h3>Feedback</h3>

            <p>
              {
                evaluation.feedback
              }
            </p>
          </div>

          <div className="improved-box">
            <h3>
              Improved Answer
            </h3>

            <p>
              {
                evaluation.improved_answer
              }
            </p>
          </div>

          {!finalReport && (
            <div className="difficulty-row">
              <span>
                Next difficulty
              </span>

              <strong>
                {
                  evaluation.next_difficulty
                }
              </strong>
            </div>
          )}
        </section>
      )}

      {finalReport && (
        <section>
          <div className="evaluation-header">
            <div>
              <p className="section-label">
                Interview Complete
              </p>

              <h2>
                Performance Report
              </h2>
            </div>

            <div className="completion-badge">
              {answeredCount}/
              {totalQuestions} completed
            </div>
          </div>

          <div className="score-grid">
            {[
              [
                "Average Score",
                finalReport
                  .numerical_report
                  ?.average_score,
              ],
              [
                "Technical Accuracy",
                finalReport
                  .numerical_report
                  ?.average_technical_accuracy,
              ],
              [
                "Relevance",
                finalReport
                  .numerical_report
                  ?.average_relevance,
              ],
              [
                "Clarity",
                finalReport
                  .numerical_report
                  ?.average_clarity,
              ],
              [
                "Completeness",
                finalReport
                  .numerical_report
                  ?.average_completeness,
              ],
            ].map(
              ([label, value]) => (
                <div
                  className="score-card"
                  key={label}
                >
                  <span>
                    {label}
                  </span>

                  <strong>
                    {Number(
                      value ?? 0
                    ).toFixed(1)}
                  </strong>

                  <div className="score-track">
                    <div
                      className="score-fill"
                      style={{
                        width: `${Math.min(
                          Number(
                            value ??
                            0
                          ) * 10,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>

          <div className="report-columns">
            <div className="report-card">
              <h3>
                Overall Performance
              </h3>

              <p className="performance-label">
                {finalReport
                  .numerical_report
                  ?.overall_performance ||
                  finalReport
                    .ai_summary
                    ?.overall_performance ||
                  analytics?.summary
                    ?.overall_performance ||
                  "—"}
              </p>
            </div>

            <div className="report-card">
              <h3>
                Total Questions
              </h3>

              <p className="performance-label">
                {finalReport
                  .numerical_report
                  ?.total_questions ??
                  analytics?.summary
                    ?.total_questions ??
                  totalQuestions}
              </p>
            </div>
          </div>

          <div className="feedback-columns">
            <div>
              <h3>
                Strong Areas
              </h3>

              <div className="tag-list">
                {(
                  finalReport
                    .numerical_report
                    ?.strong_areas ||
                  finalReport
                    .ai_summary
                    ?.strong_areas ||
                  analytics?.summary
                    ?.strong_areas ||
                  []
                ).map(
                  (item) => (
                    <span
                      className="tag"
                      key={item}
                    >
                      {item}
                    </span>
                  )
                )}
              </div>
            </div>

            <div>
              <h3>
                Weak Areas
              </h3>

              <div className="tag-list">
                {(
                  finalReport
                    .numerical_report
                    ?.weak_areas ||
                  finalReport
                    .ai_summary
                    ?.weak_areas ||
                  analytics?.summary
                    ?.weak_areas ||
                  []
                ).map(
                  (item) => (
                    <span
                      className="tag"
                      key={item}
                    >
                      {item}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>

          {finalReport.ai_summary
            ?.summary && (
              <div className="feedback-box">
                <h3>
                  AI Performance Summary
                </h3>

                <p>
                  {
                    finalReport
                      .ai_summary
                      .summary
                  }
                </p>
              </div>
            )}

          {finalReport.learning_plan
            ?.length >
            0 && (
              <div className="learning-plan">
                <h3>
                  Personalized Learning
                  Plan
                </h3>

                <div className="learning-list">
                  {finalReport.learning_plan.map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        className="learning-card"
                        key={`${item.subtopic}-${index}`}
                      >
                        <div className="priority-badge">
                          {item.priority ??
                            index +
                            1}
                        </div>

                        <div>
                          <div className="learning-title-row">
                            <h4>
                              {
                                item.subtopic
                              }
                            </h4>

                            <span className="learning-score">
                              {Number(
                                item.current_score ??
                                0
                              ).toFixed(
                                1
                              )}
                              /10
                            </span>
                          </div>

                          <p className="learning-level">
                            {
                              item.performance_level
                            }
                          </p>

                          <p>
                            {
                              item.recommended_action
                            }
                          </p>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
        </section>
      )}

      {analytics && (
        <section>
          <p className="section-label">
            Analytics Export
          </p>

          <h2>
            Question-Level
            Performance
          </h2>

          <div className="analytics-summary">
            <div>
              <span>
                Session
              </span>

              <strong>
                {
                  analytics.session_id
                }
              </strong>
            </div>

            <div>
              <span>
                Questions
              </span>

              <strong>
                {analytics.summary
                  ?.total_questions ??
                  0}
              </strong>
            </div>

            <div>
              <span>
                Average Score
              </span>

              <strong>
                {Number(
                  analytics.summary
                    ?.average_score ??
                  0
                ).toFixed(1)}
              </strong>
            </div>

            <div>
              <span>
                Performance
              </span>

              <strong>
                {analytics.summary
                  ?.overall_performance ||
                  "—"}
              </strong>
            </div>
          </div>

          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>
                    Subtopic
                  </th>
                  <th>
                    Difficulty
                  </th>
                  <th>
                    Technical
                  </th>
                  <th>
                    Relevance
                  </th>
                  <th>
                    Clarity
                  </th>
                  <th>
                    Completeness
                  </th>
                  <th>
                    Overall
                  </th>
                </tr>
              </thead>

              <tbody>
                {analytics.question_records?.map(
                  (
                    record
                  ) => (
                    <tr
                      key={
                        record.question_number
                      }
                    >
                      <td>
                        {
                          record.question_number
                        }
                      </td>

                      <td>
                        {
                          record.subtopic
                        }
                      </td>

                      <td>
                        <span className="difficulty-pill">
                          {
                            record.difficulty
                          }
                        </span>
                      </td>

                      <td>
                        {
                          record.technical_accuracy
                        }
                      </td>

                      <td>
                        {
                          record.relevance
                        }
                      </td>

                      <td>
                        {
                          record.clarity
                        }
                      </td>

                      <td>
                        {
                          record.completeness
                        }
                      </td>

                      <td>
                        <strong>
                          {
                            record.overall_score
                          }
                        </strong>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          {analytics.summary
            ?.subtopic_performance && (
              <div className="subtopic-section">
                <h3>
                  Subtopic Performance
                </h3>

                <div className="subtopic-list">
                  {Object.entries(
                    analytics.summary
                      .subtopic_performance
                  ).map(
                    ([
                      subtopic,
                      score,
                    ]) => (
                      <div
                        className="subtopic-row"
                        key={
                          subtopic
                        }
                      >
                        <span>
                          {
                            subtopic
                          }
                        </span>

                        <div className="subtopic-score-wrap">
                          <div className="subtopic-track">
                            <div
                              className="subtopic-fill"
                              style={{
                                width: `${Math.min(
                                  Number(
                                    score
                                  ) *
                                  10,
                                  100
                                )}%`,
                              }}
                            />
                          </div>

                          <strong>
                            {Number(
                              score
                            ).toFixed(
                              1
                            )}
                          </strong>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
        </section>
      )}

      {finalReport && (
        <div className="new-interview-actions">
          <button
            type="button"
            className="new-interview-button"
            onClick={
              handleReset
            }
          >
            Start New Interview
          </button>
        </div>
      )}
    </div>
  );
}