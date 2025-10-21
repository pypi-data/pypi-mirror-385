# Minitap MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to control and interact with real mobile devices (Android & iOS) through natural language commands.

## Quick Start

### Installation

```bash
pip install minitap-mcp
```

### Prerequisites

Before running the MCP server, ensure you have the required mobile automation tools installed:

- **For Android devices:**
  - [ADB (Android Debug Bridge)](https://developer.android.com/tools/adb) - For device communication
  - [Maestro](https://maestro.mobile.dev/) - For mobile automation (optional but recommended)

- **For iOS devices (macOS only):**
  - Xcode Command Line Tools with `xcrun`
  - [Maestro](https://maestro.mobile.dev/) - For mobile automation (optional but recommended)

For detailed setup instructions, see the [mobile-use repository](https://github.com/minitap-ai/mobile-use).

### Configuration

Set your Minitap API credentials as environment variables:

```bash
export MINITAP_API_KEY="your_api_key_here"
export MINITAP_API_BASE_URL="https://platform.minitap.ai/api/v1"
export MINITAP_LLM_PROFILE_NAME="default"
```

You can set these variables in your `.bashrc` or equivalent.

### Running the Server

**With environment variables:**

```bash
minitap-mcp --server
```

**With API key as argument:**

```bash
minitap-mcp --server --api-key your_api_key_here
```

Using `--api-key` overrides the `MINITAP_API_KEY` environment variable, useful for quick testing.

By default, the server will bind to `0.0.0.0:8000`. Configure via environment variables:

```bash
export MCP_SERVER_HOST="0.0.0.0"
export MCP_SERVER_PORT="8000"
```

## IDE Integration

1. Start the server: `minitap-mcp --server`
2. Add to your IDE MCP settings file:

```jsonc
# For Windsurf
{
  "mcpServers": {
    "minitap-mcp": {
      "serverUrl": "http://localhost:8000/mcp"
    }
  }
}
```

```jsonc
# For Cursor
{
  "mcpServers": {
    "minitap-mcp": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```


## Available Tools

Once connected, your AI assistant can use these tools:

### `execute_mobile_command`
Execute natural language commands on your mobile device using the Minitap SDK. This tool allows you to control your Android or iOS device using natural language.

**Parameters:**
- `goal` (required): High-level goal describing the action to perform
- `output_description` (optional): Description of expected output format
- `profile` (optional): Profile name to use (defaults to "default")

**Examples:**
```
"Open the settings app and tell me the battery level"
"Find the first 3 unread emails in Gmail"
"Open Google Maps and search for the nearest coffee shop"
"Take a screenshot and save it"
```

### `analyze_screen`
Capture and analyze what's currently shown on the mobile device screen using a vision-capable LLM. Useful for understanding UI elements, extracting text, or identifying specific features.

**Parameters:**
- `prompt` (required): Analysis prompt describing what information to extract
- `device_id` (optional): Specific device ID to target

**Examples:**
```js
"What app is currently open?"
"Read the text messages visible on screen"
"List all buttons and their labels on the current screen"
"Extract the phone number displayed"
```

## Advanced Configuration

### Custom ADB Server

If using a remote or custom ADB server (like on WSL):

```bash
export ADB_SERVER_SOCKET="tcp:192.168.1.100:5037"
```

### Vision Model

Customize the vision model used for screen analysis:

```bash
export VISION_MODEL="qwen/qwen-2.5-vl-7b-instruct"
```

## Device Setup

### Android
1. Enable USB debugging on your device
2. Connect via USB or network ADB
3. Verify connection: `adb devices`

### iOS (macOS only)
1. Install Xcode Command Line Tools
2. Start a simulator or connect a physical device
3. Verify: `xcrun simctl list devices booted`

## Troubleshooting

**No devices found:**
- Verify ADB/xcrun connection
- Check USB debugging is enabled (Android)
- Ensure device is unlocked

**Connection refused errors:**
- Check ADB/xcrun connection

**API authentication errors:**
- Verify `MINITAP_API_KEY` is set correctly

## Links

- **Mobile-Use SDK:** [github.com/minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use)
- **Mobile-Use Documentation:** [docs.minitap.ai](https://docs.minitap.ai)
