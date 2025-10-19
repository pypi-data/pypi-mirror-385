from jinjanator_plugin_format_toml import plugin


def test_formats_hook() -> None:
    result = plugin.plugin_formats()
    assert plugin.TOMLFormat.name in result
    assert result[plugin.TOMLFormat.name] == plugin.TOMLFormat


def test_format() -> None:
    fmt = plugin.TOMLFormat(None)
    result = fmt.parse('[testdoc]\ncheese="bleu"')
    assert "testdoc" in result
    assert "cheese" in result["testdoc"]
    assert "bleu" == result["testdoc"]["cheese"]
