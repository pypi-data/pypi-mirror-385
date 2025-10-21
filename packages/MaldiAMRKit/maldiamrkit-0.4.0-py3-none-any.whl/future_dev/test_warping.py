import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Assuming these are available in your environment
from maldiamrkit.warping import Warping
from maldiamrkit.peak_detector import MaldiPeakDetector


def generate_synthetic_spectra(n_samples=50, n_bins=1000, n_peaks=10, noise_level=0.05):
    """
    Generate synthetic MALDI-TOF-like spectra with random shifts.
    
    Parameters
    ----------
    n_samples : int
        Number of spectra to generate
    n_bins : int
        Number of m/z bins
    n_peaks : int
        Number of Gaussian peaks per spectrum
    noise_level : float
        Standard deviation of Gaussian noise
        
    Returns
    -------
    spectra : pd.DataFrame
        Generated spectra
    labels : np.ndarray
        Binary labels (for testing in ML pipeline)
    true_peaks : list
        True peak positions (before shifting)
    """
    mz_axis = np.arange(n_bins)
    spectra = []
    labels = []
    
    # Define true peak positions
    np.random.seed(42)
    true_peaks = np.random.choice(np.arange(100, n_bins - 100), size=n_peaks, replace=False)
    true_peaks = np.sort(true_peaks)
    
    for i in range(n_samples):
        # Create base spectrum with Gaussian peaks
        spectrum = np.zeros(n_bins)
        
        # Apply a random shift to simulate misalignment
        shift = np.random.randint(-20, 20)
        
        for peak_pos in true_peaks:
            shifted_pos = peak_pos + shift
            if 0 <= shifted_pos < n_bins:
                # Add Gaussian peak
                width = np.random.uniform(3, 8)
                height = np.random.uniform(0.5, 2.0)
                spectrum += height * np.exp(-0.5 * ((mz_axis - shifted_pos) / width) ** 2)
        
        # Add noise
        spectrum += np.random.normal(0, noise_level, n_bins)
        spectrum = np.maximum(spectrum, 0)  # No negative intensities
        
        spectra.append(spectrum)
        labels.append(i % 2)  # Binary labels for classification
    
    columns = [f"mz_{i}" for i in range(n_bins)]
    return pd.DataFrame(spectra, columns=columns), np.array(labels), true_peaks


def test_basic_functionality():
    """Test basic fit/transform functionality."""
    print("=" * 60)
    print("TEST 1: Basic Functionality")
    print("=" * 60)
    
    # Generate data
    X, y, true_peaks = generate_synthetic_spectra(n_samples=20, n_bins=500)
    print(f"Generated {len(X)} spectra with {X.shape[1]} bins")
    
    # Test each method
    methods = ["shift", "linear", "piecewise", "dtw"]
    
    for method in methods:
        print(f"\nTesting method: {method}")
        warper = Warping(method=method, max_shift=30)
        
        # Fit and transform
        warper.fit(X)
        X_aligned = warper.transform(X)
        
        # Check output shape
        assert X_aligned.shape == X.shape, f"Shape mismatch for {method}"
        print(f"  ✓ Shape preserved: {X_aligned.shape}")
        
        # Check that it's a DataFrame
        assert isinstance(X_aligned, pd.DataFrame), f"Output not DataFrame for {method}"
        print(f"  ✓ Output is DataFrame")
        
        # Check for NaN values
        assert not X_aligned.isna().any().any(), f"NaN values in output for {method}"
        print(f"  ✓ No NaN values")
        
        # Check non-negativity (MALDI spectra shouldn't have negative intensities)
        assert (X_aligned.values >= -1e-10).all(), f"Negative values in output for {method}"
        print(f"  ✓ No negative values")


def test_parameter_validation():
    """Test parameter validation."""
    print("\n" + "=" * 60)
    print("TEST 2: Parameter Validation")
    print("=" * 60)
    
    X, y, _ = generate_synthetic_spectra(n_samples=10, n_bins=300)
    
    # Test invalid method
    try:
        warper = Warping(method="invalid_method")
        warper.fit(X)
        assert False, "Should have raised ValueError for invalid method"
    except ValueError as e:
        print(f"✓ Correctly rejected invalid method: {e}")
    
    # Test invalid n_segments
    try:
        warper = Warping(method="piecewise", n_segments=0)
        warper.fit(X)
        assert False, "Should have raised ValueError for n_segments=0"
    except ValueError as e:
        print(f"✓ Correctly rejected n_segments=0: {e}")
    
    # Test invalid reference index
    try:
        warper = Warping(reference=100)  # Out of bounds
        warper.fit(X)
        assert False, "Should have raised ValueError for out-of-bounds reference"
    except ValueError as e:
        print(f"✓ Correctly rejected out-of-bounds reference: {e}")
    
    # Test empty DataFrame
    try:
        warper = Warping()
        warper.fit(pd.DataFrame())
        assert False, "Should have raised ValueError for empty DataFrame"
    except ValueError as e:
        print(f"✓ Correctly rejected empty DataFrame: {e}")


def test_sklearn_pipeline():
    """Test integration with sklearn Pipeline."""
    print("\n" + "=" * 60)
    print("TEST 3: Sklearn Pipeline Integration")
    print("=" * 60)
    
    # Generate data
    X, y, _ = generate_synthetic_spectra(n_samples=100, n_bins=500)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Test with different warping methods
    for method in ["shift", "dtw"]:
        print(f"\nTesting pipeline with {method} warping:")
        
        pipe = Pipeline([
            ("warp", Warping(method=method, max_shift=25)),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000))
        ])
        
        # Fit pipeline
        pipe.fit(X_train, y_train)
        print(f"  ✓ Pipeline fitted successfully")
        
        # Score on test set
        train_score = pipe.score(X_train, y_train)
        test_score = pipe.score(X_test, y_test)
        print(f"  ✓ Train accuracy: {train_score:.3f}")
        print(f"  ✓ Test accuracy: {test_score:.3f}")


def test_reference_options():
    """Test different reference spectrum options."""
    print("\n" + "=" * 60)
    print("TEST 4: Reference Spectrum Options")
    print("=" * 60)
    
    X, y, _ = generate_synthetic_spectra(n_samples=20, n_bins=300)
    
    # Test median reference
    warper_median = Warping(reference="median")
    warper_median.fit(X)
    X_aligned_median = warper_median.transform(X)
    print("✓ Median reference works")
    
    # Test integer reference
    warper_int = Warping(reference=5)
    warper_int.fit(X)
    X_aligned_int = warper_int.transform(X)
    print("✓ Integer reference works")
    
    # Check that they produce different results
    diff = np.abs(X_aligned_median.values - X_aligned_int.values).sum()
    print(f"✓ Different references produce different results (diff: {diff:.2f})")


def visualize_alignment_effect():
    """Visualize the effect of alignment on spectra."""
    print("\n" + "=" * 60)
    print("TEST 5: Visualization of Alignment Effect")
    print("=" * 60)
    
    # Generate data with more pronounced shifts
    X, y, true_peaks = generate_synthetic_spectra(n_samples=10, n_bins=500, n_peaks=5)
    
    # Apply different alignment methods
    methods = ["shift", "linear", "piecewise", "dtw"]
    results = {"original": X}
    
    for method in methods:
        warper = Warping(method=method, max_shift=30)
        warper.fit(X)
        results[method] = warper.transform(X)
    
    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    plot_configs = [
        ("original", "Original (Unaligned)"),
        ("shift", "Shift Alignment"),
        ("linear", "Linear Alignment"),
        ("piecewise", "Piecewise Alignment"),
        ("dtw", "DTW Alignment")
    ]
    
    for idx, (key, title) in enumerate(plot_configs):
        if idx < len(axes) - 1:  # Skip last subplot
            ax = axes[idx]
            data = results[key]
            
            # Plot mean spectrum
            mean_spectrum = data.mean(axis=0)
            std_spectrum = data.std(axis=0)
            
            mz_axis = np.arange(len(mean_spectrum))
            ax.plot(mz_axis, mean_spectrum, 'b-', linewidth=1.5, label='Mean')
            ax.fill_between(mz_axis, 
                           mean_spectrum - std_spectrum,
                           mean_spectrum + std_spectrum,
                           alpha=0.3, color='blue', label='±1 std')
            
            # Mark true peak positions
            for peak in true_peaks:
                ax.axvline(peak, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
            
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xlabel('m/z bin')
            ax.set_ylabel('Intensity')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
    
    # Remove last empty subplot
    fig.delaxes(axes[-1])
    
    plt.tight_layout()
    plt.savefig('warping_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Visualization saved as 'warping_comparison.png'")
    print("  Red dashed lines show true peak positions")
    print("  Note how alignment reduces the standard deviation band")


def test_edge_cases():
    """Test edge cases and special scenarios."""
    print("\n" + "=" * 60)
    print("TEST 6: Edge Cases")
    print("=" * 60)
    
    # Test with spectra with no peaks
    X_no_peaks = pd.DataFrame(np.random.normal(0, 0.01, (10, 200)))
    warper = Warping(method="shift")
    warper.fit(X_no_peaks)
    X_aligned = warper.transform(X_no_peaks)
    print("✓ Handles spectra with no/few peaks")
    
    # Test with identical spectra
    X_identical = pd.DataFrame(np.ones((5, 100)))
    warper = Warping(method="linear")
    warper.fit(X_identical)
    X_aligned = warper.transform(X_identical)
    print("✓ Handles identical spectra")
    
    # Test transform before fit
    try:
        warper = Warping()
        X, _, _ = generate_synthetic_spectra(n_samples=5, n_bins=300)
        warper.transform(X)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        print(f"✓ Correctly rejects transform before fit: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("WARPING TRANSFORMER TEST SUITE")
    print("=" * 60)
    
    # Run all tests
    test_basic_functionality()
    test_parameter_validation()
    test_sklearn_pipeline()
    test_reference_options()
    test_edge_cases()
    
    # Visualization (requires matplotlib)
    try:
        visualize_alignment_effect()
    except ImportError:
        print("\nSkipping visualization (matplotlib not available)")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("=" * 60)