import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, imageSrc, type ProductDetail } from '../lib/api'

export default function ProductDetailPage() {
  const { productId = '' } = useParams()
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    fetchProduct(productId)
      .then((data) => active && setProduct(data))
      .catch((err: Error) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [productId])

  return (
    <div className="page">
      <div className="container">
        <Link to="/products" className="back-link">
          ← Back to all products
        </Link>

        {loading && <p className="state">Loading…</p>}

        {error && (
          <div className="state">
            <div className="state-error">
              <strong>Couldn't load this product.</strong>
              <br />
              {error}
            </div>
          </div>
        )}

        {product && (
          <div className="detail">
            <div className="detail-image">
              {product.image_url && (
                <img src={imageSrc(product.image_url)} alt={product.name} />
              )}
            </div>

            <div>
              <p className="eyebrow">{product.garment_type ?? product.category}</p>
              <h1>{product.name}</h1>
              <p className="detail-price">{formatPrice(product.price)}</p>
              <p className="detail-desc">{product.description}</p>

              {product.colors.length > 0 && (
                <div className="detail-section">
                  <h3>Colors</h3>
                  <div className="tag-row">
                    {product.colors.map((c) => (
                      <span className="tag" key={c}>
                        {c}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {product.sizes.length > 0 && (
                <div className="detail-section">
                  <h3>Available Sizes</h3>
                  <div className="size-grid">
                    {product.sizes.map((s) => (
                      <div
                        className={`size-box ${s.in_stock ? '' : 'out'}`}
                        key={s.size}
                      >
                        <span className="size-label">{s.size}</span>
                        <span className="size-stock">
                          {s.in_stock ? `${s.quantity} in stock` : 'Sold out'}
                        </span>
                      </div>
                    ))}
                  </div>
                  <p className="stock-note">
                    {product.in_stock
                      ? `${product.total_stock} total in stock across all sizes.`
                      : 'Currently sold out in every size.'}
                  </p>
                </div>
              )}

              {product.search_tags.length > 0 && (
                <div className="detail-section">
                  <h3>Tags</h3>
                  <div className="tag-row">
                    {product.search_tags.map((t) => (
                      <span className="tag" key={t}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
