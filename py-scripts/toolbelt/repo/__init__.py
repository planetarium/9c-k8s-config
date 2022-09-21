from collections import OrderedDict

# copy release 9c repos data
repositories = OrderedDict(
    [
        ("lib9c", {}),
        ("NineChronicles.RPC.Shared", {}),
        (
            "NineChronicles",
            {
                "lib9c": "nekoyume/Assets/_Scripts/Lib9c/lib9c",
                "NineChronicles.RPC.Shared": "nekoyume/Assets/_Scripts/NineChronicles.RPC.Shared",
            },
        ),
        (
            "NineChronicles.Headless",
            {
                "lib9c": "Lib9c",
                "NineChronicles.RPC.Shared": "NineChronicles.RPC.Shared",
            },
        ),
        (
            "9c-launcher",
            {
                "NineChronicles.Headless": "NineChronicles.Headless",
                "NineChronicles": "NineChronicles",
            },
        ),
    ]
)
