# Slay the Spire 2 → iPhone Duo (public, code-only)

## Stage 4: offline Duo IPA builder

The [Stage 3 Xcode 27 validation](.github/workflows/xcode27-duo-readiness.yml) succeeded on GitHub's Apple Silicon `xcode-27` runner. The new [Stage 4 manual workflow](.github/workflows/private-offline-ipa.yml) uses the pinned [FlyingViet offline port](https://github.com/FlyingViet/sts2-ios-launch) and `--unsigned --no-ota`. It targets the user's *already-owned* Windows Steam v0.107.1 installation. No Steam sign-in is requested on the iPhone.

**The final IPA has not been compiled.** To protect the user's private game files and keep the game-containing IPA out of public GitHub, the workflow requires separate Google Drive authentication via an encrypted Actions secret. See [private setup instructions](docs/PRIVATE_DRIVE_BUILD.md). The cloud GitHub runner cannot reuse the Google Drive connection from ChatGPT.


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
python3 scripts/sts2_preflight.py '/path/to/data_sts2_windows_x86_64/sts2.dll' '/path/to/sts2-ios/src/STS2MobileIos/manifest.json'
python3 scripts/stage_windows_game.py '/path/to/Slay the Spire 2' '/path/to/empty-stage'
```

The staging script creates symbolic links for compatible managed assemblies under the macOS-named directory expected by the upstream CLI. This is a **layout shim**, not a Windows-to-iOS binary converter. Use its output `Resources` folder as the `STS2_GAME_APP` path on macOS only after resolving the other requirements.

## Not yet complete
A working game needs authenticated *private* staging of game assets, Godot 4.5.1 Mono + iOS templates, .NET 9, licensed iOS FMOD/Spine libraries, Xcode signing with the necessary memory entitlement, the separate large PCK file, and an actual iPhone test. Consult the [upstream build guide](https://github.com/jhaizhou-ops/sts2-ios/blob/main/AGENTS.md).

**Never add Steam game content, third-party proprietary binaries, Apple signing materials, or secrets to this public repository, including Actions artifacts.** A .gitignore file is not a security boundary.

## Fastest playable test (alternative launcher, no custom build)

A separate community project, [MikeMikerson/STS2 Mobile](https://github.com/MikeMikerson/sts2-ios-launcher-public), provides an **unsigned, game-free** IPA that can be signed with Signulous/AltStore/SideStore and then download the owner's game from Steam inside the app. The launcher is **not made or verified by this repository**, and it requires authorizing a Steam session in a third-party app. Read its source and terms before authorizing your account.

- [STS2 Mobile 1.1.1 IPA (release, 2026-11-13)](https://github.com/MikeMikerson/sts2-ios-launcher-public/releases/download/v1.1.1/STS2Mobile-1.1.1.ipa)
- Expected release SHA-256: `4aa3cd06cf3907058ed42653a5da67f818fd789da35e933b99271a048529e0d8` (GitHub API asset digest; not independently downloaded here)
- Upstream documents iOS 15+ and a tested Steam beta v0.113.0. **iPhone Duo layout and this signing service are unverified.**
- The user's original Windows v0.107.1 files are not imported by this launcher; it retrieves a supported game version from Steam.

The custom native port build workflows here remain available as a fallback or for device-specific work. No game binaries or signing materials are stored here.

## Offline-only route (preferred: no Steam sign-in on the iPhone)

Do **not** use a launcher requiring Steam authentication. A different open-source native port, [FlyingViet/sts2-ios-launch](https://github.com/FlyingViet/sts2-ios-launch), documents support for the user's **Windows Steam v0.107.1** game files and an optional Steam Cloud sign-in that can be skipped. It has an iPhone Duo layout path but requires **Xcode 27.1 or newer** to fill both Duo displays. This route avoids Steam account credentials altogether after the user has obtained the owned files.

On a properly provisioned **macOS** builder with access to the user's *private* owned game folder and the licensed dependencies, the documented command is:

```sh
git clone https://github.com/FlyingViet/sts2-ios-launch.git
cd sts2-ios-launch
./build.sh --unsigned --no-ota --game '/private/path/to/Slay the Spire 2'
```

The port documents `build/SlayTheSpire2.ipa` as output. `--unsigned` is intended for signing later using a personally controlled sideloading service, and `--no-ota` disables the port's script-update checks. **Do not sign into Steam at first launch**; the port says its save-sync login can be skipped. Build and test the app before treating it as safe or compatible.

### Outstanding build constraints
- This repo is public. Never commit or upload game files (including the resulting complete IPA), Apple IDs, passwords, tokens, or proprietary SDKs to public repository history, releases, or Actions artifacts.
- The previously tested default GitHub macOS runner reported **Xcode 26.6** (not sufficient for the port's native iPhone Duo screen integration). Select a macOS environment with Xcode 27.1+ for the full Duo experience.
- GitHub Actions has no access to ChatGPT's connected Google Drive. An authenticated **private** means of delivering your owned game files to the Mac is required; the present workflows do not do that.
- A successful source preflight or matching assembly symbols is **not** a compiled or device-tested game. No complete IPA has been produced here.
