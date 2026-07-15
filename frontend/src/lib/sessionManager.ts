import axios from 'axios'

class SessionManager {
  private refreshTimeout: NodeJS.Timeout | null = null
  private readonly REFRESH_BEFORE_MS = 5 * 60 * 1000 // Refresh 5 min before expiry

  async refreshTokenIfNeeded() {
    try {
      const token = localStorage.getItem('accessToken')
      const expiresAt = localStorage.getItem('tokenExpiresAt')
      
      if (!token || !expiresAt) return
      
      const now = Date.now()
      const expiryTime = parseInt(expiresAt)
      const timeUntilExpiry = expiryTime - now
      
      // Refresh if less than REFRESH_BEFORE_MS remaining
      if (timeUntilExpiry < this.REFRESH_BEFORE_MS) {
        await this.refresh()
      }
    } catch (error) {
      console.error('Failed to refresh token', error)
    }
  }

  private async refresh() {
    try {
      const response = await axios.post('/api/v1/auth/refresh')
      const { access_token, token_type } = response.data
      
      // Store token with expiry
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('tokenType', token_type)
      
      // Calculate expiry (assuming 1 hour from now)
      const expiresAt = Date.now() + 60 * 60 * 1000
      localStorage.setItem('tokenExpiresAt', expiresAt.toString())
      
      this.scheduleNextRefresh()
    } catch (error) {
      console.error('Token refresh failed', error)
      this.logout()
    }
  }

  scheduleNextRefresh() {
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
    }
    
    this.refreshTimeout = setTimeout(
      () => this.refreshTokenIfNeeded(),
      30 * 1000 // Check every 30 seconds
    )
  }

  logout() {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('tokenType')
    localStorage.removeItem('tokenExpiresAt')
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
    }
  }
}

export const sessionManager = new SessionManager()
