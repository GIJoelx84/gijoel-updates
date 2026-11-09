# Optional ROM delivery

Put config/roms.json in the cabinet profile to enable downloads for that cabinet. The updater runs this step before activating the release.

```json
{
  "version": 1,
  "roms": [
    {
      "system": "nes",
      "filename": "Example.nes",
      "url": "https://downloads.example.com/Example.nes",
      "bytes": 16400,
      "sha256": "replace-with-the-exact-64-character-lowercase-sha256"
    }
  ]
}
```

Use an HTTPS download source for files you have permission to distribute. Keep credentials and private download URLs out of public manifests. A cabinet-local profile overlay can supply config/roms.json for private or device-specific URLs.

Supported destinations are nes (.nes or .zip) and mame-libretro (.zip). Match arcade ROM sets to the installed core. Use the same filename in the cabinet's game list. Each download is staged and verified before installation. Identical files are skipped, differing existing files cause the update to stop, and ROMs are retained if an entry is removed.

This test branch includes the installer and updater hook. Add a real manifest and verify the game launches on a cabinet before rollout.
