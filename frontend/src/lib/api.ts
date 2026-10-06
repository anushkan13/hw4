// Single place that knows how to reach the FastAPI backend.
// In development Vite proxies /api and /images to http://127.0.0.1:8000 (see
// vite.config.ts), so relative URLs work without any CORS surprises. Set
// VITE_API_BASE_URL to point at a deployed backend instead.
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface Product {
  product_id: string
  name: string
  garment_type: string | null
  category: string
  description: string | null
  short_description: string
  colors: string[]
  search_tags: string[]
  image_url: string | null
  price: number | null
}

export interface SizeStock {
  size: string
  quantity: number | null
  in_stock: boolean
}

export interface ProductDetail extends Product {
  sizes: SizeStock[]
  total_stock: number
  in_stock: boolean
}

export interface ProductList {
  count: number
  categories: string[]
  products: Product[]
}

async function getJSON<T>(path: string): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`)
  } catch {
    throw new Error(
      'Could not reach the Campus Customs backend. Start it with: ' +
        'uvicorn backend.main:app --reload --port 8000',
    )
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body?.detail) detail = body.detail
    } catch {
      /* non-JSON error body; keep the status message */
    }
    throw new Error(detail)
  }
  return (await res.json()) as T
}

export const fetchProducts = () => getJSON<ProductList>('/api/products')
export const fetchProduct = (id: string) =>
  getJSON<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

// catalogue.image_url comes back as /images/<file>; prefix it for the dev proxy.
export const imageSrc = (url: string | null) => (url ? `${API_BASE}${url}` : '')

export const formatPrice = (price: number | null) =>
  price == null ? '—' : `$${price.toFixed(2)}`

// --- chat --------------------------------------------------------------------
export interface ChatProductCard {
  product_id: string
  name: string
  price: number | null
  garment_type: string | null
  category: string | null
  short_description: string
  colors: string[]
  image_url: string | null
  sizes_in_stock: string[]
}

export interface ChatReply {
  reply: string
  products: ChatProductCard[]
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

/** Where the shopper is while they type, so "this" resolves to the item on screen. */
export interface PageContext {
  path: string
  product_id: string
}

export interface ChatHistoryItem extends ChatTurn {
  id: number
  products: ChatProductCard[]
  created_at: string | null
}

/** Derive the page context from a route. Only product pages carry a product_id. */
export function pageContextFor(pathname: string): PageContext {
  const match = /^\/products\/([^/]+)/.exec(pathname)
  return { path: pathname, product_id: match ? decodeURIComponent(match[1]) : '' }
}

const TOKEN_KEY = 'campus-customs-token'

/** Bearer header when signed in. The server scopes history by this token, not by
 *  anything else the client sends, so a shopper can only ever read their own. */
function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/** Saved conversation for the signed-in shopper. Guests get an empty list. */
export async function fetchChatHistory(): Promise<ChatHistoryItem[]> {
  const headers = authHeaders()
  if (!headers.Authorization) return []
  const res = await fetch(`${API_BASE}/api/chat/history`, { headers })
  if (!res.ok) return [] // expired token or backend down: just start fresh
  const data = await res.json().catch(() => null)
  return (data?.messages ?? []) as ChatHistoryItem[]
}

/** One turn of the shop assistant. The widget sends its own transcript as history. */
export async function sendChatMessage(
  message: string,
  history: ChatTurn[],
  page: PageContext,
): Promise<ChatReply> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ message, history, page }),
    })
  } catch {
    throw new Error(
      "I can't reach the Campus Customs assistant right now. Make sure the backend " +
        'is running on port 8000.',
    )
  }
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    throw new Error(
      typeof data?.detail === 'string'
        ? data.detail
        : 'The shopping assistant is unavailable right now.',
    )
  }
  return data as ChatReply
}
