"""Compile .lang tests and write all emits to tests/emits/."""
import os
import sys

# Add project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from compiler_v2 import AICodeCompiler

TESTS_DIR = os.path.join(ROOT_DIR, "tests")
EMITS_DIR = os.path.join(TESTS_DIR, "emits")

# Ecom storefront packaging policy:
# - `storefront/app.jsx` + `storefront/index.html` are canonical sources.
# - Embedded storefront constants below are packaging-only fallbacks.
# - See `tooling/artifact_policy.json` (`packaging-embedded`).
def _get_storefront_content():
    root = ROOT_DIR
    jsx_path = os.path.join(root, "storefront", "app.jsx")
    html_path = os.path.join(root, "storefront", "index.html")
    if os.path.isfile(jsx_path) and os.path.isfile(html_path):
        with open(jsx_path) as f:
            jsx = f.read()
        with open(html_path) as f:
            html = f.read()
        return jsx, html, "storefront/"
    # Embedded storefront fallback so build works without storefront/ folder.
    # This path is non-authoritative when canonical source files exist.
    jsx = _EMBEDDED_STOREFRONT_JSX
    html = _EMBEDDED_STOREFRONT_HTML
    return jsx, html, "embedded"

_EMBEDDED_STOREFRONT_JSX = r'''const { useState, useEffect } = React;

const API_BASE = '/api';
const CART_KEY = 'ecom_cart';

function useProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    fetch(API_BASE + '/products')
      .then(r => r.json())
      .then(d => { setProducts(Array.isArray(d.data) ? d.data : (d.products || [])); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);
  return { products, loading, error };
}

function loadCart() {
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (_) { return []; }
}

function saveCart(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items));
}

const Nav = ({ path, setPath, cartCount }) => (
  <nav className="nav">
    <a className={"nav-link" + (path === '/' ? ' active' : '')} href="#/" onClick={e => { e.preventDefault(); setPath('/'); }}>Home</a>
    <a className={"nav-link" + (path === '/products' ? ' active' : '')} href="#/products" onClick={e => { e.preventDefault(); setPath('/products'); }}>Shop</a>
    <a className="nav-link nav-cart" href="#/cart" onClick={e => { e.preventDefault(); setPath('/cart'); }}>
      Cart {cartCount > 0 ? <span className="cart-badge">{cartCount}</span> : null}
    </a>
  </nav>
);

const Header = () => (
  <header className="header">
    <h1 className="logo"><a href="#/">Store</a></h1>
  </header>
);

const ProductCard = ({ product, onAddToCart }) => (
  <article className="product-card">
    <div className="product-card__image">
      <span className="product-card__placeholder">{(product.name || '?').slice(0, 1)}</span>
    </div>
    <div className="product-card__body">
      <h3 className="product-card__name">{product.name || 'Product'}</h3>
      <p className="product-card__sku">{product.sku || ''}</p>
      <p className="product-card__price">${Number(product.price ?? 0).toFixed(2)}</p>
      <button type="button" className="btn btn-primary product-card__btn" onClick={() => onAddToCart(product)}>
        Add to cart
      </button>
    </div>
  </article>
);

const ProductGrid = ({ products, onAddToCart, loading, error }) => {
  if (loading) return <div className="page-section"><p className="muted">Loading products…</p></div>;
  if (error) return <div className="page-section"><p className="error">Failed to load: {error}</p></div>;
  if (!products.length) return <div className="page-section"><p className="muted">No products yet.</p></div>;
  return (
    <div className="product-grid">
      {products.map(p => <ProductCard key={p.id ?? p.sku ?? p.name} product={p} onAddToCart={onAddToCart} />)}
    </div>
  );
};

const CartItem = ({ item, onUpdateQty, onRemove }) => (
  <div className="cart-item">
    <div className="cart-item__info">
      <span className="cart-item__name">{item.name}</span>
      <span className="cart-item__price">${Number(item.price || 0).toFixed(2)}</span>
    </div>
    <div className="cart-item__actions">
      <input type="number" min="1" value={item.qty} onChange={e => onUpdateQty(item, parseInt(e.target.value, 10) || 1)} className="cart-item__qty" />
      <button type="button" className="btn btn-ghost" onClick={() => onRemove(item)}>Remove</button>
    </div>
  </div>
);

const CartPage = ({ cart, onUpdateQty, onRemove, setPath }) => {
  const total = cart.reduce((s, i) => s + (Number(i.price) || 0) * (i.qty || 1), 0);
  return (
    <div className="page-section">
      <h2 className="page-title">Your cart</h2>
      {cart.length === 0 ? (
        <p className="muted">Cart is empty. <a href="#/products" onClick={e => { e.preventDefault(); setPath('/products'); }}>Browse products</a></p>
      ) : (
        <>
          <div className="cart-list">
            {cart.map((item, i) => <CartItem key={item.id + '-' + i} item={item} onUpdateQty={onUpdateQty} onRemove={onRemove} />)}
          </div>
          <div className="cart-footer">
            <p className="cart-total">Total: <strong>${total.toFixed(2)}</strong></p>
            <button type="button" className="btn btn-primary" onClick={() => setPath('/checkout')}>Proceed to checkout</button>
          </div>
        </>
      )}
    </div>
  );
};

const CheckoutPage = ({ cart, setPath }) => {
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const total = cart.reduce((s, i) => s + (Number(i.price) || 0) * (i.qty || 1), 0);

  const handlePlaceOrder = () => {
    setSubmitting(true);
    fetch(API_BASE + '/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items: cart, total }) })
      .then(r => r.json())
      .then(() => { setDone(true); saveCart([]); })
      .catch(() => {})
      .finally(() => setSubmitting(false));
  };

  if (done) {
    return (
      <div className="page-section">
        <h2 className="page-title">Order received</h2>
        <p className="muted">Thank you. Your order has been submitted.</p>
        <button type="button" className="btn btn-primary" onClick={() => setPath('/')}>Back to home</button>
      </div>
    );
  }

  return (
    <div className="page-section">
      <h2 className="page-title">Checkout</h2>
      <div className="checkout-summary">
        <p><strong>{cart.length}</strong> item(s)</p>
        <p className="cart-total">Total: <strong>${total.toFixed(2)}</strong></p>
      </div>
      <button type="button" className="btn btn-primary" disabled={submitting || cart.length === 0} onClick={handlePlaceOrder}>
        {submitting ? 'Placing order…' : 'Place order'}
      </button>
    </div>
  );
};

const App = () => {
  const [path, setPath] = useState(() => (window.location.hash || '#/').slice(1) || '/');
  const [cart, setCart] = useState(loadCart);
  const { products, loading, error } = useProducts();

  useEffect(() => { const onHash = () => setPath((window.location.hash || '#/').slice(1) || '/'); window.addEventListener('hashchange', onHash); return () => window.removeEventListener('hashchange', onHash); }, []);
  useEffect(() => { saveCart(cart); }, [cart]);

  const addToCart = (product) => {
    const id = product.id ?? product.sku ?? product.name;
    const existing = cart.find(i => (i.id ?? i.sku ?? i.name) === id);
    if (existing) setCart(cart.map(i => i === existing ? { ...i, qty: (i.qty || 1) + 1 } : i));
    else setCart([...cart, { ...product, qty: 1 }]);
  };

  const updateQty = (item, qty) => {
    if (qty < 1) return setCart(cart.filter(i => i !== item));
    setCart(cart.map(i => i === item ? { ...i, qty } : i));
  };

  const removeFromCart = (item) => setCart(cart.filter(i => i !== item));

  const cartCount = cart.reduce((s, i) => s + (i.qty || 1), 0);

  const Page = path === '/cart' ? () => <CartPage cart={cart} onUpdateQty={updateQty} onRemove={removeFromCart} setPath={setPath} />
    : path === '/checkout' ? () => <CheckoutPage cart={cart} setPath={setPath} />
    : () => <ProductGrid products={products} onAddToCart={addToCart} loading={loading} error={error} />;

  return (
    <div className="app">
      <Header />
      <Nav path={path} setPath={setPath} cartCount={cartCount} />
      <main className="main">
        <Page />
      </main>
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));
'''

_EMBEDDED_STOREFRONT_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Store — Ecommerce</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #faf9f7;
      --surface: #fff;
      --text: #1a1a1a;
      --text-muted: #6b6b6b;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --border: #e5e5e5;
      --radius: 12px;
      --shadow: 0 2px 8px rgba(0,0,0,0.06);
      --shadow-hover: 0 8px 24px rgba(0,0,0,0.1);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'DM Sans', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
    .app { min-height: 100vh; display: flex; flex-direction: column; }
    .header {
      background: var(--text);
      color: var(--surface);
      padding: 1rem 1.5rem;
      display: flex; align-items: center; justify-content: center;
    }
    .logo { margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; }
    .logo a { color: inherit; text-decoration: none; }
    .logo a:hover { opacity: 0.9; }
    .nav {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0.75rem 1.5rem;
      display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;
    }
    .nav-link {
      color: var(--text);
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-weight: 500;
      transition: background 0.15s, color 0.15s;
    }
    .nav-link:hover { background: var(--bg); color: var(--accent); }
    .nav-link.active { background: var(--accent); color: var(--surface); }
    .nav-cart { position: relative; }
    .cart-badge {
      background: var(--accent);
      color: var(--surface);
      font-size: 0.7rem;
      padding: 0.15em 0.5em;
      border-radius: 999px;
      margin-left: 0.35rem;
    }
    .main { flex: 1; padding: 1.5rem; max-width: 1200px; margin: 0 auto; width: 100%; }
    .page-title { margin: 0 0 1rem; font-size: 1.5rem; font-weight: 600; }
    .page-section .muted { color: var(--text-muted); }
    .page-section .error { color: #b91c1c; }
    .product-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1.5rem;
    }
    .product-card {
      background: var(--surface);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: box-shadow 0.2s, transform 0.2s;
      display: flex; flex-direction: column;
    }
    .product-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
    .product-card__image {
      aspect-ratio: 1;
      background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%);
      display: flex; align-items: center; justify-content: center;
    }
    .product-card__placeholder {
      font-size: 3rem; font-weight: 700; color: var(--text-muted); opacity: 0.6;
    }
    .product-card__body { padding: 1.25rem; flex: 1; display: flex; flex-direction: column; }
    .product-card__name { margin: 0 0 0.25rem; font-size: 1.1rem; font-weight: 600; }
    .product-card__sku { margin: 0; font-size: 0.8rem; color: var(--text-muted); }
    .product-card__price { margin: 0.5rem 0; font-size: 1.25rem; font-weight: 600; color: var(--accent); }
    .product-card__btn { margin-top: auto; width: 100%; }
    .btn {
      display: inline-flex; align-items: center; justify-content: center;
      padding: 0.6rem 1.25rem;
      font: inherit; font-weight: 500;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      transition: background 0.15s, opacity 0.15s;
    }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-primary { background: var(--accent); color: var(--surface); }
    .btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
    .btn-ghost { background: transparent; color: var(--text-muted); }
    .btn-ghost:hover { background: var(--bg); color: var(--text); }
    .cart-list { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }
    .cart-item {
      background: var(--surface);
      padding: 1rem 1.25rem;
      border-radius: var(--radius);
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
      box-shadow: var(--shadow);
    }
    .cart-item__info { display: flex; flex-direction: column; }
    .cart-item__name { font-weight: 500; }
    .cart-item__price { color: var(--accent); font-weight: 600; }
    .cart-item__actions { display: flex; align-items: center; gap: 0.75rem; }
    .cart-item__qty { width: 4rem; padding: 0.4rem; border: 1px solid var(--border); border-radius: 6px; font: inherit; }
    .cart-footer { padding: 1rem 0; border-top: 1px solid var(--border); }
    .cart-total { font-size: 1.1rem; margin: 0.5rem 0; }
    .checkout-summary { margin-bottom: 1rem; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script crossorigin src="https://unpkg.com/react@17/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script type="text/babel" src="/app.jsx?v=3"></script>
</body>
</html>
'''

SERVER_STATIC_README = """# Static files (pages & apps)

Drop any pages or apps here. They are served at /.

- index.html, app.jsx = default dashboard (from .lang)
- Add subdirs or files: other-app/, admin.html, etc.
  They are served at /other-app/, /admin.html, ...
"""

def main():
    os.makedirs(EMITS_DIR, exist_ok=True)
    compiler = AICodeCompiler()
    for fname in sorted(os.listdir(TESTS_DIR)):
        if not fname.endswith(".lang"):
            continue
        path = os.path.join(TESTS_DIR, fname)
        base = fname[:-5]
        with open(path, "r") as f:
            code = f.read()
        ir = compiler.compile(code)
        # Write emits
        for ext, emit_fn in [
            ("react.tsx", compiler.emit_react),
            ("prisma.prisma", compiler.emit_prisma_schema),
            ("api.py", compiler.emit_python_api),
            ("mt5.mq5", compiler.emit_mt5),
            ("scraper.py", compiler.emit_python_scraper),
            ("cron.py", compiler.emit_cron_stub),
        ]:
            out_path = os.path.join(EMITS_DIR, f"{base}.{ext}")
            with open(out_path, "w") as f:
                f.write(emit_fn(ir))
        if ir.get("rag") and any(ir.get("rag", {}).get(k) for k in ("sources", "chunking", "embeddings", "stores", "indexes", "retrievers", "augment", "generate", "pipelines")):
            out_path = os.path.join(EMITS_DIR, f"{base}.rag.py")
            with open(out_path, "w") as f:
                f.write(compiler.emit_rag_pipeline(ir))
        # If .lang defines both API (core) and frontend (fe), emit unified server + static.
        # Emit server for the main ecom dashboard app so one server serves API + static.
        has_core = "core" in ir.get("services", {})
        has_fe = "fe" in ir.get("services", {})
        if has_core and has_fe and base == "ecom_dashboard":
            server_dir = os.path.join(EMITS_DIR, "server")
            static_dir = os.path.join(server_dir, "static")
            os.makedirs(static_dir, exist_ok=True)
            with open(os.path.join(server_dir, "server.py"), "w") as f:
                f.write(compiler.emit_server(ir))
            with open(os.path.join(server_dir, "ir.json"), "w") as f:
                f.write(compiler.emit_ir_json(ir))
            with open(os.path.join(server_dir, "requirements.txt"), "w") as f:
                f.write("fastapi\nuvicorn[standard]\n")
            # Always write ecom storefront (product grid, cart, checkout) so serve_dashboard shows it
            _jsx, _html, _src = _get_storefront_content()
            with open(os.path.join(static_dir, "app.jsx"), "w") as f:
                f.write(_jsx)
            with open(os.path.join(static_dir, "index.html"), "w") as f:
                f.write(_html)
            print("  -> static: storefront (%s)" % _src)
            with open(os.path.join(static_dir, "README.md"), "w") as f:
                f.write(SERVER_STATIC_README)
            with open(os.path.join(server_dir, "openapi.json"), "w") as f:
                f.write(compiler.emit_openapi(ir))
            with open(os.path.join(server_dir, "runbooks.md"), "w") as f:
                f.write(compiler.emit_runbooks(ir))
            with open(os.path.join(server_dir, "Dockerfile"), "w") as f:
                f.write(compiler.emit_dockerfile(ir))
            with open(os.path.join(server_dir, "docker-compose.yml"), "w") as f:
                f.write(compiler.emit_docker_compose(ir))
            with open(os.path.join(server_dir, "k8s.yaml"), "w") as f:
                f.write(compiler.emit_k8s(ir, name="ainl-api", replicas=1, with_ingress=False))
            with open(os.path.join(server_dir, ".env.example"), "w") as f:
                f.write(compiler.emit_env_example(ir))
            migrations_dir = os.path.join(server_dir, "migrations")
            os.makedirs(migrations_dir, exist_ok=True)
            with open(os.path.join(migrations_dir, "001_initial.sql"), "w") as f:
                f.write(compiler.emit_sql_migrations(ir, dialect="postgres"))
            next_routes = compiler.emit_next_api_routes(ir)
            next_dir = os.path.join(server_dir, "next")
            for key, content in next_routes.items():
                if key.startswith("_"):
                    continue
                out_path = os.path.join(next_dir, key)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w") as f:
                    f.write(content)
            with open(os.path.join(static_dir, "App.vue"), "w") as f:
                f.write(compiler.emit_vue_browser(ir))
            with open(os.path.join(static_dir, "App.svelte"), "w") as f:
                f.write(compiler.emit_svelte_browser(ir))
            # Copy runtime package + adapters so server dir is self-contained for Docker
            import shutil
            _root = ROOT_DIR
            _rt = os.path.join(_root, "runtime")
            _rt_dest = os.path.join(server_dir, "runtime")
            if os.path.isdir(_rt):
                if os.path.isdir(_rt_dest):
                    shutil.rmtree(_rt_dest)
                shutil.copytree(_rt, _rt_dest)
            _ad = os.path.join(_root, "adapters")
            _ad_dest = os.path.join(server_dir, "adapters")
            if os.path.isdir(_ad):
                if os.path.isdir(_ad_dest):
                    shutil.rmtree(_ad_dest)
                shutil.copytree(_ad, _ad_dest)
            print(f"Compiled {fname} -> emits/{base}.* + server/ (API + static + OpenAPI + Docker)")
        if base == "ecom_dashboard":
            dashboard_dir = os.path.join(EMITS_DIR, "dashboard")
            os.makedirs(dashboard_dir, exist_ok=True)
            with open(os.path.join(dashboard_dir, "app.jsx"), "w") as f:
                f.write(compiler.emit_react_browser(ir))
            if not (has_core and has_fe):
                print(f"Compiled {fname} -> emits/{base}.* + dashboard/app.jsx")
        if not (has_core and has_fe) and base != "test_ecom_dashboard":
            print(f"Compiled {fname} -> emits/{base}.*")
    print("Done.")


def _index_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; padding: 1rem; background: #f5f5f5; }
    .dashboard { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    h1 { margin-top: 0; color: #333; }
    pre { background: #f8f8f8; padding: 1rem; border-radius: 4px; overflow: auto; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script crossorigin src="https://unpkg.com/react@17/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script type="text/babel" src="/app.jsx?v=2"></script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
