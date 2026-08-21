# Algorithmic Archaeological Synthesis Report
**Problem:** Single-Source Shortest Path in Weighted Directed Graphs  
**Family:** `graph`  
**Theoretical Lower Bound:** Time `O((V + E) log V)` | Space `O(V + E)`  

---

## 1. Executive Summary
Automated algorithmic archaeology completed for 'Single-Source Shortest Path in Weighted Directed Graphs'. Evaluated 4 candidate paradigms spanning theoretical bounds from O((V + E) log V) to polynomial baselines. Champion selected: 'Dijkstra Priority Queue (Min-Heap)' (Pareto Rank 1, Composite Score 82.76/100).

## 2. Theoretical vs. Empirical Scaling
The theoretical lower bound is O((V + E) log V). Empirical benchmarks verified that 'Dijkstra Priority Queue (Min-Heap)' demonstrated scaling of O(N) ~ O(N log N) with peak auxiliary memory of 1.58 MB.

## 3. Candidate Comparison Matrix
| Candidate | Paradigm | Asymptotic Time | Asymptotic Space | Accuracy | Avg Runtime | Peak Memory | Pareto Rank |
|---|---|---|---|---|---|---|---|
| Dijkstra Priority Queue (Min-Heap) | Greedy / Priority Queue | `O((V + E) log V)` | `O(V + E)` | 100.0% | 10.89 ms | 1.58 MB | 1 ⭐ |
| Naive Unit BFS (Pathological Trap) | Queue Breadth-First Search | `O(V + E)` | `O(V)` | 28.6% | 2.97 ms | 0.80 MB | 1  |
| Bidirectional Dijkstra Search | Bidirectional Frontier Expansion | `O((V + E) log V)` | `O(V + E)` | 100.0% | 33.88 ms | 3.26 MB | 2  |
| Dial's Bucket Queues | Bounded Integer Bucket Array | `O(V + E + W)` | `O(V + W)` | 100.0% | 180.37 ms | 25.75 MB | 2  |

## 4. Adversarial Failure Modes & Pathological Edge Cases
- Incorrect output on 'Simple Multi-Hop Weighted Graph': Expected 8, got 2.

## 5. Production Recommendations
For production environments, adopt 'Dijkstra Priority Queue (Min-Heap)'. It delivers deterministic worst-case bounds, immunity to adversarial graph/array topology traps, and minimal memory overhead.
