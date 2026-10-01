# Data

| Folder | Contents |
|--------|----------|
| `sheets/` | One CSV per Google Sheets tab, with headers and synthetic sample rows. Import each as a tab of **AI Maintenance Operations Database**. Column definitions: [docs/data-model.md](../docs/data-model.md). |
| `samples/` | Sample work order email, the AI extraction it should produce, and three assessment cases used by `python -m maintenance_ops.cli demo`. |

All data is fictional. Put real exports in `data/private/`, which is git-ignored.
