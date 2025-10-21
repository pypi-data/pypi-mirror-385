# Documentation Migration Notice

## Summary of Changes

The CovetPy Framework documentation has been reorganized to better reflect the current development focus and future roadmap. This migration notice explains what changed and where to find specific documentation.

## What Changed

### Documentation Restructure (January 2025)

1. **Archive Created**: Previous implementation documentation moved to `archive/` folder
2. **Development Plan Promoted**: New development planning documents moved to root level
3. **Focus Shift**: Documentation now emphasizes development planning over current implementation

### Before Migration Structure
```
docs/
├── README.md (general framework documentation)
├── GETTING_STARTED.md
├── FRAMEWORK_ARCHITECTURE.md
├── API_FLOW_AND_LIFECYCLE.md
├── ... (many current implementation docs)
└── development-plan/
    ├── ROADMAP.md
    ├── SPRINT_PLAN.md
    ├── TEAM_STRUCTURE.md
    └── ... (development planning docs)
```

### After Migration Structure
```
docs/
├── README.md (NEW: development planning focus)
├── PROJECT_OVERVIEW.md (promoted from development-plan/)
├── ROADMAP.md (promoted from development-plan/)
├── SPRINT_PLAN.md (promoted from development-plan/)
├── TEAM_STRUCTURE.md (promoted from development-plan/)
├── TECHNICAL_REQUIREMENTS.md (promoted from development-plan/)
├── ARCHITECTURE_DESIGN.md (promoted from development-plan/)
├── RUST_PERFORMANCE_ARCHITECTURE.md (promoted from development-plan/)
├── API_DESIGN_PATTERNS.md (promoted from development-plan/)
├── MIGRATION_STRATEGY.md (promoted from development-plan/)
├── CURRENT_VS_PROPOSED_COMPARISON.md (promoted from development-plan/)
└── archive/
    ├── README.md (OLD: general framework documentation)
    ├── GETTING_STARTED.md
    ├── FRAMEWORK_ARCHITECTURE.md
    ├── API_FLOW_AND_LIFECYCLE.md
    ├── ... (all previous implementation docs)
    └── ... (preserved directory structure)
```

## Document Migration Map

### Promoted to Root (Active Development Focus)
| Current Location | Previous Location | Purpose |
|------------------|-------------------|---------|
| `/docs/PROJECT_OVERVIEW.md` | `/docs/development-plan/PROJECT_OVERVIEW.md` | Executive summary and development phases |
| `/docs/ROADMAP.md` | `/docs/development-plan/ROADMAP.md` | 6-month development roadmap |
| `/docs/SPRINT_PLAN.md` | `/docs/development-plan/SPRINT_PLAN.md` | 12 detailed sprints with tasks |
| `/docs/TEAM_STRUCTURE.md` | `/docs/development-plan/TEAM_STRUCTURE.md` | Team composition and budget |
| `/docs/TECHNICAL_REQUIREMENTS.md` | `/docs/development-plan/TECHNICAL_REQUIREMENTS.md` | Technical specifications |
| `/docs/ARCHITECTURE_DESIGN.md` | `/docs/development-plan/ARCHITECTURE_DESIGN.md` | System architecture and design |
| `/docs/RUST_PERFORMANCE_ARCHITECTURE.md` | `/docs/development-plan/RUST_PERFORMANCE_ARCHITECTURE.md` | Rust-Python hybrid architecture |
| `/docs/API_DESIGN_PATTERNS.md` | `/docs/development-plan/API_DESIGN_PATTERNS.md` | Framework design patterns |
| `/docs/MIGRATION_STRATEGY.md` | `/docs/development-plan/MIGRATION_STRATEGY.md` | Version compatibility strategy |
| `/docs/CURRENT_VS_PROPOSED_COMPARISON.md` | `/docs/development-plan/CURRENT_VS_PROPOSED_COMPARISON.md` | Implementation comparison |

### Moved to Archive (Legacy Implementation)
| New Location | Previous Location | Purpose |
|--------------|-------------------|---------|
| `/docs/archive/README.md` | `/docs/README.md` | Previous general framework documentation |
| `/docs/archive/GETTING_STARTED.md` | `/docs/GETTING_STARTED.md` | Previous getting started guide |
| `/docs/archive/FRAMEWORK_ARCHITECTURE.md` | `/docs/FRAMEWORK_ARCHITECTURE.md` | Previous architecture documentation |
| `/docs/archive/API_FLOW_AND_LIFECYCLE.md` | `/docs/API_FLOW_AND_LIFECYCLE.md` | Previous API lifecycle documentation |
| `/docs/archive/...` | `/docs/...` | All other previous implementation docs |

## Why This Change Was Made

### Problems with Previous Structure
1. **Development Reality Mismatch**: Current implementation docs described features that don't work
2. **Planning Buried**: Critical development planning documents were hidden in subdirectory
3. **Confusion**: New contributors couldn't distinguish between wishful documentation and reality
4. **Maintenance Overhead**: Maintaining docs for broken features wastes resources

### Benefits of New Structure
1. **Clear Focus**: Root documentation now focuses on realistic development planning
2. **Honest Assessment**: Documentation acknowledges current state (95% incomplete)
3. **Actionable Plans**: Detailed roadmap and sprint plans for achieving feature parity
4. **Resource Allocation**: Clear team structure and budget for 6-month development cycle
5. **Preserved History**: All previous documentation preserved in archive for reference

## Impact on Links and References

### Internal Repository Links
- **Links to old docs**: Many internal links in code and other documents may be broken
- **Status**: Requires systematic update of all cross-references
- **Priority**: Medium (affects developer experience)

### External Links
- **GitHub URLs**: External links to specific documentation files may be broken
- **Status**: Cannot be automatically updated
- **Mitigation**: Old files preserved in archive/ with same names

### Action Items for Contributors
1. **Update Internal Links**: Scan codebase for references to old documentation paths
2. **Check CI/CD**: Verify build processes don't reference old documentation paths
3. **Update Bookmarks**: Personal bookmarks may need updating
4. **Review Dependencies**: Check if any tooling depends on old documentation structure

## Finding Specific Documentation

### For Current Implementation Information
- **Location**: `/docs/archive/`
- **Purpose**: Reference current (limited) implementation details
- **Note**: Much of this documentation describes aspirational features, not working functionality

### For Development Planning
- **Location**: `/docs/` (root level)
- **Purpose**: Understand development roadmap, team structure, and technical requirements
- **Note**: This is the active documentation for the 6-month development project

### For Quick Reference

| Looking For | Check Here | Notes |
|-------------|------------|-------|
| How to install/run CovetPy | `/docs/archive/GETTING_STARTED.md` | Limited functionality |
| Current API documentation | `/docs/archive/API_REFERENCE.md` | Many features don't work |
| Development roadmap | `/docs/ROADMAP.md` | NEW: Active planning document |
| Team and budget info | `/docs/TEAM_STRUCTURE.md` | NEW: Resource planning |
| Technical requirements | `/docs/TECHNICAL_REQUIREMENTS.md` | NEW: Development specifications |
| Architecture plans | `/docs/ARCHITECTURE_DESIGN.md` | NEW: Future architecture |

## Questions or Issues?

If you encounter broken links or need help finding specific documentation:

1. **Check Archive First**: Most old documentation is preserved in `/docs/archive/`
2. **Search Repository**: Use GitHub's search to find moved content
3. **Create Issue**: Open a GitHub issue for broken links or missing documentation
4. **Ask Community**: Use Discord or Stack Overflow with the `covet` tag

## Migration Date

- **Completed**: January 2025
- **Performed By**: DevOps Architecture Team
- **Reason**: Focus shift from aspirational documentation to realistic development planning

---

This migration aligns documentation with project reality and provides clear development direction for achieving feature parity with FastAPI and Flask over the next 6 months.