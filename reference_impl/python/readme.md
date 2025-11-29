# Resonance: Python Reference Implementation (Level 1)

This folder contains the MVP implementation of the Resonance Protocol.

## Files
- `sender.py` / `receiver.py` - The Wire Protocol demo (TCP + Protobuf).
- `alignment.py` - The Semantic Alignment algorithm (Procrustes).
- `gossip.py` - Mesh network simulation.
- `resonance.proto` - The binary contract definition.

## How to Run

1. Install dependencies:
   ```bash
   pip install sentence-transformers scipy protobuf grpcio-tools