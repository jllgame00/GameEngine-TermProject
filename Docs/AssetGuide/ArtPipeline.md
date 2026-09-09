# Art Pipeline

## Hybrid environment workflow

1. Build an Unreal greybox first.
2. Validate player movement, camera, and NPC paths.
3. Use Fab/vendor assets for generic props.
4. Use Astra, Meshy, Tripo, and Blender for distinctive game-specific assets.
5. Clean generated models in Blender.
6. Apply transforms, scale, origin, normals, and UV cleanup.
7. Export FBX or GLB.
8. Import into `Content/RecordShop`.
9. Apply game Material Instances in Unreal.
10. Add collision.
11. Test in gameplay.
12. Replace the greybox only after the asset passes gameplay testing.

Generic assets include cups, plants, chairs, lamps, small tables, and decorations. Good custom assets include the turntable, LP shelves, listening-bar counter, signature speakers, record display units, and store signage.

Do not generate the whole store as one monolithic AI mesh. Prefer modular pieces.

## Source-asset boundary

Keep AI sources, references, Blender files, exports, textures, UI source, and audio source under `ArtSource/`; do not directly mix AI source files into Unreal Content.

```text
AI / reference
→ Blender source
→ cleaned Blender asset
→ FBX/GLB export
→ Unreal import
→ .uasset
```

Example:

```text
ArtSource/AI_Generated/Meshy/Speaker01/original.glb
→ ArtSource/Blender/ListeningBar/Speakers/Speaker01_clean.blend
→ ArtSource/Export/FBX/SM_Speaker01.fbx
→ Content/RecordShop/Art/Environment/ListeningBar/Speakers/SM_Speaker01
```

