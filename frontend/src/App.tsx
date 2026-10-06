import { Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import ChatPanel from './components/ChatPanel'
import Footer from './components/Footer'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetailPage from './pages/ProductDetail'
import About from './pages/About'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
      {/* Floating assistant: mounted once here so it is present on every route. */}
      <ChatPanel />
    </div>
  )
}
