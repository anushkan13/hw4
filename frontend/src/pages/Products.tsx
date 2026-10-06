import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, formatPrice, imageSrc, type Product } from '../lib/api'

// $10 bands, built from the catalogue's own range so the list never shows an empty
// bucket or misses the top end.
const BAND_SIZE = 10

function priceBands(products: Product[]): { label: string; min: number; max: number }[] {
  const prices = products.map((p) => p.price ?? 0).filter((p) => p > 0)
  if (prices.length === 0) return []
  const top = Math.ceil(Math.max(...prices) / BAND_SIZE) * BAND_SIZE
  const bands = []
  for (let min = 0; min < top; min += BAND_SIZE) {
    const max = min + BAND_SIZE
    if (prices.some((p) => p > min && p <= max)) {
      bands.push({ label: `$${min}–${max}`, min, max })
    }
  }
  return bands
}

const SORTS = [
  { value: 'name', label: 'A–Z' },
  { value: 'price-asc', label: 'Price: low to high' },
  { value: 'price-desc', label: 'Price: high to low' },
] as const

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [category, setCategory] = useState('All')
  const [query, setQuery] = useState('')
  const [band, setBand] = useState<string>('All')
  const [sort, setSort] = useState<string>('name')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    fetchProducts()
      .then((data) => {
        if (!active) return
        setProducts(data.products)
        setCategories(data.categories)
      })
      .catch((err: Error) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  const bands = useMemo(() => priceBands(products), [products])

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase()
    const chosen = bands.find((b) => b.label === band)

    const filtered = products.filter((p) => {
      if (category !== 'All' && p.category !== category) return false
      if (chosen) {
        const price = p.price ?? 0
        if (price <= chosen.min || price > chosen.max) return false
      }
      if (!needle) return true
      return (
        p.name.toLowerCase().includes(needle) ||
        (p.description ?? '').toLowerCase().includes(needle) ||
        p.search_tags.some((t) => t.toLowerCase().includes(needle)) ||
        p.colors.some((c) => c.toLowerCase().includes(needle))
      )
    })

    if (sort === 'price-asc') {
      return [...filtered].sort((a, b) => (a.price ?? 0) - (b.price ?? 0))
    }
    if (sort === 'price-desc') {
      return [...filtered].sort((a, b) => (b.price ?? 0) - (a.price ?? 0))
    }
    return filtered
  }, [products, category, query, band, sort, bands])

  return (
    <div className="page">
      <div className="container">
        <div className="page-head">
          <p className="eyebrow">The Collection</p>
          <h1>Products</h1>
          <p className="lede">
            Every piece in the Campus Customs shop, straight from the Yale rack.
          </p>
        </div>

        {error && (
          <div className="state">
            <div className="state-error">
              <strong>Couldn't load the catalogue.</strong>
              <br />
              {error}
            </div>
          </div>
        )}

        {loading && !error && (
          <div className="skeleton-grid">
            {Array.from({ length: 8 }).map((_, i) => (
              <div className="skeleton" key={i}>
                <div className="skeleton-thumb" />
                <div className="skeleton-line" style={{ width: '70%' }} />
                <div className="skeleton-line" style={{ width: '40%' }} />
              </div>
            ))}
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="toolbar">
              <input
                className="search-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search the collection…"
                aria-label="Search products"
              />
              {['All', ...categories].map((c) => (
                <button
                  key={c}
                  className={`chip ${category === c ? 'active' : ''}`}
                  onClick={() => setCategory(c)}
                >
                  {c}
                </button>
              ))}
              <span className="result-count">
                {visible.length} {visible.length === 1 ? 'piece' : 'pieces'}
              </span>
            </div>

            <div className="toolbar toolbar-secondary">
              <span className="toolbar-label">Price</span>
              <button
                className={`chip ${band === 'All' ? 'active' : ''}`}
                onClick={() => setBand('All')}
              >
                Any
              </button>
              {bands.map((b) => (
                <button
                  key={b.label}
                  className={`chip ${band === b.label ? 'active' : ''}`}
                  onClick={() => setBand(b.label)}
                >
                  {b.label}
                </button>
              ))}

              {/* kept in one group so the label and the control never wrap apart */}
              <span className="sort-group">
                <span className="toolbar-label">Sort</span>
                <select
                  className="sort-select"
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                  aria-label="Sort products"
                >
                  {SORTS.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </span>
            </div>

            {visible.length === 0 ? (
              <p className="state">Nothing matches that search just yet.</p>
            ) : (
              <div className="product-grid">
                {visible.map((p) => (
                  <Link
                    to={`/products/${p.product_id}`}
                    className="product-card"
                    key={p.product_id}
                  >
                    <div className="product-thumb">
                      {p.image_url ? (
                        <img src={imageSrc(p.image_url)} alt={p.name} loading="lazy" />
                      ) : (
                        <span className="product-cat">No image</span>
                      )}
                    </div>
                    <div className="product-body">
                      <span className="product-cat">{p.category}</span>
                      <h3 className="product-name">{p.name}</h3>
                      <p className="product-desc">{p.short_description}</p>
                      <span className="product-price">{formatPrice(p.price)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
