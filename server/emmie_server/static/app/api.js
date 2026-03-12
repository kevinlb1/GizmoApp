export async function fetchBootstrap(apiBase) {
  const response = await fetch(`${apiBase}/bootstrap`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Bootstrap request failed with ${response.status}`);
  }

  return response.json();
}

