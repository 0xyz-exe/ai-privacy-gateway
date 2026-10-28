# Contributing to AI Privacy Gateway

We welcome contributions from the community!

## Development Guidelines

1. **Modular Architecture:** Add new PII recognizers to `app/privacy/recognizers/` extending `BaseRecognizer`.
2. **Deterministic Tests:** Ensure all new recognizers and policies have unit tests in `backend/tests/`.
3. **No Secret Commits:** Never commit `.env` files, production credentials, or real personal information.
4. **Code Quality:** Format backend code using standard formatting and run `pytest backend/tests` before submitting PRs.
5. **Frontend Changes:** Verify that `npm run build` inside `frontend/` succeeds without type errors.

## Pull Request Process

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/my-new-recognizer`).
3. Commit your changes (`git commit -m 'feat: add custom recognizer'`).
4. Push to your branch (`git push origin feature/my-new-recognizer`).
5. Open a Pull Request.
