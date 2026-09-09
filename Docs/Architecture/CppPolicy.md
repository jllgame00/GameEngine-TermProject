# C++ Policy

RecordShop is currently Blueprint-only: there is no `Source/` directory and `RecordShop.uproject` declares no modules. No C++ module is created by this setup.

If the team legitimately adds a RecordShop C++ module later, its intended organization is:

```text
Source/RecordShop/
├── Core/
├── Characters/
├── Interaction/
├── Systems/
│   ├── Dialogue/
│   ├── Recommendation/
│   ├── Turntable/
│   └── Customer/
├── Data/
├── AI/
└── UI/
```

Create this physical tree only as part of the normal Unreal C++ module-creation workflow.

