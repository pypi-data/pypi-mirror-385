# Changelog

All notable changes to EzDB B-Class will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-11

### 🎉 Official B-Class Release

**Status:** STABLE - Production Ready

This is the first stable release of EzDB B-Class (Basic). This version is locked and will receive only bug fixes and security patches. No breaking changes will be made in the 1.x series.

### Added
- Core vector storage and search functionality
- HNSW (Hierarchical Navigable Small World) indexing for fast ANN search
- Multiple similarity metrics (cosine, euclidean, dot product)
- Metadata filtering
- Collections management (multiple isolated databases)
- Persistence (save/load to disk)
- REST API server with FastAPI
- Python client library for REST API
- Docker support with docker-compose
- Comprehensive documentation
  - README.md - Project overview
  - GETTING_STARTED.md - Beginner's guide
  - API.md - Complete API reference
  - DEPLOYMENT.md - Deployment guide
  - PRODUCT_TIERS.md - Product strategy
- Example applications
  - Basic usage example
  - Semantic search demo
  - REST API client demo
- Unit tests with pytest
- MIT License (free and open source)

### Features
- ✅ Vector insert, search, get, delete operations
- ✅ Batch operations for efficiency
- ✅ Multiple collections per database
- ✅ Metadata filtering during search
- ✅ Save/load databases to disk
- ✅ Embedded mode (Python library)
- ✅ Server mode (REST API)
- ✅ Health checks
- ✅ Statistics endpoint
- ✅ CORS support for web applications

### Limitations (By Design)
- ⚠️ No authentication (open access)
- ⚠️ No encryption
- ⚠️ No automated backups
- ⚠️ No high availability
- ⚠️ No monitoring/metrics
- ⚠️ No rate limiting
- ⚠️ Manual persistence only
- ⚠️ Single-machine deployment
- ⚠️ Community support only (no SLA)

> **Note:** For production features, see [EzDB Professional](PRODUCT_TIERS.md)

---

## Future Releases

### Version 1.x (B-Class Maintenance)
- Only bug fixes and security patches
- No new features
- No breaking changes
- Stability guaranteed

### Version 2.x (Professional Class)
- Production-grade reliability
- Authentication and security
- Performance optimizations
- Monitoring and observability
- Multi-language clients
- See [PRODUCT_TIERS.md](PRODUCT_TIERS.md) for details

### Version 3.x (Enterprise Class)
- Multi-tenancy
- Advanced security and compliance
- Distributed architecture
- Enterprise support
- See [PRODUCT_TIERS.md](PRODUCT_TIERS.md) for details

---

## Upgrade Policy

### B-Class (1.x)
- **Stability Promise:** No breaking changes in 1.x series
- **Bug Fixes:** Security patches and critical bug fixes only
- **Duration:** Supported indefinitely as long as Python 3.8+ is available
- **Migration:** Easy upgrade path to Professional when ready

### Professional (2.x)
- **Breaking Changes:** May introduce breaking changes from 1.x
- **Migration Guide:** Provided for smooth transition
- **Backward Compatibility:** Data format compatible with B-Class

### Enterprise (3.x)
- **Breaking Changes:** May introduce breaking changes from 2.x
- **Migration Support:** Assisted migration for Enterprise customers
- **Backward Compatibility:** Can import from Professional and B-Class

---

## How to Upgrade

### From B-Class to Professional

```python
# 1. Export your B-Class data
from ezdb import EzDB

db = EzDB.load("my_database.ezdb")
vectors = db.get_all_vectors()
metadata = db.get_all_metadata()
ids = db.get_all_ids()

# 2. Import to Professional
from ezdb_professional import EzDBProClient

client = EzDBProClient(
    url="https://api.ezdb.io",
    api_key="your_key"
)

client.insert_batch(
    vectors=vectors,
    metadata_list=metadata,
    ids=ids
)
```

---

## Contributing

We welcome contributions to EzDB B-Class!

- 🐛 **Bug Reports:** [Open an issue](https://github.com/yourusername/ezdb/issues)
- 🔧 **Bug Fixes:** PRs for bug fixes are welcome
- 📖 **Documentation:** Help improve our docs
- ⚠️ **New Features:** Will not be accepted for B-Class (but see Professional!)

---

## Support

### B-Class (Free)
- Community support via GitHub issues
- Documentation
- No SLA

### Professional
- Email support (24-48hr response)
- 99.9% uptime SLA
- Priority bug fixes

### Enterprise
- Dedicated support team
- Phone support
- 99.99% uptime SLA
- Custom feature development

[Contact Sales](mailto:sales@ezdb.io) for Professional and Enterprise options.

---

## License

EzDB B-Class is released under the [MIT License](LICENSE).

EzDB Professional and Enterprise are proprietary software with separate commercial licenses.
