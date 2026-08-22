# Bom de Clique — Zernio command bridge

This bridge lets ChatGPT operate Zernio indirectly through GitHub Issues while keeping the Zernio API credential in GitHub Actions Secrets.

## Security model

- Credential name: `ZERNIO_API_KEY` (GitHub Actions secret only; never commit it).
- Workflow triggers only for issues whose title starts with `[BDC-ZERNIO]`.
- API paths are allowlisted to accounts, analytics, posts, media, profiles, and usage.
- Results are written back as issue comments so the ChatGPT GitHub connector can read them.

## Command format

The entire issue body must be JSON.

Read-only health check:

```json
{"method":"GET","path":"/v1/accounts"}
```

Example draft creation (do not publish):

```json
{
  "method":"POST",
  "path":"/v1/posts",
  "body": {
    "title": "Bom de Clique test draft",
    "content": "Teste controlado",
    "isDraft": true
  }
}
```

Production publishing remains approval-gated in the ChatGPT conversation. The bridge does not itself decide what to publish.
