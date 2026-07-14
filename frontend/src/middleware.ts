import { NextRequest, NextResponse } from 'next/server'

const AUTH_ROUTES = ['/auth/login', '/auth/register']
const PROTECTED_PREFIX = ['/dashboard', '/watchlist']

function isValidToken(token: string | undefined): boolean {
  if (!token) return false
  try {
    // A JWT has three dot-separated, base64url-encoded segments. We only
    // need a lightweight structural/expiry check here — the API itself is
    // the source of truth and will reject invalid/expired tokens.
    const parts = token.split('.')
    if (parts.length !== 3) return false

    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString('utf-8'))
    if (payload?.exp && Date.now() >= payload.exp * 1000) {
      return false
    }
    return true
  } catch (err) {
    console.error('[middleware] Failed to parse token, treating as invalid:', err)
    return false
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  try {
    const token = request.cookies.get('dnt_access_token')?.value
    const authenticated = isValidToken(token)

    const isAuthRoute = AUTH_ROUTES.some((r) => pathname.startsWith(r))
    const isProtectedRoute = PROTECTED_PREFIX.some((p) => pathname.startsWith(p))

    // Authenticated users shouldn't see the login/register screens again.
    if (isAuthRoute && authenticated) {
      console.log(`[middleware] Authenticated request to ${pathname} — redirecting to /dashboard`)
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // Unauthenticated users can't reach protected routes.
    if (isProtectedRoute && !authenticated) {
      console.log(`[middleware] Unauthenticated request to ${pathname} — redirecting to /auth/login`)
      const loginUrl = new URL('/auth/login', request.url)
      loginUrl.searchParams.set('next', pathname)
      return NextResponse.redirect(loginUrl)
    }

    console.log(`[middleware] Allowing request to ${pathname}`)
    return NextResponse.next()
  } catch (err) {
    // Fail closed for protected routes, fail open for everything else so a
    // middleware bug can't take down the whole site.
    console.error(`[middleware] Unexpected error while evaluating ${pathname}:`, err)
    const isProtectedRoute = PROTECTED_PREFIX.some((p) => pathname.startsWith(p))
    if (isProtectedRoute) {
      return NextResponse.redirect(new URL('/auth/login', request.url))
    }
    return NextResponse.next()
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/watchlist/:path*', '/auth/login', '/auth/register'],
}
