import apiRequest from './client'

interface SignupData{
  email: string
  password: string
}

interface LoginData{
    email:string
    password:string
}

interface TokenResponse{
    access_token:string
    token_type:string
}

export function signup(data: SignupData) {
  return apiRequest('/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
}

export function login(data:LoginData): Promise<TokenResponse>{
    return apiRequest(
        '/auth/login',{
            method:'POST',
            headers:{
                'Content-Type':'application/json',
            },
            body: JSON.stringify(data)
        }
    )
}

export function getMe(){
    return apiRequest('/auth/me')
}