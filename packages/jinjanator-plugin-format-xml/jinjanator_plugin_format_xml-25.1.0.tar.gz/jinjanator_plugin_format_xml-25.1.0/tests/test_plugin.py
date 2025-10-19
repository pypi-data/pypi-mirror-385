from jinjanator_plugin_format_xml import plugin


def test_formats_hook() -> None:
    result = plugin.plugin_formats()
    assert plugin.XMLFormat.name in result
    assert result[plugin.XMLFormat.name] == plugin.XMLFormat


def test_format() -> None:
    fmt = plugin.XMLFormat(None)
    result = fmt.parse("<testdoc><cheese>bleu</cheese></testdoc>")
    assert "testdoc" in result
    assert "cheese" in result["testdoc"]
    assert "bleu" == result["testdoc"]["cheese"]


def test_format_namespaces() -> None:
    fmt = plugin.XMLFormat("process-namespaces")
    result = fmt.parse('<testdoc xmlns:a="http://a.com/"><a:cheese>bleu</a:cheese></testdoc>')
    assert "testdoc" in result
    assert "http://a.com/:cheese" in result["testdoc"]
    assert "bleu" == result["testdoc"]["http://a.com/:cheese"]


def test_format_ignore_namespaces() -> None:
    fmt = plugin.XMLFormat(None)
    result = fmt.parse('<testdoc xmlns:a="http://a.com/"><a:cheese>bleu</a:cheese></testdoc>')
    assert "testdoc" in result
    assert "a:cheese" in result["testdoc"]
    assert "bleu" == result["testdoc"]["a:cheese"]
