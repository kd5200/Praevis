# Malicious page fixtures

Used by automated tests via mocked HTTP transports or local file reads.
**Do not** fetch uncontrolled public websites in CI.

| Fixture | Intent |
|---------|--------|
| `direct-prompt-injection.html` | Visible ignore-previous / secret exfil |
| `hidden-prompt-injection.html` | Hidden `display:none` injection |
| `tool-manipulation.html` | Tool/function call coercion |
| `encoded-instructions.html` | Base64 / obfuscation markers |
| `role-markers.html` | system/assistant/developer role lines |
| `zero-width-injection.html` | Zero-width characters around instructions |
| `command-execution.html` | Shell/command execution instructions |
