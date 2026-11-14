# Slay the Spire 2 → iPhone Duo (public, code-only)

A preparation repository for a **legitimately owned Windows Steam copy of Slay the Spire 2**, using the open-source [sts2-ios port](https://github.com/jhaizhou-ops/sts2-ios) as a starting point. **No game binaries or proprietary SDKs are included.**

## Verified inputs (not included)
- Steam game version: **v0.107.1** (June 18, 2026).
- Managed assembly: `data_sts2_windows_x86_64/sts2.dll`, 9,364,480 bytes.
- Asset pack: `SlayTheSpire2.pck`, 1,901,378,340 bytes (Drive metadata; bytes not validated).
- An offline PE/.NET metadata audit found **37/37 target class/method names** from the upstream patch manifest. This does **not** validate signatures, iOS compilation, or gameplay.

## Workflow
`.github/workflows/source-preflight.yml` runs a **code-only** check on a GitHub macOS runner: verifies Xcode and .NET 9, fetches upstream public source, builds the open-source assembly weaver, and validates the patch manifest. No game content is downloaded or uploaded. It does **not** produce an IPA.

## Staging locally
With your own game files on a private machine:

```sh
python3 scripts/sts2_preflight.py '/path/to/data_sts2_windows_x86_64/sts2.dll'
python3 scripts/stage_windows_game.py '/path/to/Slay the Spire 2' '/path/to/empty-stage'
```

The staging script creates symbolic links for compatible managed assemblies under the macOS-named directory expected by the upstream CLI. This is a **layout shim**, not a Windows-to-iOS binary converter. Use its output `Resources` folder as the `STS2_GAME_APP` path on macOS only after resolving the other requirements.

## Not yet complete
A working game needs authenticated *private* staging of game assets, Godot 4.5.1 Mono + iOS templates, .NET 9, licensed iOS FMOD/Spine libraries, Xcode signing with the necessary memory entitlement, the separate large PCK file, and an actual iPhone test. Consult the [upstream build guide](https://github.com/jhaizhou-ops/sts2-ios/blob/main/AGENTS.md).

**Never add Steam game content, third-party proprietary binaries, Apple signing materials, or secrets to this public repository, including Actions artifacts.** A .gitignore file is not a security boundary.
