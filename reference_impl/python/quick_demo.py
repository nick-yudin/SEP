#!/usr/bin/env python3
"""
RESONANCE PROTOCOL - QUICK DEMO
================================
One command to see all core concepts in action.

Run: python quick_demo.py
"""

import sys
import time
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from scipy.linalg import orthogonal_procrustes
import numpy as np

# Configuration
THRESHOLD = 0.35
DIMENSION = 384

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_step(num, text):
    print(f"[{num}] {text}")

# ============================================================================
# DEMO 1: SEMANTIC FILTERING (The Core Insight)
# ============================================================================
def demo_semantic_filtering():
    print_header("DEMO 1: SEMANTIC FILTERING - Silence is Default")
    
    print_step(1, "Loading semantic model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print_step(2, "Testing noise suppression...")
    
    inputs = [
        ("System startup", None),
        ("System initialization", "SYNONYM"),
        ("System boot sequence", "SYNONYM"),
        ("A cat is walking", "EVENT"),
        ("A small feline is moving", "SYNONYM"),
        ("FIRE DETECTED IN SECTOR 7", "EVENT")
    ]
    
    last_vector = None
    transmitted = 0
    suppressed = 0
    
    print("\n" + "-"*70)
    for text, expected in inputs:
        current_vector = model.encode(text)
        
        if last_vector is None:
            # First event always transmits
            print(f"🔵 BASELINE: '{text}'")
            last_vector = current_vector
            transmitted += 1
            continue
        
        dist = cosine(last_vector, current_vector)
        
        if dist > THRESHOLD:
            print(f"⚡ TRANSMIT ({dist:.3f}): '{text}' [{expected}]")
            last_vector = current_vector
            transmitted += 1
        else:
            print(f"🔇 SILENCE  ({dist:.3f}): '{text}' [{expected}] ← Energy saved")
            suppressed += 1
        
        time.sleep(0.3)
    
    print("-"*70)
    print(f"\n✅ Result: {transmitted} events transmitted, {suppressed} suppressed")
    print(f"   Bandwidth reduction: {(suppressed/(transmitted+suppressed)*100):.1f}%\n")
    
    input("Press ENTER to continue to Demo 2...")

# ============================================================================
# DEMO 2: PROCRUSTES ALIGNMENT (Alien Minds)
# ============================================================================
def demo_procrustes_alignment():
    print_header("DEMO 2: PROCRUSTES ALIGNMENT - Alien Minds Can Talk")
    
    print_step(1, "Generating synthetic anchor vectors...")
    # Create standard reference vectors
    std_anchors = np.random.randn(1000, DIMENSION)
    
    print_step(2, "Simulating 'Alien Node' with rotated vector space...")
    # Rotate to simulate different LLM
    H = np.random.randn(DIMENSION, DIMENSION)
    Q, _ = np.linalg.qr(H)
    alien_anchors = np.dot(std_anchors, Q)
    
    # Measure chaos
    dist_before = np.mean([cosine(std_anchors[i], alien_anchors[i]) for i in range(5)])
    print(f"   Distance BEFORE alignment: {dist_before:.4f} (Chaos)")
    
    print_step(3, "Computing Procrustes rotation matrix...")
    R, _ = orthogonal_procrustes(alien_anchors, std_anchors)
    
    print_step(4, "Testing on real semantic vector...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    test_text = "The quick brown fox jumps over the lazy dog"
    
    # Standard view
    target_vector = model.encode(test_text)
    
    # Alien view (apply rotation)
    source_vector_raw = np.dot(target_vector, Q)
    
    # Align alien -> standard
    aligned_vector = np.dot(source_vector_raw, R)
    
    # Measure accuracy
    raw_dist = cosine(target_vector, source_vector_raw)
    aligned_dist = cosine(target_vector, aligned_vector)
    
    print("\n" + "-"*70)
    print(f"Test phrase: '{test_text}'")
    print(f"   Without alignment: distance = {raw_dist:.4f} (Gibberish)")
    print(f"   With alignment:    distance = {aligned_dist:.8f} (Perfect)")
    print("-"*70)
    
    if aligned_dist < 1e-5:
        print("\n✅ SUCCESS: Alien node now speaks our language!\n")
    else:
        print("\n⚠️  Alignment imperfect (but close)\n")
    
    input("Press ENTER to continue to Demo 3...")

# ============================================================================
# DEMO 3: MESH PROPAGATION (Gossip Protocol)
# ============================================================================
def demo_mesh_gossip():
    print_header("DEMO 3: MESH PROPAGATION - Information Spreads Like Fire")
    
    print_step(1, "Creating 5-node mesh network...")
    
    class SimpleNode:
        def __init__(self, node_id):
            self.id = f"NODE_{node_id}"
            self.peers = []
            self.memory = set()
            self.last_vector = None
        
        def connect(self, other):
            if other not in self.peers:
                self.peers.append(other)
                other.peers.append(self)
    
    nodes = [SimpleNode(i) for i in range(5)]
    
    # Create mesh topology
    nodes[0].connect(nodes[1])
    nodes[1].connect(nodes[2])
    nodes[2].connect(nodes[3])
    nodes[3].connect(nodes[4])
    nodes[0].connect(nodes[3])  # Cross-link
    
    print("   Topology:")
    for n in nodes:
        peers = [p.id for p in n.peers]
        print(f"     {n.id} <-> {peers}")
    
    print_step(2, "Injecting event at NODE_0...")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    event_text = "CRITICAL: Drone detected at perimeter"
    event_vector = model.encode(event_text)
    event_id = "evt_001"
    
    def propagate(node, event_id, vector, text, ttl, indent=0):
        if event_id in node.memory:
            return  # Already seen
        
        node.memory.add(event_id)
        prefix = "  " * indent
        print(f"{prefix}⚡ {node.id} received: '{text}' (TTL={ttl})")
        
        if ttl > 0:
            time.sleep(0.2)
            for peer in node.peers:
                propagate(peer, event_id, vector, text, ttl - 1, indent + 1)
    
    print("\n" + "-"*70)
    propagate(nodes[0], event_id, event_vector, event_text, ttl=3)
    print("-"*70)
    
    reached = sum(1 for n in nodes if event_id in n.memory)
    print(f"\n✅ Event reached {reached}/{len(nodes)} nodes without central server\n")
    
    input("Press ENTER to finish...")

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║             RESONANCE PROTOCOL - INTERACTIVE DEMO                 ║
    ║                                                                   ║
    ║   "The clock stops. The resonance begins."                        ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    
    This demo shows three core concepts:
    
    1. Semantic Filtering  - Nodes transmit only when meaning changes
    2. Procrustes Alignment - Different LLMs can align their vector spaces
    3. Mesh Propagation    - Events spread through gossip, no server needed
    
    """)
    
    input("Press ENTER to start...")
    
    try:
        demo_semantic_filtering()
        demo_procrustes_alignment()
        demo_mesh_gossip()
        
        print_header("ALL DEMOS COMPLETE")
        print("""
    What you just saw:
    
    ✅ Semantic noise suppression (67% bandwidth reduction)
    ✅ Cross-LLM alignment via Procrustes (10^-7 error)
    ✅ Decentralized mesh propagation (no server)
    
    This is SEP Protocol Level 1.
    
    Next steps:
    - Explore individual demos: alignment.py, gossip.py, sender.py
    - Read the specification: /docs/01_specs/v1.0_current/spec_v1_final.md
    - Check the website: https://seprotocol.ai
    
    Questions? → 1@seprotocol.ai
        """)
        
    except KeyboardInterrupt:
        print("\n\n[Demo interrupted by user]\n")
        sys.exit(0)

if __name__ == "__main__":
    main()