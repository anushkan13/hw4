import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import Bulldog from './Bulldog'
import {
  fetchChatHistory,
  formatPrice,
  imageSrc,
  pageContextFor,
  sendChatMessage,
  type ChatProductCard,
  type ChatTurn,
} from '../lib/api'
import { useAuth } from '../lib/auth'

interface Message {
  role: 'user' | 'assistant'
  content: string
  products?: ChatProductCard[]
  failed?: boolean
  /** Replayed from the database rather than sent in this session. */
  restored?: boolean
}

const GREETING: Message = {
  role: 'assistant',
  content:
    "Hi, I'm Handsome Dan — the Campus Customs bulldog. Ask me about hoodies, tees, " +
    'sizes, or anything Yale, and I\'ll dig up the right piece.',
}

// Shown only on an empty conversation: a shopper who has never used the widget has
// no idea what it can do, and a blank box invites nothing. Each chip is a real
// question that exercises a different tool.
const STARTER_CHIPS = [
  'What hoodies do you have?',
  'Show me items under $50',
  'What t-shirts are in stock in the XL size?',
]

// Mounted once in App, outside <Routes>, so useParams is not available here --
// read the product slug off the pathname instead. The slug is a good enough label
// without a second fetch.
function routeContext(pathname: string) {
  const match = /^\/products\/([^/]+)/.exec(pathname)
  if (!match) return undefined
  return decodeURIComponent(match[1])
    .split('-')
    .map((w) => (w.length > 2 ? w[0].toUpperCase() + w.slice(1) : w.toUpperCase()))
    .join(' ')
}

export default function ChatPanel() {
  const { pathname } = useLocation()
  const { user } = useAuth()
  const context = routeContext(pathname)
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, open, sending, loadingHistory])

  // Replay the signed-in shopper's saved conversation, cards included. Runs on sign
  // in and on sign out: signing out clears the panel so the next person at this
  // browser does not see someone else's transcript.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING])
      return
    }
    let active = true
    setLoadingHistory(true)
    fetchChatHistory()
      .then((items) => {
        if (!active) return
        setMessages([
          GREETING,
          ...items.map((m) => ({
            role: m.role,
            content: m.content,
            products: m.products,
            restored: true,
          })),
        ])
      })
      .catch(() => {
        /* no saved history, or the backend is down: start fresh */
      })
      .finally(() => active && setLoadingHistory(false))
    return () => {
      active = false
    }
  }, [user])

  async function send(text: string) {
    if (!text || sending) return

    // The greeting is local, so it is not part of the transcript the agent sees.
    const history: ChatTurn[] = messages
      .filter((m) => m !== GREETING && !m.failed)
      .map((m) => ({ role: m.role, content: m.content }))

    setDraft('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setSending(true)
    try {
      // Page context travels with every message so "do you have this in pink?" on a
      // product page resolves to that product.
      const data = await sendChatMessage(text, history, pageContextFor(pathname))
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.reply, products: data.products },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: (err as Error).message, failed: true },
      ])
    } finally {
      setSending(false)
    }
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    void send(draft.trim())
  }

  // Only while the conversation is empty; once the shopper is talking they are gone.
  const showStarters = messages.length === 1 && !sending && !loadingHistory

  if (!open) {
    return (
      <button
        className="chat-fab"
        onClick={() => setOpen(true)}
        aria-label="Chat with Handsome Dan, the Campus Customs shopping assistant"
      >
        <Bulldog size={38} accent="var(--gold-bright)" title="" />
      </button>
    )
  }

  return (
    <aside className="chat-panel" aria-label="Chat with Handsome Dan, the Campus Customs assistant">
      <div className="chat-head">
        <div className="chat-head-id">
          <span className="chat-avatar">
            <Bulldog size={30} accent="var(--gold-bright)" title="" />
          </span>
          <div>
            <strong>Handsome Dan</strong>
            <span>Campus Customs shopping assistant</span>
          </div>
        </div>
        <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
          ×
        </button>
      </div>

      {context && <p className="chat-context">Viewing: {context}</p>}
      {loadingHistory && <p className="chat-context">Loading your conversation…</p>}

      <div className="chat-log" ref={logRef} aria-live="polite">
        {messages.map((m, i) => (
          <div className={`chat-row ${m.role === 'user' ? 'me' : 'bot'}`} key={i}>
            {m.role !== 'user' && (
              <span className="chat-bot-avatar" aria-hidden="true">
                <Bulldog size={21} accent="var(--gold-bright)" title="" />
              </span>
            )}
            <div
              className={`bubble ${m.role === 'user' ? 'me' : 'bot'} ${m.failed ? 'failed' : ''}`}
            >
              {m.content}
            </div>

            {/* The contract: whatever the agent puts in ChatReply.products is what
                renders here. The cards show real catalogue data rather than anything
                written in prose, and each is a router <Link> to the shared product
                detail route — so the main page navigates while the panel stays open. */}
            {m.products && m.products.length > 0 && (
              <div className="chat-cards">
                {m.products.map((p) => (
                  <Link
                    to={`/products/${p.product_id}`}
                    className="chat-card"
                    key={p.product_id}
                  >
                    {p.image_url && (
                      <img src={imageSrc(p.image_url)} alt={p.name} />
                    )}
                    <div className="chat-card-body">
                      <span className="chat-card-name">{p.name}</span>
                      <span className="chat-card-price">{formatPrice(p.price)}</span>
                      {/* Stock is only truthful for cards from this session. A
                          replayed card's sizes may be months old, and older stored
                          payloads have no size data at all, so say nothing rather
                          than claim "sold out" about an item that may be in stock. */}
                      {p.sizes_in_stock.length > 0 ? (
                        <span className="chat-card-sizes">
                          {p.sizes_in_stock.join(' · ')}
                        </span>
                      ) : m.restored ? null : (
                        <span className="chat-card-sizes out">Sold out</span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}

        {showStarters && (
          <div className="chat-starters">
            <span className="chat-starters-label">Try asking</span>
            {STARTER_CHIPS.map((q) => (
              <button
                key={q}
                type="button"
                className="chat-starter"
                onClick={() => void send(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {sending && (
          <div className="chat-row bot">
            <span className="chat-bot-avatar" aria-hidden="true">
              <Bulldog size={21} accent="var(--gold-bright)" title="" />
            </span>
            <div className="bubble bot typing" aria-label="Handsome Dan is typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask about sizes, colors, or styles…"
          aria-label="Message the shopping assistant"
          disabled={sending}
        />
        <button className="chat-send" type="submit" disabled={!draft.trim() || sending}>
          Send
        </button>
      </form>
    </aside>
  )
}
