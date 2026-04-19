#!/usr/bin/env python3
"""
inject-scripts-into-template.py - Inject Lua scripts into template.rbxl
This script reads the template.rbxl XML file and injects script content from the scripts/ directory.
"""

import sys
import os
import xml.etree.ElementTree as ET
import base64
import re

def escape_xml(text):
    """Escape XML special characters in text."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

def read_lua_file(filepath):
    """Read and return Lua script content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None

def inject_scripts(template_path, scripts_dir, output_path):
    """Inject Lua scripts into the template.rbxl file."""
    
    # Parse the XML template
    print(f"Loading template: {template_path}")
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # Find or create ServerScriptService
    server_script_service = None
    for item in root.iter('Item'):
        if item.get('class') == 'ServerScriptService':
            server_script_service = item
            break
    
    if not server_script_service:
        print("ServerScriptService not found, creating it...")
        # Find the root DataModel
        data_model = root
        if root.tag == 'roblox':
            for item in root:
                if item.tag == 'Item' and item.get('class') in ['DataModel', 'Place', None]:
                    data_model = item
                    break
        
        # Create ServerScriptService
        server_script_service = ET.SubElement(data_model, 'Item')
        server_script_service.set('class', 'ServerScriptService')
        server_script_service.set('referent', 'RBXServerScriptService')
        
        # Add properties
        props = ET.SubElement(server_script_service, 'Properties')
        name_prop = ET.SubElement(props, 'string')
        name_prop.set('name', 'Name')
        name_prop.text = 'ServerScriptService'
        
        print("  ✅ Created ServerScriptService")
    
    # Script mapping (which scripts go where)
    script_mappings = [
        ('MainGameScript.lua', 'ServerScriptService', 'Script'),
        ('PlayerManager.lua', 'ServerScriptService', 'Script'),
        ('CombatSystem.lua', 'ServerScriptService', 'Script'),
        ('NPCSpawner.lua', 'ServerScriptService', 'Script'),
        ('AnimationController.lua', 'ServerScriptService', 'Script'),
        ('ClientGUI.lua', 'StarterPlayer', 'LocalScript')
    ]
    
    scripts_injected = 0
    
    for script_file, parent_service, script_type in script_mappings:
        script_path = os.path.join(scripts_dir, script_file)
        if not os.path.exists(script_path):
            print(f"  ⚠️  Script not found: {script_file}")
            continue
            
        script_content = read_lua_file(script_path)
        if not script_content:
            continue
            
        script_name = script_file.replace('.lua', '')
        
        # Create script element
        script_elem = ET.SubElement(server_script_service, 'Item')
        script_elem.set('class', script_type)
        script_elem.set('referent', f'RBX{script_name}_{abs(hash(script_name))}')
        
        # Add properties
        props = ET.SubElement(script_elem, 'Properties')
        
        # Name property
        name_prop = ET.SubElement(props, 'string')
        name_prop.set('name', 'Name')
        name_prop.text = script_name
        
        # Source property (the actual Lua code)
        source_prop = ET.SubElement(props, 'ProtectedString')
        source_prop.set('name', 'Source')
        # Wrap in CDATA to preserve formatting
        source_prop.text = f'<![CDATA[{script_content}]]>'
        
        print(f"  ✅ Injected: {script_name} ({len(script_content)} bytes)")
        scripts_injected += 1
    
    # Write the modified XML
    print(f"\nWriting output to: {output_path}")
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    # Fix CDATA sections (ElementTree doesn't handle them well)
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace escaped CDATA markers
    content = content.replace('&lt;![CDATA[', '<![CDATA[')
    content = content.replace(']]&gt;', ']]>')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Successfully injected {scripts_injected} scripts into template")
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 inject-scripts-into-template.py <template.rbxl> <scripts-dir> <output.rbxl>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    scripts_dir = sys.argv[2]
    output_path = sys.argv[3]
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found: {template_path}")
        sys.exit(1)
        
    if not os.path.isdir(scripts_dir):
        print(f"ERROR: Scripts directory not found: {scripts_dir}")
        sys.exit(1)
    
    success = inject_scripts(template_path, scripts_dir, output_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()