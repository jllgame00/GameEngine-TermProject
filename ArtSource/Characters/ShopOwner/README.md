# Production ShopOwner source

`ShopOwner.blend` and `ShopOwner.fbx` correspond to production
`/Game/RecordShop/Characters/Player/Mesh/SKM_ShopOwner1` from PR #14.
These are **reconstructed editable sources**, not the contributor's original
Blender project or original import FBX. Original DCC files were not supplied
in PR #14 and their recorded machine-local paths are unavailable here.

The previous procedural character sources are preserved byte-for-byte in
`Historical/ShopOwner_PrePR14.blend` and `Historical/ShopOwner_PrePR14.fbx`.
Those describe the older `SKM_ShopOwner`, not the current player.

## Recovery and correspondence

- Unreal Engine 5.8's supported skeletal-mesh exporter produced `ShopOwner.fbx`
  directly from the current mesh. This FBX has not been rewritten in Blender.
  Its material metadata retains contributor-machine texture filenames. Use the
  packed Blender material or explicitly bind the supplied Textures/ PNG files;
  those old absolute texture paths are not portable dependencies.
- Blender 5.2.1's official FBX importer supplied the editable mesh and rig in
  `ShopOwner.blend`: 84,619 vertices, 101,797 triangles, original UVs and weights.
  Mesh dimensions are approximately 0.815439 x 0.320245 x 1.647670 metres.
- All 66 Unreal skeleton nodes are represented. Blender imports the FBX `Root`
  skeleton node as the armature object, with 65 bones underneath it. This is
  expected importer behavior. Node transforms and parent relationships are
  retained; no duplicate root bone was added.
- The single `M_ShopOwner_Body` preview material uses the three exported textures
  in `Textures/`. PNG pixels match official Unreal TGA exports exactly. The same
  images are packed into the blend for portability.
- Base color uses sRGB. ORM and normal maps use non-color data. ORM red is ambient
  occlusion, green is roughness and blue is metallic. The Blender shader connects
  roughness/metallic and flips the DirectX normal map's green channel in the
  shader; the image is unchanged. Unreal's AO connection is recorded here;
  Blender Principled has no equivalent direct AO input. Specular is 0.42.
  Blender shading is a preview approximation of Unreal.
- `Animations/A_ShopOwner_SendingFax_01.fbx` is the supported Unreal export of
  the production baked animation. Montage windows, blends, IK, AnimBP logic,
  physics and capsule settings remain authoritative in Unreal assets.

`source-manifest.json` records source ref/SHA/LFS identifiers, current Unreal
package hashes, reconstructed-file hashes, geometry/weight/UV/transform
fingerprints and historical-file hashes. Recovery cannot recreate the original
sculpt, modifier stack, authoring controls or unbaked animation rig.

## Editing

Open `ShopOwner.blend`; the mesh, rig, material and packed images are ready for
editing. Keep the imported centimetre-to-metre object transforms and bone names.
Use the retained FBX as the exact exported reference. Work in a separate import
target and compare skeleton, bind transforms, weights, material slots and
animation before any production reimport. A Blender round trip is not a reason
to overwrite the proven player or its physics/animation setup.

The model is contributor work from PR #14. This recovery does not claim new
original authorship of its geometry, textures or animation.
