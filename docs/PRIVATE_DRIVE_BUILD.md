# Secure offline build from your Windows Steam copy (iPhone Duo)

This repository is PUBLIC and contains only scripts. The official Steam game files and the completed game-containing IPA stay in **private Google Drive**, never in public GitHub commits, releases or Actions artifacts. The game runs offline after installation and does not require a Steam login in the iOS app.

## Ready
- [Source-only checks](../.github/workflows/source-preflight.yml) already pass.
- [Duo Xcode 27.1+ runner test](../.github/workflows/xcode27-duo-readiness.yml) passes on `runs-on: xcode-27`.
- [Offline builder](../.github/workflows/private-offline-ipa.yml) has been added but **cannot be run successfully until private Drive authentication is configured**.
- Source folder (already present): [Slay the Spire 2](https://drive.google.com/drive/folders/1lBeSs_qBpZbmfFbvcuhRdCUUlrCD1dIk)
- Output folder (private): [STS2 iPhone IPA Builds](https://drive.google.com/drive/folders/1wO88P2wMpF84SIhWXikCmiV5cIdfRmSj)

## Required private setup on Windows

GitHub Actions **cannot** reuse the Google Drive connection that you approved for ChatGPT. To let the cloud Mac read and write those two private folders, you must separately authorize a Google Drive client.

**Security notice:** A typical rclone OAuth configuration with full Drive scope can access your entire Google Drive, not just these two folders. GitHub Actions secrets conceal the token from repository visitors, but anyone who can modify the repository's default-branch workflows could potentially access it. Prefer a *separate, dedicated Google account* that has access only to the game folder (Viewer) and the IPA output folder (Editor), and authorize rclone under that account. If you use your main Google account, consider it higher-risk and revoke the authorization after the build.

1. Install [rclone](https://rclone.org/downloads/) on your Windows PC.
2. Open PowerShell and create an isolated config file:

   ```powershell
   rclone --config "$env:TEMP\sts2-only-rclone.conf" config
   ```

3. Choose a new remote named exactly `sts2drive`, select **Google Drive**, select the **read/write Drive scope** needed to retrieve and upload files, and complete the browser authentication. If you selected a dedicated account, first share both folders with that account as described above.
4. Open only the isolated config in Notepad:

   ```powershell
   notepad "$env:TEMP\sts2-only-rclone.conf"
   ```

5. In your GitHub repository, go to [Settings → Secrets and variables → Actions](https://github.com/noggle040/sts2-duo-build/settings/secrets/actions), select **New repository secret**, name it exactly `STS2_RCLONE_CONFIG`, and paste the *complete* contents of that isolated config. **Do not paste the token in a chat, a GitHub issue, a file committed to the repo, or a workflow input.**
6. Open [Actions → Stage 4 - Private offline Duo IPA build](https://github.com/noggle040/sts2-duo-build/actions/workflows/private-offline-ipa.yml), click **Run workflow**, and follow the result. The job:
   - Runs on Xcode 27.1+ on Apple silicon
   - Downloads your owned v0.107.1 Windows game files into ephemeral local disk, without contacting Steam
   - Deletes its Drive token before invoking the pinned offline port source
   - Builds `--unsigned --no-ota`
   - Restores the Drive token only to upload the completed IPA into your private output folder
   - Clears local game files and OAuth config at the end
7. Once the IPA is in your private Drive, download it to your iPhone and sign it through Signulous. Test launch and folding behaviour. The build is **not guaranteed to succeed**; compatibility, space, and signing must be verified.

## After completion
- Delete the `STS2_RCLONE_CONFIG` GitHub Actions secret.
- Revoke rclone's Google account authorization if it was temporary.
- Check that no game files or IPA appeared in public GitHub Actions artifacts or repository contents (the workflow does not upload any).
- Don't give the finished game-containing IPA to anyone else.

## Caveats
The upstream [FlyingViet port](https://github.com/FlyingViet/sts2-ios-launch) is unofficial third-party code. This workflow pins commit `e4a8b82ffa10d571c3144ef7ce2612b707e559fb` for reproducibility; no security audit is implied. It downloads tools/dependencies at build time. Review source and dependency licensing before running. The iPhone app's optional Steam Cloud login should be **skipped**. Signing services may alter entitlements or application identifiers; actual Duo behaviour must be checked on-device.
