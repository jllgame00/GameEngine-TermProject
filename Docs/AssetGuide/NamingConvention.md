# Unreal Asset Naming Convention

| Prefix | Meaning |
| --- | --- |
| `BP_` | Blueprint Actor |
| `BPC_` | Blueprint Component |
| `BPI_` | Blueprint Interface |
| `WBP_` | Widget Blueprint |
| `SM_` | Static Mesh |
| `SK_` | Skeletal Mesh |
| `M_` | Material |
| `MI_` | Material Instance |
| `MF_` | Material Function |
| `T_` | Texture |
| `DT_` | DataTable |
| `DA_` | Data Asset |
| `ST_` | Struct |
| `E_` | Enum |
| `ABP_` | Animation Blueprint |
| `AM_` | Animation Montage |
| `BT_` | Behavior Tree |
| `BB_` | Blackboard |
| `S_` | Sound |
| `SC_` | Sound Cue |
| `MS_` | MetaSound |
| `NS_` | Niagara System |
| `L_` | Level |
| `LS_` | Level Sequence |

Examples: `BP_Customer`, `BP_Turntable`, `BPI_Interactable`, `WBP_Dialogue`, `WBP_RecordSelection`, `SM_Turntable`, `SM_RecordShelf_A`, `M_Wood_Master`, `MI_Wood_Dark`, `DT_Records`, `DT_Customers`, `DT_Requests`, `BT_Customer`, `BB_Customer`, and `L_RecordShop_Greybox`.

- Do not use spaces in Unreal asset names.
- Prefer clear English asset names.
- Do not append arbitrary suffixes such as `Final_Final2`.
- Use A/B/C only for meaningful visual variants.
- Use `_Test` only for temporary test assets.
- Production assets must not live under `Dev/`.

