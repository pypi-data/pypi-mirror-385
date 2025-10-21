# Kaizen Documentation - Quick Navigator for Claude Code

**Purpose**: Concise instructions for navigating Kaizen documentation
**For**: Claude Code agents and developers
**Complement**: README.md (detailed reference)

---

## 📍 Quick Navigation

### For New Users
1. **[Getting Started](getting-started/quickstart.md)** - 5-min quickstart
2. **[Core Concepts](getting-started/concepts.md)** - Essential understanding
3. **[Examples](../examples/)** - Working code examples

### For Developers
1. **[Multi-Modal API](reference/multi-modal-api-reference.md)** - Vision, audio, multi-modal (**START HERE for multi-modal**)
2. **[Integration Testing](development/integration-testing-guide.md)** - Real model validation
3. **[Developer Experience](developer-experience/README.md)** - UX improvements (config auto-extraction, etc.)
4. **[Testing Strategy](development/testing.md)** - 3-tier testing approach
5. **[Test Configuration](development/TESTING_WITH_CUSTOM_MOCK_PROVIDERS.md#test-configuration-authority)** - Conftest authority (IMPORTANT)

### For Problem Solving
1. **[Troubleshooting](reference/troubleshooting.md)** - Common errors and fixes
2. **[Common Pitfalls](reference/multi-modal-api-reference.md#common-pitfalls)** - Multi-modal API mistakes
3. **[Integration Testing Guide](development/integration-testing-guide.md#bug-detection-patterns)** - Debugging patterns

### For Architecture Decisions
1. **[ADR Index](architecture/adr/README.md)** - All architecture decisions
2. **[Integration Strategy](architecture/design/KAIZEN_INTEGRATION_STRATEGY.md)** - Framework integration
3. **[Testing Strategy (ADR-005)](architecture/adr/ADR-005-testing-strategy-alignment.md)** - 3-tier testing
4. **[Claude Agent SDK vs Kaizen](architecture/comparisons/CLAUDE_AGENT_SDK_VS_KAIZEN_PARITY_ANALYSIS.md)** - Framework comparison and decision guide

---

## 📂 Folder Structure

```
docs/
├── getting-started/        # New user onboarding
├── reference/              # API docs, troubleshooting
│   ├── api-reference.md                    # General API
│   ├── multi-modal-api-reference.md        # Vision, audio, multi-modal
│   └── troubleshooting.md                  # Common errors
├── development/            # Developer guides
│   ├── integration-testing-guide.md        # Real model validation
│   ├── testing.md                          # 3-tier strategy
│   └── patterns.md                         # Code patterns
├── developer-experience/   # UX improvements
│   ├── 01-config-auto-extraction.md
│   ├── 02-shared-memory-convenience.md
│   └── 03-result-parsing.md
├── integrations/           # Platform integrations
│   ├── dataflow/           # Database framework
│   ├── mcp/                # Model Context Protocol
│   └── nexus/              # Multi-channel platform
├── architecture/           # Design decisions
│   ├── adr/                # Architecture Decision Records
│   └── design/             # System design
├── deployment/             # Production deployment
├── enterprise/             # Enterprise features
├── reports/                # Implementation reports
└── research/               # Advanced topics
```

---

## 🎯 Common Tasks

### Task: Implement Multi-Modal Feature
**Path**:
1. [Multi-Modal API Reference](reference/multi-modal-api-reference.md) - API signatures
2. [Integration Testing Guide](development/integration-testing-guide.md) - Validation
3. [Common Pitfalls](reference/multi-modal-api-reference.md#common-pitfalls) - Avoid mistakes

### Task: Fix Integration Bug
**Path**:
1. [Troubleshooting](reference/troubleshooting.md) - Known issues
2. [Integration Testing](development/integration-testing-guide.md#bug-detection-patterns) - Debug patterns
3. [Multi-Modal API](reference/multi-modal-api-reference.md#troubleshooting) - Multi-modal errors

### Task: Add New Agent
**Path**:
1. [Developer Experience](developer-experience/README.md) - UX patterns
2. [Testing Strategy](development/testing.md) - Test structure
3. [Examples](../examples/) - Copy working example

### Task: Deploy to Production
**Path**:
1. [Deployment Guide](deployment/README.md) - Deploy strategies
2. [Enterprise Security](enterprise/security.md) - Security checklist
3. [Monitoring](enterprise/monitoring.md) - Observability

---

## 🔍 Finding Information

### By Topic

| Topic | Location |
|-------|----------|
| **Multi-Modal (Vision/Audio)** | `reference/multi-modal-api-reference.md` |
| **Integration Testing** | `development/integration-testing-guide.md` |
| **UX Improvements** | `developer-experience/README.md` |
| **Testing Strategy** | `development/testing.md` or `architecture/adr/ADR-005` |
| **Framework Comparison** | `architecture/comparisons/CLAUDE_AGENT_SDK_VS_KAIZEN_PARITY_ANALYSIS.md` |
| **MCP Integration** | `integrations/mcp/README.md` |
| **DataFlow** | `integrations/dataflow/` |
| **Deployment** | `deployment/README.md` |
| **Troubleshooting** | `reference/troubleshooting.md` |

### By User Type

**New User**:
- Start: `getting-started/quickstart.md`
- Learn: `getting-started/concepts.md`
- Practice: `../examples/`

**Developer**:
- API: `reference/multi-modal-api-reference.md`
- Testing: `development/integration-testing-guide.md`
- Patterns: `developer-experience/README.md`

**Architect**:
- Decisions: `architecture/adr/README.md`
- Design: `architecture/design/`
- Strategy: `architecture/adr/ADR-005-testing-strategy-alignment.md`

**Operator**:
- Deploy: `deployment/README.md`
- Monitor: `enterprise/monitoring.md`
- Troubleshoot: `reference/troubleshooting.md`

---

## ⚡ Critical Documents

### Multi-Modal Development (Phases 0-5)
- **[Multi-Modal API Reference](reference/multi-modal-api-reference.md)** - Complete API with common pitfalls
- **[Integration Testing Guide](development/integration-testing-guide.md)** - Real model validation requirements

### Developer Experience
- **[UX Improvements](developer-experience/README.md)** - Config auto-extraction, concise APIs
- **[Testing Strategy](development/testing.md)** - 3-tier approach (unit, integration, e2e)

### Integration
- **[MCP Guide](integrations/mcp/README.md)** - Model Context Protocol integration
- **[DataFlow](integrations/dataflow/best-practices.md)** - Database framework patterns
- **[Nexus](integrations/nexus/best-practices.md)** - Multi-channel platform

### Architecture
- **[ADR Index](architecture/adr/README.md)** - All architecture decisions
- **[Testing Strategy ADR](architecture/adr/ADR-005-testing-strategy-alignment.md)** - 3-tier testing

---

## 🚨 Common Mistakes

### Mistake 1: Creating Root Conftest.py
**Problem**: Creating `conftest.py` in project root causes conflicts
**Solution**: Use `tests/conftest.py` ONLY - this is the authority
**Evidence**: Root conftest runs first and conflicts with test infrastructure
**Fix**: Read [Test Configuration Authority](development/TESTING_WITH_CUSTOM_MOCK_PROVIDERS.md#test-configuration-authority)

### Mistake 2: Skipping Integration Tests
**Problem**: Relying only on mocked unit tests
**Solution**: Read [Integration Testing Guide](development/integration-testing-guide.md)
**Evidence**: Phase 4 had 94 unit tests passing but 2 critical bugs found only with real inference

### Mistake 3: Wrong Multi-Modal API
**Problem**: Using 'prompt' instead of 'question' for VisionAgent
**Solution**: Check [Multi-Modal API Reference](reference/multi-modal-api-reference.md#common-pitfalls)
**Fix**: Always use config objects for OllamaVisionProvider

### Mistake 4: Missing Documentation Trace
**Problem**: New docs not linked from README
**Solution**: Follow trace: `README.md` → `docs/README.md` → specific doc

---

## 📊 Documentation Status

### Complete & Production-Ready ✅
- ✅ Multi-Modal API Reference (Phases 0-5)
- ✅ Integration Testing Guide
- ✅ Developer Experience UX guides
- ✅ MCP Integration
- ✅ DataFlow Integration
- ✅ Nexus Integration

### In Progress ⏳
- ⏳ Advanced RAG techniques
- ⏳ Performance optimization guides

---

## 🔄 Using This Guide

1. **Quick lookup**: Use "Finding Information" tables above
2. **Task-based**: Follow "Common Tasks" workflows
3. **Problem solving**: Check "Common Mistakes" first
4. **Deep dive**: See README.md for comprehensive index

**Remember**: This is instructions, README.md is reference.

---

**Last Updated**: 2025-10-05
**Maintainer**: Kaizen AI Team
**Related**: [README.md](README.md) - Comprehensive documentation index
