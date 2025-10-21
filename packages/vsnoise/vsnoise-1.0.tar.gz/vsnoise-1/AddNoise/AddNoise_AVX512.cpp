#ifdef __x86_64__
#include "AddNoise.h"

template <typename pixel_t, typename noise_t>
void updateFrame_avx512(const void *_srcp, void *_dstp, const int width,
                        const int height, const ptrdiff_t stride,
                        const int noisePlane, void *_pNW,
                        const AddNoiseData *const VS_RESTRICT d) noexcept {
  auto srcp{reinterpret_cast<const pixel_t *>(_srcp)};
  auto dstp{reinterpret_cast<pixel_t *>(_dstp)};
  auto pNW{reinterpret_cast<noise_t *>(_pNW)};

  for (auto y{0}; y < height; y++) {
    for (auto x{0}; x < width; x += d->step) {
      if constexpr (std::is_same_v<pixel_t, uint8_t>) {
        Vec64c sign{-0x80};
        auto val{Vec64c().load_a(srcp + x)};
        auto nz{Vec64c().load(pNW + x)};
        val ^= sign;
        val = add_saturated(val, nz);
        val ^= sign;
        val.store_nt(dstp + x);
      } else if constexpr (std::is_same_v<pixel_t, uint16_t>) {
        Vec32s sign{-0x8000};
        auto val{Vec32s().load_a(srcp + x)};
        auto nz{Vec32s().load(pNW + x)};
        val ^= sign;
        val = add_saturated(val, nz);
        val ^= sign;
        min(Vec32us(val), d->peak).store_nt(dstp + x);
      } else {
        auto val{Vec16f().load_a(srcp + x)};
        auto nz{Vec16f().load(pNW + x)};
        (val + nz).store_nt(dstp + x);
      }
    }

    srcp += stride;
    dstp += stride;
    pNW += d->nStride[noisePlane];
  }
}

template void updateFrame_avx512<uint8_t, int8_t>(
    const void *_srcp, void *_dstp, const int width, const int height,
    const ptrdiff_t stride, const int noisePlane, void *_pNW,
    const AddNoiseData *const VS_RESTRICT d) noexcept;
template void updateFrame_avx512<uint16_t, int16_t>(
    const void *_srcp, void *_dstp, const int width, const int height,
    const ptrdiff_t stride, const int noisePlane, void *_pNW,
    const AddNoiseData *const VS_RESTRICT d) noexcept;
template void updateFrame_avx512<float, float>(
    const void *_srcp, void *_dstp, const int width, const int height,
    const ptrdiff_t stride, const int noisePlane, void *_pNW,
    const AddNoiseData *const VS_RESTRICT d) noexcept;
#endif
