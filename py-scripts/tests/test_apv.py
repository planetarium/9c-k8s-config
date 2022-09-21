import pytest

from toolbelt.planet.apv import Planet, ApvParseError

planet = Planet()


def test_planet_analyze_apv():
    apv = planet.analyze_apv(
        "100081/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEQCIBY+2PYNH4ccQljtgcUE.6VFxsjmC732wnjhwVsdeQN1AiBu75I6Wvugciehz2EE8XqT3kZy8YOvAlfQ8kq6YEAe6A==/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTA3VDEzOjA4OjQyKzAwOjAwZQ=="
    )
    assert 100081 == apv.version
    assert "0x6ec8E598962F1f475504F82fD5bF3410eAE58B9B" == apv.signer
    assert (
        "30440220163ed8f60d1f871c4258ed81c504ffa545c6c8e60bbdf6c278e1c15b1d79037502206eef923a5afba07227a1cf6104f17a93de4672f183af0257d0f24aba60401ee8"
        == apv.signature
    )
    assert {
        "WindowsBinaryUrl": "https://download.nine-chronicles.com/v100081/Windows.zip",
        "macOSBinaryUrl": "https://download.nine-chronicles.com/v100081/macOS.tar.gz",
        "timestamp": "2021-10-07T13:08:42+00:00",
    } == apv.extra


@pytest.mark.parametrize(
    "apv",
    [
        "100",
        "100081/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEQCIBY+2PYNH4ccQljtgcUE.6VFxsjmC732wnjhwVsdeQN1AiBu75I6Wvugciehz2EE8XqT3kZy8YOvAlfQ8kq6YEAe6A==/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTA3VDEzOjA4OjQyKzAwOjAwZQ====",
    ],
)
def test_planet_invalid_analyze_apv(apv):
    with pytest.raises(ApvParseError):
        planet.analyze_apv(apv)
