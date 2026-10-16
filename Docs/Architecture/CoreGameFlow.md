# Core Game Flow

## State progression

```text
StoreReady
→ CustomerEntering
→ CustomerWaiting
→ Dialogue
→ RecordSelection
→ TurntableSetup
→ Listening
→ RecommendationResult
→ ResultDialogue
→ PurchaseDecision (optional)
→ CustomerLeaving
→ CycleComplete
```

The player explores a small LP listening bar, record shop, and café; handles customers, learns their mood and taste through dialogue, selects and plays an LP, and observes the result. A staff NPC handles drinks as ambient café activity.

## Coordination principle

Systems should not form a web of arbitrary direct dependencies. A central Game Flow layer coordinates progression between Customer, Dialogue, Recommendation, Record Selection, Turntable, Camera, Audio, and Result systems. Each system should expose the focused information or events that flow coordination needs, rather than directly driving unrelated systems.

