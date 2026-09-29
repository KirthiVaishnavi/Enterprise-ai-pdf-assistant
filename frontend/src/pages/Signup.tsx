import { useState, type SubmitEvent } from "react"
import { useNavigate } from "react-router-dom"
import { signup } from "../api/auth"

function Signup(){
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
            await signup({
            email,
            password,
            })

            navigate('/login')
        }
        catch{
            setError('Signup failed. Please check your details.')
        }
        finally{
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>PDF Assistant</h1>
                    <p>Create an account to get started</p>
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
                        {loading?'Signing up...':'Signup'}
                    </button>
                </form>

                <p className="auth-footer">
                    Already have an account?{' '}
                    <button type="button" onClick={() => navigate('/login')}>
                    Login
                    </button>
                </p>
            </div>
        </div>
    )
}
export default Signup