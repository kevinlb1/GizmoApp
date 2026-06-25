export async function fetchBootstrap(apiBase) {
  const response = await fetch(`${apiBase}/bootstrap`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Bootstrap request failed with ${response.status}`);
  }

  return response.json();
}


export async function fetchCapabilities(apiBase) {
  const response = await fetch(`${apiBase}/capabilities`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Capabilities request failed with ${response.status}`);
  }

  return response.json();
}


export async function searchRecords(apiBase, query) {
  const params = new URLSearchParams({ q: query });
  const response = await fetch(`${apiBase}/search?${params.toString()}`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Search request failed with ${response.status}`);
  }

  return response.json();
}
