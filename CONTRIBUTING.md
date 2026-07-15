# Contributing to Double N Trading

## Development Setup

```bash
git clone https://github.com/NadimMohamed/DoubleN
cd DoubleN

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Code Quality Standards

- **Backend**: Type hints on all functions, async/await, proper error handling
- **Frontend**: TypeScript everywhere, React hooks, proper error boundaries
- **Database**: Migrations for all schema changes, proper indexing
- **API**: Consistent response formats, proper HTTP status codes

## PR Process

1. Create feature branch from main
2. Make changes with proper commit messages
3. Ensure tests pass (if applicable)
4. Create PR with detailed description
5. Code review required before merge
6. Merging triggers auto-deploy on Railway

## Areas for Contribution

- [ ] Chart enhancements (timeframes, indicators overlay)
- [ ] BingX exchange integration
- [ ] Position risk analyzer
- [ ] Advanced settings (2FA, API key management)
- [ ] Performance optimizations
- [ ] Test coverage
- [ ] Documentation
