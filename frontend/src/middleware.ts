import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_ROUTES = ['/auth/login', '/auth/register']
const PROTECTED_PREFIX = ['/dashboard', '/watchlist']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public routes always
  if (PUBLIC_ROUTES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next()
  }

  // Protect dashboard/watchlist — check for token cookie or header
  const isProtected = PROTECTED_PREFIX.some((p) => pathname.startsWith(p))
  if (!isProtected) return NextResponse.next()

  // Check for token in cookies (set by client after login)
  const token = request.cookies.get('dnt_access_token')?.value

  if (!token) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('next', pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)'],
}
