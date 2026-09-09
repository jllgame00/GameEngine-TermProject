# Asset Ownership

Unreal `.uasset` and `.umap` files are binary. Do not have several developers edit the same asset at the same time.

Suggested ownership:

| Asset or area | Owner |
| --- | --- |
| `L_RecordShop_Main` | Environment / Integration owner |
| `BP_Customer` | NPC owner |
| `WBP_Dialogue` | UI / Dialogue owner |
| `WBP_RecordSelection` | UI / Recommendation owner |
| `BP_Turntable` | Interaction / Turntable owner |
| Recommendation system assets | Recommendation owner |

Use the separate test maps for parallel implementation. Transfer ownership explicitly before another contributor makes substantial changes to a binary asset.

