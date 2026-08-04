const BASE = import.meta.env.BASE_URL

export const assetUrl = (p) => `${BASE}${p.replace(/^\//, '')}`
