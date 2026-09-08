const API_BASE =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";

async function parseResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        let message = "Request failed";

        if (typeof data.detail === "string") {
            message = data.detail;
        } else if (Array.isArray(data.detail)) {
            message = data.detail
                .map((item) => item.msg)
                .join(", ");
        }

        throw new Error(message);
    }

    return data;
}

export async function checkHealth() {
    const response = await fetch(`${API_BASE}/health`);
    return parseResponse(response);
}

export async function startFromResume({
    sessionId,
    topic,
    difficulty,
    totalQuestions,
    jobRole,
    companyContext,
    resume,
}) {
    const formData = new FormData();

    formData.append("session_id", sessionId);
    formData.append("topic", topic);
    formData.append("difficulty", difficulty);
    formData.append("total_questions", String(totalQuestions));
    formData.append("resume", resume);

    if (jobRole.trim()) {
        formData.append("job_role", jobRole);
    }

    if (companyContext.trim()) {
        formData.append("company_context", companyContext);
    }

    const response = await fetch(
        `${API_BASE}/interview/start-from-resume`,
        {
            method: "POST",
            body: formData,
        }
    );

    return parseResponse(response);
}

export async function submitAnswer(
    sessionId,
    candidateAnswer
) {
    const response = await fetch(
        `${API_BASE}/interview/answer`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                candidate_answer: candidateAnswer,
            }),
        }
    );

    return parseResponse(response);
}

export async function getAnalytics(sessionId) {
    const response = await fetch(
        `${API_BASE}/interview/${encodeURIComponent(
            sessionId
        )}/analytics`
    );

    return parseResponse(response);
}