import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="page">
      <div className="container state">
        <h1>Page not found</h1>
        <p>
          That page isn't in the collection. <Link to="/products">Browse products</Link>
        </p>
      </div>
    </div>
  )
}
