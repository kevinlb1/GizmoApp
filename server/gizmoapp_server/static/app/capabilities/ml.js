export async function runKMeans(apiBase, { points, clusters = 2 }) {
  const response = await fetch(`${apiBase}/ml/kmeans`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ points, clusters }),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.errors?.join("; ") || `KMeans failed with ${response.status}`);
  }
  return payload;
}
