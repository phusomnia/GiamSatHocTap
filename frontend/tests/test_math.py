# tests/unit/test_math.py
import pytest
import math
from scipy import stats
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from frontend.SharedKernel.math.Probability import Bernoulli, Gaussian


def test_bernoulli_pmf_so_sánh_với_scipy():
    """Test Bernoulli PMF so sánh với scipy.stats implementation"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    p = 0.7
    bernoulli = Bernoulli(p)
    scipy_bernoulli = stats.bernoulli(p)

    custom_pmf_1 = bernoulli.pmf(1)
    scipy_pmf_1 = scipy_bernoulli.pmf(1)
    custom_pmf_0 = bernoulli.pmf(0)
    scipy_pmf_0 = scipy_bernoulli.pmf(0)

    print(f"[COMPARE] Bernoulli PMF (p={p})")
    print(f"  x=1: Custom={custom_pmf_1} | Scipy={scipy_pmf_1} | Diff={abs(custom_pmf_1 - scipy_pmf_1)}")
    print(f"  x=0: Custom={custom_pmf_0} | Scipy={scipy_pmf_0} | Diff={abs(custom_pmf_0 - scipy_pmf_0)}")
    print(f"  x=2 (invalid): Custom={bernoulli.pmf(2)} | Scipy={scipy_bernoulli.pmf(2)}")

    assert custom_pmf_1 == scipy_pmf_1
    assert custom_pmf_0 == scipy_pmf_0
    assert bernoulli.pmf(2) == 0


def test_bernoulli_mean_so_sánh_với_scipy():
    """Test Bernoulli mean so sánh với scipy.stats"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    p = 0.3
    bernoulli = Bernoulli(p)
    scipy_bernoulli = stats.bernoulli(p)

    custom_mean = bernoulli.mean()
    scipy_mean = scipy_bernoulli.mean()

    print(f"[COMPARE] Bernoulli Mean (p={p})")
    print(f"  Custom={custom_mean} | Scipy={scipy_mean} | Diff={abs(custom_mean - scipy_mean)}")

    assert custom_mean == scipy_mean


def test_bernoulli_variance_so_sánh_với_scipy():
    """Test Bernoulli variance so sánh với scipy.stats"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    p = 0.4
    bernoulli = Bernoulli(p)
    scipy_bernoulli = stats.bernoulli(p)

    custom_var = bernoulli.variance()
    scipy_var = scipy_bernoulli.var()

    print(f"[COMPARE] Bernoulli Variance (p={p})")
    print(f"  Custom={custom_var} | Scipy={scipy_var} | Diff={abs(custom_var - scipy_var)}")

    assert custom_var == scipy_var


def test_bernoulli_validation_raise_khi_p_không_hợp_lệ():
    """Test Bernoulli validation raise ValueError khi p ngoài [0,1]"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print(f"[COMPARE] Bernoulli Validation")
    print(f"  p=-0.1: Custom=raises ValueError | Scipy=raises exception")

    with pytest.raises(ValueError):
        Bernoulli(-0.1)

    with pytest.raises(ValueError):
        Bernoulli(1.1)

    print(f"  p=1.1: Custom=raises ValueError | Scipy=raises exception")


def test_bernoulli_sample_trả_về_0_hoặc_1():
    """Test Bernoulli sample chỉ trả về 0 hoặc 1"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    bernoulli = Bernoulli(0.5)
    samples = []

    for _ in range(100):
        samples.append(bernoulli.sample())

    scipy_samples = [stats.bernoulli.rvs(0.5) for _ in range(100)]

    print(f"[COMPARE] Bernoulli Sample (100 samples)")
    print(f"  Custom range: {min(samples)} to {max(samples)} | Valid: {all(s in [0,1] for s in samples)}")
    print(f"  Scipy range:  {min(scipy_samples)} to {max(scipy_samples)} | Valid: {all(s in [0,1] for s in scipy_samples)}")

    assert all(sample in [0, 1] for sample in samples)


def test_gaussian_pdf_so_sánh_với_scipy():
    """Test Gaussian PDF so sánh với scipy.stats.norm implementation"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    mu, sigma = 0, 1
    gaussian = Gaussian(mu, sigma)
    scipy_norm = stats.norm(mu, sigma)
    x_values = [-2, -1, 0, 1, 2]

    print(f"[COMPARE] Gaussian PDF (mu={mu}, sigma={sigma})")

    for x in x_values:
        custom_pdf = gaussian.PDF(x)
        scipy_pdf = scipy_norm.pdf(x)
        diff = abs(custom_pdf - scipy_pdf)
        print(f"  x={x}: Custom={custom_pdf:.10f} | Scipy={scipy_pdf:.10f} | Diff={diff:.2e}")

    for x in x_values:
        assert abs(gaussian.PDF(x) - scipy_norm.pdf(x)) < 1e-10


def test_gaussian_validation_raise_khi_sigma_không_hợp_lệ():
    """Test Gaussian validation raise ValueError khi sigma <= 0"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print(f"[COMPARE] Gaussian Validation")
    print(f"  sigma=0: Custom=raises ValueError | Scipy=raises exception")

    with pytest.raises(ValueError, match="sigma phai lon hon 0"):
        Gaussian(0, 0)

    with pytest.raises(ValueError, match="sigma phai lon hon 0"):
        Gaussian(0, -1)

    print(f"  sigma=-1: Custom=raises ValueError | Scipy=raises exception")


def test_gaussian_sample_BoxMuller_trả_về_số():
    """Test Gaussian Box-Muller sample trả về số thực"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    gaussian = Gaussian(0, 1)
    scipy_norm = stats.norm(0, 1)

    custom_samples = [gaussian.sample_BoxMuller() for _ in range(10)]

    scipy_mean = scipy_norm.mean()
    custom_mean = sum(custom_samples) / len(custom_samples)

    print(f"[COMPARE] Gaussian Box-Muller Sample (10 samples)")
    print(f"  Custom samples: {custom_samples}")
    print(f"  Custom mean: {custom_mean:.4f} | Scipy mean: {scipy_mean:.4f}")
    print(f"  Custom valid: {all(isinstance(s, (int, float)) for s in custom_samples)}")

    assert all(isinstance(sample, (int, float)) for sample in custom_samples)
    assert len(custom_samples) == 10


def test_gaussian_pdf_tại_x_bằng_mu_là_max():
    """Test Gaussian PDF tại x=mu là giá trị lớn nhất"""
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    mu, sigma = 5, 2
    gaussian = Gaussian(mu, sigma)

    pdf_at_mu = gaussian.PDF(mu)
    pdf_at_other = gaussian.PDF(mu + 1)
    scipy_pdf_at_mu = stats.norm.pdf(mu, mu, sigma)
    scipy_pdf_at_other = stats.norm.pdf(mu + 1, mu, sigma)

    print(f"[COMPARE] Gaussian PDF at x=mu (mu={mu}, sigma={sigma})")
    print(f"  x=mu={mu}: Custom={pdf_at_mu:.10f} | Scipy={scipy_pdf_at_mu:.10f}")
    print(f"  x=mu+1={mu+1}: Custom={pdf_at_other:.10f} | Scipy={scipy_pdf_at_other:.10f}")
    print(f"  Custom max at mu: {pdf_at_mu > pdf_at_other}")
    print(f"  Scipy max at mu:  {scipy_pdf_at_mu > scipy_pdf_at_other}")

    assert pdf_at_mu > pdf_at_other


def run_all_test():
    """Run all tests in this file sequentially"""
    import sys

    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    tests = [
        test_bernoulli_pmf_so_sánh_với_scipy,
        test_bernoulli_mean_so_sánh_với_scipy,
        test_bernoulli_variance_so_sánh_với_scipy,
        test_bernoulli_validation_raise_khi_p_không_hợp_lệ,
        test_bernoulli_sample_trả_về_0_hoặc_1,
        test_gaussian_pdf_so_sánh_với_scipy,
        test_gaussian_validation_raise_khi_sigma_không_hợp_lệ,
        test_gaussian_sample_BoxMuller_trả_về_số,
        test_gaussian_pdf_tại_x_bằng_mu_là_max,
    ]

    failed = []
    passed = []

    for test in tests:
        print(f"\n{'='*60}")
        try:
            test()
            passed.append(test.__name__)
            print(f"[PASS] {test.__name__}")
        except Exception as e:
            failed.append((test.__name__, str(e)))
            print(f"[FAIL] {test.__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"Passed: {len(passed)}/{len(tests)}")
    print(f"Failed: {len(failed)}/{len(tests)}")

    if failed:
        print("\nFailed tests:")
        for name, error in failed:
            print(f"  - {name}: {error}")

    return len(failed) == 0


if __name__ == "__main__":
    run_all_test()