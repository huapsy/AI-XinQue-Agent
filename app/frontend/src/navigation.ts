export type AppRoute = "chat" | "history" | "admin";

export interface ParsedRoute {
  route: AppRoute;
  params: URLSearchParams;
}

export function parseHashRoute(hash: string): ParsedRoute {
  const normalized = hash.replace(/^#/, "") || "chat";
  const [routePart, query = ""] = normalized.split("?");
  const route: AppRoute =
    routePart === "admin" || routePart === "history" ? routePart : "chat";
  return {
    route,
    params: new URLSearchParams(query),
  };
}

export function buildHashRoute(
  route: AppRoute,
  params?: Record<string, string | number | boolean | null | undefined>,
): string {
  const search = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `#${route}?${query}` : `#${route}`;
}
