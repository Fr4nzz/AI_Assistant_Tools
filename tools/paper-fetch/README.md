# Paper Fetch

Search and download academic papers with automatic mirror discovery and Open Access fallback.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool paper-fetch
```

The installer downloads the skill and Python scripts to:

```text
%USERPROFILE%\.ai-assistant-tools\paper-fetch
```

And creates a shim at:

```text
%USERPROFILE%\.local\bin\paper-dl
```

Restart Codex Desktop after installing.

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

The installer downloads the skill to:

```text
~/.ai-assistant-tools/paper-fetch
```

And creates a shim at:

```text
~/.local/bin/paper-dl
```

Restart Codex Desktop after installing.

## Setup

Before using, configure the required email:

```bash
paper-dl set-key unpaywall-email your@email.com
```

### Optional: Get an OpenAlex API Key (Recommended)

1. Go to https://openalex.org/settings/api-key
2. Create an account or sign in
3. Copy the API key
4. Run:
   ```bash
   paper-dl set-key openalex YOUR_KEY_HERE
   ```

This improves search rate limits and is free.

## Tests

```bash
paper-dl --version
paper-dl mirrors
paper-dl search "CRISPR gene editing" -n 3
paper-dl lookup 10.1038/s41586-019-1055-0
paper-dl download 10.1038/s41586-019-1055-0 -o ~/Downloads/papers
```
