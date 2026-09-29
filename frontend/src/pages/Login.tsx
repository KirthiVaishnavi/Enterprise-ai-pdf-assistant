import { useState, type SubmitEvent} from 'react'
import { login } from '../api/auth'
import { saveToken } from '../auth/storage'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]=useState(false)
  const [error, setError]=useState('')
  const navigate= useNavigate()

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    setLoading(true)
    setError('')
    try{
        const response = await login({
        email,
        password,
        })

        saveToken(response.access_token)
        navigate('/dashboard')
    }
    catch{
        setError('Login failed. Please check your email and password.')
    }
    finally{
        setLoading(false)
    }
  }

  return (
    <div className='auth-page'>
        <div className='auth-card'>
            <div className="auth-header">
                <h1>PDF Assistant</h1>
                <p>Sign in to continue</p>
            </div>

            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="auth-field">
                    <label htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                    />
                </div>

                <div className="auth-field">
                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                    />
                </div>

                {error && <p className="auth-error">{error}</p>}
                <button className="auth-button" type="submit" disabled={loading}> 
                    {loading? "Logging in...": 'Login'}
                </button>
            </form>

            <p className="auth-footer">
                Don't have an account?{' '}
                <button type="button" onClick={() => navigate('/signup')}>
                Sign up
                </button>
            </p>

        </div>
    </div>
  )
}

export default Login