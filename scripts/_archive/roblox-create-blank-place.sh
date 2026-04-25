#!/bin/bash

# roblox-create-blank-place.sh
# Creates a blank Roblox place (.rbxl file) programmatically
# Usage: ./roblox-create-blank-place.sh [output_path]
# Default output: ~/.games/momotaro-roblox-rpg/template.rbxl

set -euo pipefail

# Configuration
DEFAULT_OUTPUT_PATH="$HOME/.games/momotaro-roblox-rpg/template.rbxl"
OUTPUT_PATH="${1:-$DEFAULT_OUTPUT_PATH}"
MAX_RETRIES=3
RETRY_DELAY=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to generate UUID
generate_uuid() {
    if command -v uuidgen >/dev/null 2>&1; then
        echo "RBX$(uuidgen | tr -d '-' | tr '[:lower:]' '[:upper:]')"
    else
        # Fallback: use random hex
        echo "RBX$(openssl rand -hex 16 | tr '[:lower:]' '[:upper:]')"
    fi
}

# Function to create directory with retry
create_directory() {
    local dir=$1
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        if mkdir -p "$dir" 2>/dev/null; then
            return 0
        fi
        
        print_message "$YELLOW" "Attempt $attempt/$MAX_RETRIES: Failed to create directory, retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
        ((attempt++))
    done
    
    return 1
}

# Function to write file with retry
write_file() {
    local file=$1
    local content=$2
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        if echo "$content" > "$file" 2>/dev/null; then
            return 0
        fi
        
        print_message "$YELLOW" "Attempt $attempt/$MAX_RETRIES: Failed to write file, retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
        ((attempt++))
    done
    
    return 1
}

# Function to generate minimal blank RBXL XML
generate_blank_rbxl() {
    local workspace_id=$(generate_uuid)
    local lighting_id=$(generate_uuid)
    local soundservice_id=$(generate_uuid)
    local replicated_storage_id=$(generate_uuid)
    local replicated_first_id=$(generate_uuid)
    local starter_gui_id=$(generate_uuid)
    local starter_pack_id=$(generate_uuid)
    local starter_player_id=$(generate_uuid)
    local teams_id=$(generate_uuid)
    
    cat <<EOF
<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">
	<Meta name="ExplicitAutoJoints">true</Meta>
	<External>null</External>
	<External>nil</External>
	<Item class="Workspace" referent="${workspace_id}">
		<Properties>
			<bool name="AllowThirdPartySales">false</bool>
			<string name="CollisionGroups">Default^0^1</string>
			<float name="Gravity">196.2</float>
			<string name="Name">Workspace</string>
			<bool name="StreamingEnabled">false</bool>
			<int name="StreamingMinRadius">64</int>
			<int name="StreamingTargetRadius">1024</int>
		</Properties>
		<Item class="Camera" referent="$(generate_uuid)">
			<Properties>
				<string name="Name">Camera</string>
				<CoordinateFrame name="CFrame">
					<X>0</X>
					<Y>20</Y>
					<Z>20</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>0.707106769</R11>
					<R12>-0.707106769</R12>
					<R20>0</R20>
					<R21>0.707106769</R21>
					<R22>0.707106769</R22>
				</CoordinateFrame>
				<float name="FieldOfView">70</float>
			</Properties>
		</Item>
		<Item class="Terrain" referent="$(generate_uuid)">
			<Properties>
				<string name="Name">Terrain</string>
				<bool name="Anchored">true</bool>
				<Color3 name="WaterColor">
					<R>0.0470588244</R>
					<G>0.329411775</G>
					<B>0.360784322</B>
				</Color3>
				<float name="WaterReflectance">1</float>
				<float name="WaterTransparency">0.300000012</float>
				<float name="WaterWaveSize">0.150000006</float>
				<float name="WaterWaveSpeed">10</float>
			</Properties>
		</Item>
		<Item class="SpawnLocation" referent="$(generate_uuid)">
			<Properties>
				<string name="Name">SpawnLocation</string>
				<bool name="Anchored">true</bool>
				<Vector3 name="Size">
					<X>12</X>
					<Y>1</Y>
					<Z>12</Z>
				</Vector3>
				<CoordinateFrame name="CFrame">
					<X>0</X>
					<Y>0.5</Y>
					<Z>0</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>1</R11>
					<R12>0</R12>
					<R20>0</R20>
					<R21>0</R21>
					<R22>1</R22>
				</CoordinateFrame>
				<bool name="CanCollide">true</bool>
				<int name="BrickColor">194</int>
				<float name="Transparency">0</float>
			</Properties>
		</Item>
	</Item>
	<Item class="Lighting" referent="${lighting_id}">
		<Properties>
			<string name="Name">Lighting</string>
			<Color3 name="Ambient">
				<R>0.5</R>
				<G>0.5</G>
				<B>0.5</B>
			</Color3>
			<float name="Brightness">1</float>
			<string name="TimeOfDay">14:00:00</string>
		</Properties>
	</Item>
	<Item class="SoundService" referent="${soundservice_id}">
		<Properties>
			<string name="Name">SoundService</string>
		</Properties>
	</Item>
	<Item class="ReplicatedStorage" referent="${replicated_storage_id}">
		<Properties>
			<string name="Name">ReplicatedStorage</string>
		</Properties>
	</Item>
	<Item class="ReplicatedFirst" referent="${replicated_first_id}">
		<Properties>
			<string name="Name">ReplicatedFirst</string>
		</Properties>
	</Item>
	<Item class="StarterGui" referent="${starter_gui_id}">
		<Properties>
			<string name="Name">StarterGui</string>
		</Properties>
	</Item>
	<Item class="StarterPack" referent="${starter_pack_id}">
		<Properties>
			<string name="Name">StarterPack</string>
		</Properties>
	</Item>
	<Item class="StarterPlayer" referent="${starter_player_id}">
		<Properties>
			<string name="Name">StarterPlayer</string>
		</Properties>
		<Item class="StarterPlayerScripts" referent="$(generate_uuid)">
			<Properties>
				<string name="Name">StarterPlayerScripts</string>
			</Properties>
		</Item>
		<Item class="StarterCharacterScripts" referent="$(generate_uuid)">
			<Properties>
				<string name="Name">StarterCharacterScripts</string>
			</Properties>
		</Item>
	</Item>
	<Item class="Teams" referent="${teams_id}">
		<Properties>
			<string name="Name">Teams</string>
		</Properties>
	</Item>
</roblox>
EOF
}

# Main execution
main() {
    print_message "$GREEN" "=== Roblox Blank Place Creator ==="
    print_message "$NC" "Output path: $OUTPUT_PATH"
    
    # Extract directory from output path
    OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
    
    # Create directory if it doesn't exist
    print_message "$NC" "Creating directory: $OUTPUT_DIR"
    if ! create_directory "$OUTPUT_DIR"; then
        print_message "$RED" "ERROR: Failed to create directory after $MAX_RETRIES attempts"
        exit 1
    fi
    
    # Generate RBXL content
    print_message "$NC" "Generating blank place XML..."
    RBXL_CONTENT=$(generate_blank_rbxl)
    
    # Write the file
    print_message "$NC" "Writing RBXL file..."
    if ! write_file "$OUTPUT_PATH" "$RBXL_CONTENT"; then
        print_message "$RED" "ERROR: Failed to write file after $MAX_RETRIES attempts"
        exit 1
    fi
    
    # Verify file was created
    if [ -f "$OUTPUT_PATH" ]; then
        FILE_SIZE=$(wc -c < "$OUTPUT_PATH")
        print_message "$GREEN" "✅ SUCCESS: Created blank place file"
        print_message "$NC" "   Path: $OUTPUT_PATH"
        print_message "$NC" "   Size: $FILE_SIZE bytes"
        
        # Validate XML structure
        if command -v xmllint >/dev/null 2>&1; then
            print_message "$NC" "Validating XML structure..."
            if xmllint --noout "$OUTPUT_PATH" 2>/dev/null; then
                print_message "$GREEN" "✅ XML validation passed"
            else
                print_message "$YELLOW" "⚠️  XML validation warnings (file may still work)"
            fi
        fi
        
        # Run validation if script exists
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -x "$SCRIPT_DIR/validate-rbxl.sh" ]; then
            print_message "$NC" ""
            print_message "$NC" "Running full validation..."
            "$SCRIPT_DIR/validate-rbxl.sh" "$OUTPUT_PATH" | grep -E "(✅|❌|⚠️)" || true
        fi
        
        # Optional: Open in Roblox Studio
        if [ -d "/Applications/RobloxStudio.app" ]; then
            print_message "$NC" ""
            print_message "$NC" "To open in Roblox Studio, run:"
            print_message "$GREEN" "   open -a RobloxStudio \"$OUTPUT_PATH\""
        fi
    else
        print_message "$RED" "ERROR: File was not created successfully"
        exit 1
    fi
    
    print_message "$GREEN" ""
    print_message "$GREEN" "=== Process Complete ==="
}

# Run main function
main