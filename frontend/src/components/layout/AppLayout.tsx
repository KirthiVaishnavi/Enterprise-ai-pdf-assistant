import { Link, Outlet,useNavigate, useLocation } from 'react-router-dom'
import { removeToken } from '../../auth/storage'

function AppLayout() {
    const navigate=useNavigate()
    const location=useLocation()

    function handleLogout(){
        removeToken()
        navigate('/login')
    }
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-brand">
            <h1>PDF Assistant</h1>
        </div>

        <nav className="app-nav">
            {location.pathname === '/chat' && (
            <Link to="/dashboard">Dashboard</Link>
            )}

            <button type="button" onClick={handleLogout}>
                Logout
            </button>
        </nav>
      </header>

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout