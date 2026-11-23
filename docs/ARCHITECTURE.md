# Technical & Mathematical Architecture Document
**Project 2: Privacy-Preserving Federated Swarm Intelligence**  
**Company:** Zaalima Development Pvt. Ltd. | SOP Version 1.1 Compliance  

---

## 1. System Topology Overview

```
                         +-----------------------------------+
                         |      Central Coordinator          |
                         |   (Zero-Knowledge Evaluator)      |
                         +-----------------+-----------------+
                                           |
                                  Encrypted Ciphertexts
                                  (Without Server Key)
                                           |
                   +-----------------------+-----------------------+
                   |                       |                       |
        +----------v----------+ +----------v----------+ +----------v----------+
        |  Edge Node (Mobile) | |  Edge Node (Sensor) | | Edge Node (Gateway) |
        |  Local Non-IID Data | |  Local Non-IID Data | | Local Non-IID Data  |
        |  • Local SGD Loop   | |  • Local SGD Loop   | | • Local SGD Loop    |
        |  • L2 Gradient Clip | |  • L2 Gradient Clip | | • L2 Gradient Clip  |
        |  • Gaussian DP      | |  • Gaussian DP      | | • Gaussian DP       |
        |  • INT8 Top-K Comp  | |  • INT8 Top-K Comp  | | • INT8 Top-K Comp   |
        |  • FHE Encryption   | |  • FHE Encryption   | | • FHE Encryption    |
        +---------------------+ +---------------------+ +---------------------+
```

---

## 2. Mathematical Formulations

### 2.1 Fully Homomorphic & Additively Homomorphic Encryption (FHE/AHE)
Let $p, q$ be large prime numbers, $n = p \cdot q$, and $\lambda = \text{lcm}(p - 1, q - 1)$.  
The generator $g = n + 1$, and $\mu = (L(g^\lambda \bmod n^2))^{-1} \bmod n$, where $L(u) = \frac{u - 1}{n}$.

For a real-valued model parameter update $\Delta w \in \mathbb{R}$, fixed-point quantization with scale factor $S = 10^4$ maps the float to an integer:
$$m = \text{round}(\Delta w \cdot S) \pmod n$$

**Encryption:**
$$c = g^m \cdot r^n \pmod{n^2}, \quad r \in \mathbb{Z}_n^*$$

**Homomorphic Addition (Ciphertext Multiplication):**
$$c_{\text{sum}} = \prod_{k=1}^K c_k \pmod{n^2}$$
When decrypted:
$$\text{Dec}(c_{\text{sum}}) = \sum_{k=1}^K m_k \pmod n$$

**Zero-Knowledge Privacy:**
The central aggregator only evaluates $c_{\text{sum}}$ via modular arithmetic. Because the aggregator does not hold the private key $(\lambda, \mu)$, the ciphertexts $c_k$ are statistically indistinguishable from uniform random noise over $\mathbb{Z}_{n^2}^*$.

---

### 2.2 Differential Privacy (DP) & Moments Accountant
To defend against Membership Inference Attacks (MIA):

1. **$L_2$ Sensitivity Bounding (Clipping):**
$$g_k \leftarrow \frac{g_k}{\max\left(1, \frac{\|g_k\|_2}{C}\right)}, \quad C = 1.0$$

2. **Calibrated Gaussian Perturbation:**
$$\tilde{g}_k = g_k + \mathcal{N}\left(0, \sigma^2 C^2 I\right), \quad \sigma = \frac{\sqrt{2 \ln(1.25 / \delta)}}{\epsilon}$$

3. **Cumulative Privacy Composition:**
Using the Rényi Moments Accountant across $T$ rounds with client subsampling ratio $q = \frac{|S|}{N}$:
$$\epsilon_{\text{total}} \approx \frac{q \sqrt{2 T \ln(1 / \delta)}}{\sigma} + \frac{T q^2}{\sigma^2}$$

---

### 2.3 Non-IID Dirichlet Data Fragmentation
Sensory datasets are partitioned using a Dirichlet distribution $\text{Dir}(\alpha \cdot \mathbf{1})$:
$$p_c \sim \text{Dir}(\alpha), \quad \alpha = 0.3$$
Lower $\alpha$ values yield heavy class imbalance (high Non-IID skew), simulating real-world decentralized environments where individual devices observe only a subset of sensory classes.

---

### 2.4 Byzantine Fault Tolerance (BFT) Multi-Krum Protocol
Given $n$ candidate updates $\{v_1, \dots, v_n\}$ with at most $f$ Byzantine rogue workers:

For each vector $v_i$, compute the distance score to its $n - f - 2$ closest Euclidean neighbors:
$$S(i) = \sum_{j \in \mathcal{N}_{n - f - 2}(i)} \|v_i - v_j\|_2^2$$

Multi-Krum iteratively selects the $m = n - 2f$ vectors with the lowest scores:
$$v_{\text{consensus}} = \frac{1}{m} \sum_{i \in \text{Selected}} v_i$$
Outlier vectors (poisoned gradients from sign-flipping or scale attacks) yield high distance scores and are automatically dropped.
