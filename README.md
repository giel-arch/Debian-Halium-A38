# Debian + Halium 14 — Oppo A38 (CPH2579, "ossi")

Debian trixie arm64 + libhybris (Halium 14 = komposisi resmi: libhybris
`halium-13.0` + patchset `hybris-patches@halium-14.0`) di atas kernel stock
Android 14 Oppo A38 (4.19.191, semua driver builtin — tanpa modul vendor).

## Arsitektur

```
lk → kernel stock A14 (boot_b, tanpa perubahan)
   → initramfs (assets/initramfs-v13.cpio.gz — telnetd + RNDIS 172.16.42.1)
   → mount /dev/mmcblk0p59 (userdata) — cmdline systempart=
   → switch_root → Debian trixie (SSH root/ossi)
   → [fase 2] libhybris + container lxc-android (blob dari super A14)
```

- `boot_a` = stock A14 dengan recovery — jalur penyelamatan, tidak disentuh.
- `vbmeta_a/b` = pra-patch flags 3 (di repo ini, atau flash stok dengan
  `--disable-verity --disable-verification`).
- `super` (system/vendor A14) = sumber blob libhybris, tidak disentuh.

## Workflow

`Build Debian + Halium14 (Oppo A38)` menghasilkan artifact
`halium-debian-pack` berisi:

- `boot-a14-ossi.img` — kernel A14 + initramfs Halium + DTB (flash ke `boot_b`)
- `userdata.img` — rootfs Debian (flash ke `userdata`)

## Fase 2 (libhybris)

Setelah SSH hidup: build libhybris `halium-13.0` + `android-headers`
`halium-14.0` + `hybris-patches@halium-14.0`, container `lxc-android`
dari partisi system/vendor stok, backend `fbdev` → `hwcomposer2`.
