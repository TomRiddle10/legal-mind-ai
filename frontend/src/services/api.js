const API_BASE_URL = 'http://127.0.0.1:5000'

export async function askLegalAI(question) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.message || 'Failed to get answer from Legal Mind AI.'
    )
  }

  return data
}