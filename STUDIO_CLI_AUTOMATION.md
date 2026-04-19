# Roblox Studio CLI Automation

## Overview

This document describes the approach for programmatically creating blank Roblox place files (.rbxl) on macOS.

## Research Findings

### Roblox Studio CLI Limitations
1. **No direct CLI for creating places**: Roblox Studio on macOS does not provide command-line arguments to create new blank places programmatically.
2. **Limited CLI options**: The available CLI options are mainly for opening existing places (`-placeId`, `-openScriptPath`).
3. **GUI-based workflow**: Creating new places requires GUI interaction, making direct CLI automation challenging.

### RBXL File Format
- RBXL files are XML-based documents with a specific structure
- They contain instances, properties, and metadata
- A minimal blank place can be created by generating the XML structure directly

## Solution Approach

Since Roblox Studio doesn't support CLI-based place creation, we'll:
1. **Generate a minimal RBXL XML file** programmatically
2. **Create the file structure** that represents a blank place
3. **Save it to the specified location**
4. **Optionally open it in Roblox Studio** for verification

### Minimal RBXL Structure

A blank place file requires:
- Root `<roblox>` element with version="4"
- Metadata for model format compatibility
- A Workspace instance as the root container
- Basic services (Workspace, Lighting, etc.)

### Implementation Strategy

1. **Template Generation**: Create a minimal XML template for a blank place
2. **File Creation**: Write the XML to the target location
3. **Validation**: Ensure the file can be opened in Roblox Studio
4. **Error Handling**: Handle file system errors and retry logic

## Script Features

The `roblox-create-blank-place.sh` script will:
- Create necessary directories if they don't exist
- Generate a valid blank RBXL file
- Provide clear success/error messages
- Include retry logic for file operations
- Optionally validate the created file

## Alternative Approaches Considered

1. **AppleScript/UI Automation**: Too fragile and platform-specific
2. **Third-party tools (Rojo, run-in-roblox)**: Add unnecessary dependencies
3. **Binary RBXL format**: More complex than XML format

## Conclusion

Direct XML generation is the most reliable approach for creating blank RBXL files programmatically on macOS, given the lack of CLI support in Roblox Studio.