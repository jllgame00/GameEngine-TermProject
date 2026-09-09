# RecordShop Documentation

This documentation keeps the six-person project aligned without mixing source-art work into Unreal asset folders.

- [Architecture](Architecture/) — game flow, map coordination, future C++ layout, and plugin policy.
- [AssetGuide](AssetGuide/) — naming, ownership, development-workspace, art-pipeline, and third-party guidance.
- [ArtSource](../ArtSource/) — editable Blender and design files, references, AI outputs, exports, and source audio.
- [Content/RecordShop](../Content/RecordShop/) — Unreal assets actually used by the game.

## Folder responsibilities

`Content/RecordShop` contains reviewed assets used by Unreal. `ArtSource` contains editable source files, references, AI outputs, and DCC files; it is not an Unreal import destination. `Docs` contains architecture and team workflow documentation. `Content/ThirdParty`, and any existing vendor namespaces, contain external assets. Preserve vendor/Fab/Marketplace namespaces; use `Content/ThirdParty` only for third-party assets the team manually controls.

