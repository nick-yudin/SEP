# Governance Model

## Current Status

As of December 2025, the Semantic Event Protocol (SEP) is a **single-author research project** in its early experimental phase.

## Decision-Making Process

### Protocol Specification Changes

All changes to the protocol specification (Level 1 and above) follow this process:

1. **Proposal:** Open an issue or discussion describing the proposed change
2. **RFC Draft:** Create a document in `docs/rfcs/RFC-XXXX.md` with:
   - Problem statement
   - Proposed solution
   - Backward compatibility analysis
   - Implementation considerations
3. **Review Period:** Minimum 14 days for community feedback
4. **Decision:** Currently made by the project author (BDFL model)
5. **Implementation:** After approval, implementation can proceed

### Code Contributions

- All contributions must include tests where applicable
- Code style follows existing patterns in the reference implementation
- Pull requests require review before merging

### Documentation

- Documentation changes follow standard PR review process
- All public artifacts maintained in English
- Attribution required for significant contributions

## Versioning

Protocol versions follow semantic versioning:
- **Major (v2.0):** Breaking changes to wire format or core invariants
- **Minor (v1.1):** Backward-compatible additions
- **Patch (v1.0.1):** Bug fixes and clarifications

## Future Governance

As the project matures and gains contributors:

1. **Short term (1-3 contributors):** BDFL model with community input
2. **Medium term (4-10 contributors):** Technical steering committee
3. **Long term (10+ contributors):** Open governance foundation

## Communication Channels

- **Issues & PRs:** Technical discussions
- **Discussions:** General questions, ideas, research
- **Email:** 1@seprotocol.ai for private matters

## Code of Conduct

Expected behavior:
- Be respectful and constructive
- Focus on technical merit
- Welcome newcomers
- Assume good faith

Unacceptable behavior will result in removal from the project.
