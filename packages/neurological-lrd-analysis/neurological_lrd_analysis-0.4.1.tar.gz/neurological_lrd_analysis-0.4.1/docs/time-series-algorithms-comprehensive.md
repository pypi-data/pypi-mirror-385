# Comprehensive Algorithms for Time Series Data Generation in Biomedicine and Neuroscience

## Table of Contents
1. [Fractional Gaussian Models (fGn/fBm/mBm)](#fractional-gaussian-models)
2. [Multifractal Cascade Models](#multifractal-cascade-models)
3. [ARFIMA Models](#arfima-models)
4. [Renewal/CTRW and Lévy Processes](#renewal-ctrw-levy-processes)
5. [Implementation Notes](#implementation-notes)
6. [Usage Examples](#usage-examples)

## Fractional Gaussian Models

### 1.1 Circulant Embedding Algorithm (Davies-Harte Method)

**Complexity:** O(N log N)  
**Best for:** Fast generation of fGn/fBm with any Hurst parameter

```python
def circulant_embedding_fgn(H, N, sigma=1.0):
    """
    Generate fractional Gaussian noise using circulant embedding
    
    Parameters:
    H: Hurst parameter (0 < H < 1)
    N: Length of time series
    sigma: Standard deviation
    
    Returns:
    fgn: Fractional Gaussian noise sequence
    """
    # Step 1: Compute autocovariance function
    def autocovariance(k):
        if k == 0:
            return sigma**2
        return (sigma**2 / 2) * (abs(k + 1)**(2*H) + abs(k - 1)**(2*H) - 2 * abs(k)**(2*H))
    
    # Step 2: Build circulant embedding
    cov_seq = np.array([autocovariance(k) for k in range(N)])
    circulant_row = np.concatenate([cov_seq, cov_seq[1:-1][::-1]])
    
    # Step 3: Compute eigenvalues via FFT
    eigenvalues = np.real(fft(circulant_row))
    eigenvalues = np.maximum(eigenvalues, 1e-12)  # Ensure non-negative
    
    # Step 4: Generate complex Gaussian noise
    M = len(eigenvalues)
    Z = np.random.normal(0, 1, M) + 1j * np.random.normal(0, 1, M)
    Z[0] = np.real(Z[0])  # DC component must be real
    if M % 2 == 0:
        Z[M//2] = np.real(Z[M//2])  # Nyquist frequency must be real
    
    # Step 5: Apply square root filter
    Y = Z * np.sqrt(eigenvalues / 2)
    
    # Step 6: Inverse FFT
    fgn = np.real(ifft(Y))[:N]
    
    return fgn

def generate_fbm(H, N, sigma=1.0):
    """Generate fractional Brownian motion"""
    fgn = circulant_embedding_fgn(H, N, sigma)
    fbm = np.cumsum(fgn)
    return fbm
```

### 1.2 Hosking's Method

**Complexity:** O(N²)  
**Best for:** High precision, theoretical accuracy

```python
def hosking_fgn(H, N, sigma=1.0):
    """
    Generate fGn using Hosking's recursive method
    """
    def autocovariance(k):
        if k == 0:
            return sigma**2
        return (sigma**2 / 2) * (abs(k + 1)**(2*H) + abs(k - 1)**(2*H) - 2 * abs(k)**(2*H))
    
    fgn = np.zeros(N)
    phi = np.zeros((N, N))
    v = np.ones(N) * sigma**2
    
    fgn[0] = np.random.normal(0, sigma)
    
    for k in range(1, N):
        # Compute prediction coefficient
        phi[k, k] = autocovariance(k)
        for j in range(1, k):
            phi[k, k] -= phi[k-1, j] * autocovariance(k-j)
        phi[k, k] /= v[k-1]
        
        # Update coefficients
        for j in range(1, k):
            phi[k, j] = phi[k-1, j] - phi[k, k] * phi[k-1, k-j]
        
        # Update variance
        v[k] = v[k-1] * (1 - phi[k, k]**2)
        
        # Generate next value
        prediction = sum(phi[k, j] * fgn[k-j] for j in range(1, k+1))
        fgn[k] = prediction + np.sqrt(v[k]) * np.random.normal(0, 1)
    
    return fgn
```

### 1.3 Multifractional Brownian Motion

```python
def generate_multifractional_bm(H_function, N, T=1.0):
    """
    Generate multifractional Brownian motion with time-varying Hurst parameter
    
    Parameters:
    H_function: Function H(t) returning Hurst parameter at time t
    N: Number of time points
    T: Total time
    """
    t = np.linspace(0, T, N)
    mbm = np.zeros(N)
    segment_length = max(1, N // 20)
    
    for i in range(0, N, segment_length//2):
        end_idx = min(i + segment_length, N)
        t_segment = t[i:end_idx]
        local_H = np.mean([H_function(ti) for ti in t_segment])
        local_H = np.clip(local_H, 0.01, 0.99)
        
        # Generate local fBm segment
        local_fgn = circulant_embedding_fgn(local_H, end_idx - i)
        local_fbm = np.cumsum(local_fgn)
        
        # Smooth connection
        if i == 0:
            mbm[i:end_idx] = local_fbm
        else:
            mbm[i:end_idx] = local_fbm + mbm[i-1] - local_fbm[0]
    
    return mbm
```

## Multifractal Cascade Models

### 2.1 Binomial Multiplicative Cascade

```python
def binomial_cascade(N, n_scales, m1=0.3, m2=0.7, p=0.5):
    """
    Generate binomial multiplicative cascade
    
    Parameters:
    N: Final resolution
    n_scales: Number of cascade scales
    m1, m2: Multiplicative weights (should sum to 1)
    p: Probability of choosing m1
    """
    measure = np.ones(1)
    
    for scale in range(n_scales):
        new_measure = []
        for val in measure:
            if np.random.random() < p:
                w1, w2 = m1, m2
            else:
                w1, w2 = m2, m1
            new_measure.extend([val * w1, val * w2])
        measure = np.array(new_measure)
    
    # Interpolate to desired resolution
    n_final = len(measure)
    if n_final >= N:
        cascade = measure[:N]
    else:
        indices = np.linspace(0, n_final-1, N)
        cascade = np.interp(indices, range(n_final), measure)
    
    return cascade
```

### 2.2 Log-Normal Cascade

```python
def lognormal_cascade(N, n_multipliers, sigma=0.2):
    """
    Generate log-normal multiplicative cascade
    
    Parameters:
    N: Length of output series
    n_multipliers: Number of random multipliers to apply
    sigma: Standard deviation of log-normal distribution
    """
    measure = np.ones(N)
    
    # Generate random time-scale grid
    time_positions = np.random.uniform(0, 1, n_multipliers)
    scales = np.random.exponential(1.0, n_multipliers)
    scales = np.clip(scales, 1.0 / N, 0.5)
    
    # Log-normal multipliers (mean-corrected)
    mu = -sigma**2 / 2  # Ensures E[exp(X)] = 1
    multipliers = np.exp(np.random.normal(mu, sigma, n_multipliers))
    
    # Apply cascade
    t_grid = np.linspace(0, 1, N)
    
    for i in range(n_multipliers):
        t_center = time_positions[i]
        scale = scales[i]
        mult = multipliers[i]
        
        # Apply multiplier to influenced region
        influence_mask = np.abs(t_grid - t_center) <= scale / 2
        measure[influence_mask] *= mult
    
    return measure
```

### 2.3 P-Model Cascade

```python
def p_model_cascade(N, p=0.7):
    """
    Generate deterministic p-model cascade
    
    Parameters:
    N: Final length (should be power of 2)
    p: Splitting parameter (0 < p < 1)
    """
    n_levels = int(np.log2(N))
    field = np.ones(2**n_levels)
    
    for level in range(n_levels):
        field_size = len(field)
        new_field = np.zeros(field_size * 2)
        
        for i in range(field_size):
            new_field[2*i] = field[i] * p
            new_field[2*i + 1] = field[i] * (1 - p)
        
        field = new_field
    
    return field[:N]
```

## ARFIMA Models

### 3.1 FFT-Based ARFIMA Generation

```python
def generate_arfima_fft(N, d, ar_params=None, ma_params=None, sigma=1.0):
    """
    Generate ARFIMA process using FFT method
    
    Parameters:
    N: Length of time series
    d: Fractional differencing parameter (-0.5 < d < 0.5)
    ar_params: Autoregressive parameters
    ma_params: Moving average parameters
    sigma: Innovation standard deviation
    """
    if ar_params is None:
        ar_params = []
    if ma_params is None:
        ma_params = []
    
    # Generate white noise
    innovations = np.random.normal(0, sigma, 2*N)
    
    # Frequency grid
    frequencies = np.fft.fftfreq(2*N, 1.0)
    frequencies[0] = 1e-10  # Avoid division by zero
    
    # Fractional differencing filter
    frac_filter = np.abs(2 * np.sin(np.pi * frequencies))**(-d)
    frac_filter[0] = 1.0
    
    # AR filter
    if ar_params:
        z = np.exp(-2j * np.pi * frequencies)
        ar_poly = np.poly1d([1] + [-p for p in ar_params])
        ar_response = ar_poly(z)
        ar_filter = 1.0 / np.abs(ar_response)
    else:
        ar_filter = np.ones_like(frequencies)
    
    # MA filter
    if ma_params:
        z = np.exp(-2j * np.pi * frequencies)
        ma_poly = np.poly1d([1] + list(ma_params))
        ma_response = ma_poly(z)
        ma_filter = np.abs(ma_response)
    else:
        ma_filter = np.ones_like(frequencies)
    
    # Combined filter
    total_filter = frac_filter * ar_filter * ma_filter
    
    # Apply filter
    fft_innovations = np.fft.fft(innovations)
    fft_filtered = fft_innovations * total_filter
    filtered_series = np.real(np.fft.ifft(fft_filtered))
    
    return filtered_series[:N]
```

### 3.2 Direct ARFIMA Simulation

```python
def generate_arfima_direct(N, d, ar_params=None, ma_params=None, sigma=1.0):
    """
    Generate ARFIMA using direct recursive approach
    """
    if ar_params is None:
        ar_params = []
    if ma_params is None:
        ma_params = []
    
    # Fractional differencing coefficients
    def frac_diff_coeffs(d, max_k):
        coeffs = np.zeros(max_k + 1)
        coeffs[0] = 1.0
        for k in range(1, max_k + 1):
            coeffs[k] = coeffs[k-1] * (d - k + 1) / k
        return coeffs
    
    N_extended = N + 1000  # Burn-in
    innovations = np.random.normal(0, sigma, N_extended)
    
    max_coeff = min(500, N_extended - 1)
    frac_coeffs = frac_diff_coeffs(d, max_coeff)
    
    x = np.zeros(N_extended)
    
    for t in range(N_extended):
        # AR part
        ar_sum = 0
        for i, phi in enumerate(ar_params):
            if t - i - 1 >= 0:
                ar_sum += phi * x[t - i - 1]
        
        # Fractional integration (MA∞)
        frac_sum = 0
        for k in range(min(t + 1, len(frac_coeffs))):
            if t - k >= 0:
                frac_sum += frac_coeffs[k] * innovations[t - k]
        
        # MA part
        ma_sum = 0
        for j, theta in enumerate(ma_params):
            if t - j - 1 >= 0:
                ma_sum += theta * innovations[t - j - 1]
        
        x[t] = ar_sum + frac_sum + ma_sum
    
    return x[1000:]  # Remove burn-in
```

## Renewal/CTRW and Lévy Processes

### 4.1 Renewal Process Generation

```python
def generate_renewal_process(T, waiting_dist='exponential', **params):
    """
    Generate renewal process with specified waiting time distribution
    
    Parameters:
    T: Total time
    waiting_dist: 'exponential', 'gamma', 'weibull', 'lognormal', 'pareto'
    **params: Distribution parameters
    """
    events = []
    current_time = 0.0
    
    while current_time < T:
        if waiting_dist == 'exponential':
            rate = params.get('rate', 1.0)
            waiting_time = np.random.exponential(1.0 / rate)
        elif waiting_dist == 'gamma':
            shape = params.get('shape', 2.0)
            scale = params.get('scale', 1.0)
            waiting_time = np.random.gamma(shape, scale)
        elif waiting_dist == 'weibull':
            shape = params.get('shape', 1.5)
            scale = params.get('scale', 1.0)
            waiting_time = scale * np.random.weibull(shape)
        elif waiting_dist == 'lognormal':
            mu = params.get('mu', 0.0)
            sigma = params.get('sigma', 1.0)
            waiting_time = np.random.lognormal(mu, sigma)
        elif waiting_dist == 'pareto':
            alpha = params.get('alpha', 2.5)
            scale = params.get('scale', 1.0)
            waiting_time = scale * (np.random.pareto(alpha) + 1)
        
        current_time += waiting_time
        if current_time <= T:
            events.append(current_time)
    
    return events
```

### 4.2 Continuous Time Random Walk

```python
def generate_ctrw(T, N, waiting_dist='exponential', jump_dist='gaussian', 
                  waiting_params=None, jump_params=None):
    """
    Generate Continuous Time Random Walk
    
    Parameters:
    T: Total time
    N: Number of discretization points
    waiting_dist: Distribution for waiting times
    jump_dist: Distribution for jump sizes
    """
    if waiting_params is None:
        waiting_params = {'rate': 1.0}
    if jump_params is None:
        jump_params = {'mean': 0.0, 'std': 1.0}
    
    # Generate event times
    events = generate_renewal_process(T, waiting_dist, **waiting_params)
    n_jumps = len(events)
    
    # Generate jump sizes
    if jump_dist == 'gaussian':
        mean = jump_params.get('mean', 0.0)
        std = jump_params.get('std', 1.0)
        jumps = np.random.normal(mean, std, n_jumps)
    elif jump_dist == 'laplace':
        loc = jump_params.get('loc', 0.0)
        scale = jump_params.get('scale', 1.0)
        jumps = np.random.laplace(loc, scale, n_jumps)
    elif jump_dist == 'cauchy':
        loc = jump_params.get('loc', 0.0)
        scale = jump_params.get('scale', 1.0)
        jumps = stats.cauchy.rvs(loc=loc, scale=scale, size=n_jumps)
    
    # Construct CTRW process
    time_grid = np.linspace(0, T, N)
    ctrw_process = np.zeros(N)
    position = 0.0
    
    for i, event_time in enumerate(events):
        position += jumps[i]
        idx = np.searchsorted(time_grid, event_time)
        if idx < N:
            ctrw_process[idx:] = position
    
    return ctrw_process, events, jumps
```

### 4.3 Brownian Motion and Gaussian Processes

```python
def generate_brownian_motion(T, N, sigma=1.0):
    """Generate standard Brownian motion"""
    dt = T / N
    increments = np.random.normal(0, sigma * np.sqrt(dt), N)
    return np.cumsum(increments)

def generate_ornstein_uhlenbeck(T, N, theta=1.0, mu=0.0, sigma=1.0):
    """Generate Ornstein-Uhlenbeck process"""
    dt = T / N
    X = np.zeros(N)
    X[0] = mu
    
    for i in range(1, N):
        dX = theta * (mu - X[i-1]) * dt + sigma * np.sqrt(dt) * np.random.normal()
        X[i] = X[i-1] + dX
    
    return X
```

## Implementation Notes

### Computational Complexity Summary

| Algorithm | Complexity | Memory | Best Use Case |
|-----------|------------|---------|---------------|
| Circulant Embedding | O(N log N) | O(N) | Fast fGn/fBm generation |
| Hosking Method | O(N²) | O(N²) | High precision fGn |
| Cholesky Decomposition | O(N³) | O(N²) | Small N, exact covariance |
| ARFIMA FFT | O(N log N) | O(N) | Long-memory processes |
| ARFIMA Direct | O(N·K) | O(N) | Parameter control |
| Binomial Cascade | O(N·S) | O(N) | Simple multifractals |
| Log-normal Cascade | O(N·M) | O(N) | Realistic multifractals |

Where:
- N = time series length
- K = truncation order for ARFIMA
- S = number of cascade scales
- M = number of multipliers

### Parameter Guidelines

#### Fractional Gaussian Models
- **Hurst Parameter H:**
  - H < 0.5: Anti-persistent (negatively correlated increments)
  - H = 0.5: Standard Brownian motion (uncorrelated increments)
  - H > 0.5: Persistent (positively correlated increments)
  - Typical biomedical range: 0.5 ≤ H ≤ 0.9

#### ARFIMA Models
- **Fractional Parameter d:**
  - d ∈ (-0.5, 0): Stationary, anti-persistent
  - d = 0: Short memory (ARMA)
  - d ∈ (0, 0.5): Stationary, long memory
  - Typical biomedical range: 0 ≤ d ≤ 0.4

#### Multifractal Cascades
- **Log-normal σ:** Controls intermittency (0.1 ≤ σ ≤ 0.5)
- **P-model p:** Asymmetry parameter (0.5 ≤ p ≤ 0.8)
- **Binomial weights:** Should satisfy conservation (m₁ + m₂ = 1)

### Limitations and Considerations

1. **Lévy Stable Generation:** Complex numerical implementation; use specialized libraries for production
2. **Memory Requirements:** Cholesky method scales as O(N²) in memory
3. **Boundary Effects:** Circulant embedding may have edge artifacts
4. **Parameter Estimation:** Generated series should be validated against theoretical properties
5. **Numerical Stability:** Use appropriate precision for small/large parameter values

## Usage Examples

### Example 1: Heart Rate Variability Simulation

```python
# Generate HRV-like signal using ARFIMA
N = 1000  # 1000 RR intervals
d = 0.15  # Long-range dependence
ar_params = [0.3]  # Short-term correlation
sigma = 50  # Physiological variation (ms)

hrv_series = generate_arfima_fft(N, d, ar_params=ar_params, sigma=sigma)
# Add physiological mean
hrv_series += 800  # Mean RR interval ~800ms
```

### Example 2: EEG-like Multifractal Signal

```python
# Generate multifractal cascade for neural activity
N = 2048  # 2048 samples
n_scales = 10
sigma = 0.25  # Moderate intermittency

eeg_like = lognormal_cascade(N, N, sigma)
# Normalize to typical EEG amplitude range
eeg_like = (eeg_like - np.mean(eeg_like)) / np.std(eeg_like) * 50  # μV
```

### Example 3: Anomalous Diffusion in Tissue

```python
# Generate subdiffusive motion
T = 100.0  # seconds
N = 10000  # time points

# Power-law waiting times (subdiffusion)
events = generate_renewal_process(T, 'pareto', alpha=1.8, scale=0.1)

# Gaussian displacements
n_events = len(events)
displacements = np.random.normal(0, 1.0, n_events)

# Construct trajectory
trajectory = np.cumsum(displacements)
```

### Example 4: Time-Varying Hurst Parameter

```python
# Simulate non-stationary neural signal
def varying_hurst(t):
    return 0.5 + 0.3 * np.sin(2 * np.pi * t / 10)**2

N = 1024
mbm_signal = generate_multifractional_bm(varying_hurst, N, T=20.0)
```

## References and Further Reading

1. **Fractional Brownian Motion:**
   - Mandelbrot, B.B. & Van Ness, J.W. (1968). Fractional Brownian motions, fractional noises and applications. SIAM Review, 10(4), 422-437.
   - Davies, R.B. & Harte, D.S. (1987). Tests for Hurst effect. Biometrika, 74(1), 95-101.

2. **ARFIMA Processes:**
   - Granger, C.W.J. & Joyeux, R. (1980). An introduction to long‐memory time series models and fractional differencing. Journal of Time Series Analysis, 1(1), 15-29.
   - Hosking, J.R.M. (1981). Fractional differencing. Biometrika, 68(1), 165-176.

3. **Multifractal Cascades:**
   - Mandelbrot, B.B. (1974). Intermittent turbulence in self-similar cascades: divergence of high moments and dimension of the carrier. Journal of Fluid Mechanics, 62(2), 331-358.
   - Muzy, J.F., Bacry, E. & Arneodo, A. (1991). Wavelets and multifractal formalism for singular signals. Physical Review Letters, 67(25), 3515-3518.

4. **Renewal and CTRW:**
   - Montroll, E.W. & Weiss, G.H. (1965). Random walks on lattices. II. Journal of Mathematical Physics, 6(2), 167-181.
   - Metzler, R. & Klafter, J. (2000). The random walk's guide to anomalous diffusion: a fractional dynamics approach. Physics Reports, 339(1), 1-77.

5. **Biomedical Applications:**
   - Goldberger, A.L. et al. (2002). What is physiologic complexity and how does it change with aging and disease? Neurobiology of Aging, 23(1), 23-26.
   - Ivanov, P.C. et al. (1999). Multifractality in human heartbeat dynamics. Nature, 399(6735), 461-465.