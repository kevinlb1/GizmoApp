export async function optimizeRoute(apiBase, points) {
  const response = await fetch(`${apiBase}/optimize/route`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ points }),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.errors?.join("; ") || `Optimization failed with ${response.status}`);
  }
  return payload;
}
