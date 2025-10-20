import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag, NavigableString
from openai import AzureOpenAI
from dotenv import load_dotenv
import re
import urllib.parse
import argparse
import json
import subprocess

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
)

def get_provider_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    path_segments = parsed_url.path.split('/')
    if 'learn.microsoft.com' in parsed_url.netloc and '/rest/api/' in parsed_url.path:
        return 'azapi'
    try:
        provider_index = path_segments.index('providers')
        if provider_index + 2 < len(path_segments):
            return path_segments[provider_index + 2]
    except ValueError:
        pass
    return None

def get_module_path(url):
    provider = get_provider_from_url(url)
    if not provider:
        raise ValueError("Could not determine provider from URL")

    parsed_url = urllib.parse.urlparse(url)
    path_segments = parsed_url.path.split('/')

    if provider == 'azapi':
        # For Azure REST API URLs, extract resource type from the path
        # Example: .../rest/api/containerregistry/registries/create
        try:
            api_index = path_segments.index('api')
            # The next segment is the service, the one after is the resource type
            if api_index + 2 < len(path_segments):
                service = path_segments[api_index + 1]
                resource_type = path_segments[api_index + 2]
                pascal_case_name = f"{service.capitalize()}{resource_type.capitalize()}"
                module_name = f"Azure.{pascal_case_name}"
                return os.path.join('modules', provider, module_name)
        except ValueError:
            pass
        raise ValueError("Could not extract resource type from Azure REST API URL")

    # Existing logic for Terraform Registry URLs
    resource_name_snake_case = None
    for i, segment in enumerate(path_segments):
        if segment == 'resources' and i + 1 < len(path_segments):
            resource_name_snake_case = path_segments[i+1]
            break

    if not resource_name_snake_case:
        raise ValueError("Could not extract resource name from URL")

    pascal_case_name = ''.join(word.capitalize() for word in resource_name_snake_case.split('_'))
    if provider == 'azurerm':
        module_name = f"Azure.{pascal_case_name}"
    else:
        module_name = pascal_case_name

    return os.path.join('modules', provider, module_name)

async def download_azapi_doc(url: str) -> str:
    print(f"\nFetching AzAPI REST documentation from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("load")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Extract msDocs.data.restAPIData JSON
        rest_data_script = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script'));
                for (const script of scripts) {
                    const text = script.textContent;
                    if (text.includes('msDocs.data.restAPIData')) {
                        const jsonText = text.split('msDocs.data.restAPIData = ')[1].split(';')[0];
                        return jsonText;
                    }
                }
                return null;
            }
        """)
        await browser.close()

        md_lines = ["## URI Parameters\n"]
        if not rest_data_script:
            raise Exception("Failed to extract msDocs REST data.")

        rest_data = json.loads(rest_data_script)
        for param in rest_data.get("uriParameters", []):
            name = param["name"]
            required = "required" if param.get("isRequired") else "optional"
            typ = param.get("type", "string")
            md_lines.append(f"- **`{name}`** *(type: {typ}, {required})*")

        # Request Body
        md_lines.append("\n## Request Body\n")
        body_section = soup.find("h2", {"id": "request-body"})
        table = body_section.find_next("table") if body_section else None
        if not table:
            md_lines.append("- *(Request body section not found)*")
        else:
            rows = table.find_all("tr")
            if len(rows) <= 1:
                # Only header row, no data
                md_lines.append("- *(Request body table is present but contains no parameters)*")
            else:
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        name = cols[0].get_text(strip=True).replace("\n", "").replace("\xa0", " ")
                        typ = cols[1].get_text(strip=True)
                        desc = cols[2].get_text(strip=True).replace("\n", " ")
                        md_lines.append(f"- **`{name}`** *(type: {typ})* – {desc}")

        return "\n".join(md_lines)

def html_to_markdown(elem):
    # Convert HTML element to Markdown recursively with improved formatting
    if elem.name in ['ul', 'ol']:
        return list_to_md(elem)
    if elem.name == 'li':
        return li_to_md(elem)
    if elem.name in ['h3', 'h4', 'h5', 'h6']:
        level = int(elem.name[1])
        return f"{'#' * level} {elem.get_text(strip=True)}"
    if elem.name == 'pre':
        code = elem.get_text('\n', strip=True)
        return f"\n```hcl\n{code}\n```\n"
    if elem.name == 'code':
        return f"`{elem.get_text(strip=True)}`"
    if elem.name == 'p':
        return p_to_md(elem)
    if elem.name == 'div' and 'alert' in elem.get('class', []):
        # Note or warning block - flatten to a single paragraph
        note_type = 'Note' if 'alert-info' in elem.get('class', []) else 'Warning'
        text = flatten_alert(elem)
        return f"> **{note_type}:** {text}"
    if elem.name == 'hr':
        return '\n---\n'
    if elem.name == 'a':
        # Remove anchor references from links but keep brackets for internal links
        href = elem.get('href', '')
        if href.startswith('#'):
            return f"[{elem.get_text(strip=True)}]"
        return f"[{elem.get_text(strip=True)}]({href})"
    # Generic recursive conversion for other tags
    content_parts = []
    for child in elem.children:
        if isinstance(child, Tag):
            content_parts.append(html_to_markdown(child))
        elif isinstance(child, NavigableString):
            s = str(child).strip()
            if s:
                content_parts.append(s)
    return ' '.join(content_parts).strip()

def flatten_alert(alert_elem):
    # Flatten all text and inline code in the alert into a single paragraph
    parts = []
    for child in alert_elem.descendants:
        if isinstance(child, Tag) and child.name == 'code':
            parts.append(f'`{child.get_text(strip=True)}`')
        elif isinstance(child, Tag) and child.name == 'br':
            parts.append(' ')
        elif isinstance(child, NavigableString):
            s = str(child).replace('\n', ' ').strip()
            if s:
                parts.append(s)
    # Remove extra spaces and join
    text = ' '.join(parts)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def list_to_md(ul_elem):
    items = []
    for li in ul_elem.find_all('li', recursive=False):
        items.append(li_to_md(li))
    return '\n'.join(items)

def li_to_md(li_elem):
    # Try to bold and code the argument name and process children recursively
    text_parts = []
    for child in li_elem.children:
        if isinstance(child, Tag) and child.name == 'a' and child.code:
            arg = child.get_text(strip=True)
            href = child.get('href', '')
            if href and not href.startswith('#'):  # Only keep non-anchor links
                text_parts.append(f'**[`{arg}`]({href})**')
            else:
                text_parts.append(f'**[{arg}]**')  # Keep square brackets but remove anchor
        elif isinstance(child, Tag) and child.name == 'code':
            text_parts.append(f'**`{child.get_text(strip=True)}`**')
        elif isinstance(child, NavigableString):
            s = str(child)
            dash_idx = s.find('-')
            if dash_idx > 0:
                arg_part = s[:dash_idx].strip()
                desc_part = s[dash_idx+1:].strip()
                if arg_part:
                    text_parts.append(f'**[{arg_part}]** – {desc_part}')
                else:
                    text_parts.append(desc_part)
            else:
                text_parts.append(s)
        elif isinstance(child, Tag):
            # Recursively convert nested tags within <li>
            text_parts.append(html_to_markdown(child))

    return f'- {' '.join(text_parts).strip()}'

def p_to_md(p_elem):
    # Convert <p> with possible <code> and <a> children recursively
    out_parts = []
    for child in p_elem.children:
        if isinstance(child, Tag) and child.name == 'code':
            out_parts.append(f'`{child.get_text(strip=True)}`')
        elif isinstance(child, Tag) and child.name == 'a':
            label = child.get_text(strip=True)
            href = child.get('href', '')
            if href and not href.startswith('#'):  # Only keep non-anchor links
                out_parts.append(f'[{label}]({href})')
            else:
                out_parts.append(label)
        elif isinstance(child, Tag):
            # Recursively convert nested tags within <p>
            out_parts.append(html_to_markdown(child))
        else:
            out_parts.append(str(child))
    return ' '.join(out_parts).strip()

def fetch_schema_block(provider: str, resource: str):
    import tempfile
    import subprocess
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "main.tf"), "w") as f:
                f.write(f"""
terraform {{
  required_providers {{
    {provider} = {{
      source  = "hashicorp/{provider}"
    }}
  }}
}}

provider "{provider}" {{}}

resource "{provider}_{resource}" "dummy" {{}}
""")
            subprocess.run(["terraform", "init", "-input=false", "-no-color"], cwd=tmpdir, check=True, stdout=subprocess.DEVNULL)
            result = subprocess.run(["terraform", "providers", "schema", "-json"], cwd=tmpdir, capture_output=True, check=True)
            schema = json.loads(result.stdout)
            provider_key = next(iter(schema["provider_schemas"]))
            resource_key = f"{provider}_{resource}"
            return schema["provider_schemas"][provider_key]["resource_schemas"].get(resource_key)
    except Exception as e:
        print(f"⚠️ Failed to fetch schema for {provider}_{resource}: {e}")
        return None

def split_and_save_outputs(gpt_output, module_dir):
    sections = {
        'main.tf': '',
        'variables.tf': '',
        'outputs.tf': ''
    }
    current_section = None
    code_lines = []
    for line in gpt_output.splitlines():
        header_match = re.match(r'^#+\s*(main|variables|outputs)\.tf', line.strip().lower())
        if header_match:
            if current_section and code_lines:
                content = '\n'.join(code_lines).strip()
                content = re.sub(r'^```hcl', '', content, flags=re.IGNORECASE).strip()
                content = re.sub(r'^```', '', content, flags=re.IGNORECASE).strip()
                content = re.sub(r'```$', '', content, flags=re.IGNORECASE).strip()
                sections[current_section] = content
            section_name = header_match.group(1) + '.tf'
            current_section = section_name
            code_lines = []
        elif current_section:
            code_lines.append(line)
    if current_section and code_lines:
        content = '\n'.join(code_lines).strip()
        content = re.sub(r'^```hcl', '', content, flags=re.IGNORECASE).strip()
        content = re.sub(r'^```', '', content, flags=re.IGNORECASE).strip()
        content = re.sub(r'```$', '', content, flags=re.IGNORECASE).strip()
        sections[current_section] = content
    os.makedirs(module_dir, exist_ok=True)
    print(f"\n💾 Saving generated files to {module_dir}/...\n")
    for fname, content in sections.items():
        file_path = os.path.join(module_dir, fname)
        if content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✅ Saved {file_path} ({len(content)} characters)')
        else:
            print(f'Warning: {file_path} is empty or missing in GPT output')
    print('✅ Done!')

def validate_terraform_module(module_dir):
    """Run terraform init and validate on the generated module"""
    print(f"\n🔧 Validating Terraform module in {module_dir}...")
    
    try:
        # Run terraform init
        print("Running terraform init...")
        init_result = subprocess.run(
            ["terraform", "init", "-input=false", "-no-color"],
            cwd=module_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if init_result.returncode != 0:
            print(f"❌ terraform init failed:")
            print(f"STDOUT: {init_result.stdout}")
            print(f"STDERR: {init_result.stderr}")
            return False, f"terraform init failed:\nSTDOUT: {init_result.stdout}\nSTDERR: {init_result.stderr}"
        else:
            print("✅ terraform init successful")
        
        # Run terraform validate
        print("Running terraform validate...")
        validate_result = subprocess.run(
            ["terraform", "validate", "-no-color"],
            cwd=module_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if validate_result.returncode != 0:
            print(f"❌ terraform validate failed:")
            print(f"STDOUT: {validate_result.stdout}")
            print(f"STDERR: {validate_result.stderr}")
            error_output = f"terraform validate failed:\nSTDOUT: {validate_result.stdout}\nSTDERR: {validate_result.stderr}"
            return False, error_output
        else:
            print("✅ terraform validate successful")
            print("🎉 Module validation completed successfully!")
            return True, None
            
    except FileNotFoundError:
        print("❌ Error: terraform command not found. Please ensure Terraform is installed and in your PATH.")
        return False, "terraform command not found"
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False, str(e)

async def generate_examples_with_gpt(module_dir, url, schema_text, doc_text=""):
    """Generate examples folder using AI based on the module files and schema"""
    print(f"\n📁 Generating examples folder with AI for {module_dir}...")
    
    try:
        # Read the generated module files
        module_files = {}
        for filename in ['main.tf', 'variables.tf', 'outputs.tf']:
            file_path = os.path.join(module_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    module_files[filename] = f.read()
        
        # Extract provider and resource info
        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.split("/")
        
        if get_provider_from_url(url) == "azapi":
            try:
                api_index = path_parts.index('api')
                service = path_parts[api_index + 1]
                resource = path_parts[api_index + 2]
                provider = "azapi"
            except:
                provider = "azapi"
                resource = "resource"
        else:
            try:
                provider = path_parts[path_parts.index("providers") + 2]
                resource = path_parts[path_parts.index("resources") + 1]
            except:
                provider = "unknown"
                resource = "resource"
        
        # Create AI prompt for examples generation
        system_prompt = (
            f"You are creating example usage files for a Terraform module `{provider}_{resource}`.\n"
            f"Below are the generated module files and the provider schema.\n"
            f"Create complete example usage in an 'examples' folder with:\n"
            f"1. main.tf - Complete working example that calls the module with all parameters\n"
            f"2. variables.tf - Variable definitions for the example (same as module but for example usage)\n"
            f"3. terraform.tfvars - Example values for all variables\n\n"
            f"## Module Files:\n"
        )
        
        for filename, content in module_files.items():
            system_prompt += f"### {filename}\n```hcl\n{content}\n```\n\n"
        
        system_prompt += (
            f"## Provider Schema:\n{schema_text}\n\n"
            f"## Documentation:\n{doc_text}\n\n"
            f"Generate realistic example values. For required variables, provide actual values in terraform.tfvars.\n"
            f"For optional variables, provide commented examples in terraform.tfvars.\n"
            f"The main.tf should call the module using source = \"..\" (parent directory).\n"
            f"Output the files with these headers exactly:\n"
            f"### examples/main.tf\n...\n### examples/variables.tf\n...\n### examples/terraform.tfvars\n...\n"
        )
        
        endpoint = os.getenv("ENDPOINT_URL")
        deployment = "gpt-5-mini"
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=subscription_key, api_version="2025-01-01-preview")
        
        chat_prompt = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": "Generate the example files for this Terraform module."}]}
        ]
        
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_completion_tokens=30000,
            temperature=1,
            top_p=1,
        )
        
        if completion.choices:
            examples_output = completion.choices[0].message.content.strip()
            return save_examples_output(examples_output, module_dir)
        else:
            print("❌ AI did not return examples output.")
            return None
            
    except Exception as e:
        print(f"❌ Error generating examples with AI: {e}")
        return None

def save_examples_output(examples_output, module_dir):
    """Parse and save the AI-generated examples output"""
    examples_dir = os.path.join(module_dir, 'examples')
    os.makedirs(examples_dir, exist_ok=True)
    
    sections = {
        'main.tf': '',
        'variables.tf': '',
        'terraform.tfvars': ''
    }
    
    current_section = None
    code_lines = []
    
    for line in examples_output.splitlines():
        # Look for headers like "### examples/main.tf"
        header_match = re.match(r'^#+\s*examples/(main\.tf|variables\.tf|terraform\.tfvars)', line.strip().lower())
        if header_match:
            if current_section and code_lines:
                content = '\n'.join(code_lines).strip()
                # Clean up code blocks
                content = re.sub(r'^```hcl', '', content, flags=re.IGNORECASE).strip()
                content = re.sub(r'^```', '', content, flags=re.IGNORECASE).strip()
                content = re.sub(r'```$', '', content, flags=re.IGNORECASE).strip()
                sections[current_section] = content
            
            current_section = header_match.group(1)
            code_lines = []
        elif current_section:
            code_lines.append(line)
    
    # Handle the last section
    if current_section and code_lines:
        content = '\n'.join(code_lines).strip()
        content = re.sub(r'^```hcl', '', content, flags=re.IGNORECASE).strip()
        content = re.sub(r'^```', '', content, flags=re.IGNORECASE).strip()
        content = re.sub(r'```$', '', content, flags=re.IGNORECASE).strip()
        sections[current_section] = content
    
    # Save the files
    print(f"\n💾 Saving examples to {examples_dir}/...\n")
    for filename, content in sections.items():
        if content:
            file_path = os.path.join(examples_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✅ Created {file_path} ({len(content)} characters)')
        else:
            print(f'⚠️ Warning: {filename} is empty or missing in AI output')
    
    print(f'✅ Examples folder created successfully!')
    return examples_dir

async def fix_examples_with_gpt(module_dir, url, schema_text, doc_text, error_context):
    """Fix examples validation errors using AI"""
    print(f"\n🔧 Fixing examples validation errors with AI...")
    
    try:
        # Read the current module files and examples files
        module_files = {}
        examples_files = {}
        
        # Read module files
        for filename in ['main.tf', 'variables.tf', 'outputs.tf']:
            file_path = os.path.join(module_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    module_files[filename] = f.read()
        
        # Read examples files
        examples_dir = os.path.join(module_dir, 'examples')
        for filename in ['main.tf', 'variables.tf', 'terraform.tfvars']:
            file_path = os.path.join(examples_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    examples_files[filename] = f.read()
        
        # Extract provider and resource info
        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.split("/")
        
        if get_provider_from_url(url) == "azapi":
            try:
                api_index = path_parts.index('api')
                service = path_parts[api_index + 1]
                resource = path_parts[api_index + 2]
                provider = "azapi"
            except:
                provider = "azapi"
                resource = "resource"
        else:
            try:
                provider = path_parts[path_parts.index("providers") + 2]
                resource = path_parts[path_parts.index("resources") + 1]
            except:
                provider = "unknown"
                resource = "resource"
        
        # Create AI prompt for fixing examples
        system_prompt = (
            f"You are fixing example usage files for a Terraform module `{provider}_{resource}` that have validation errors.\n"
            f"Below are the module files, current examples files, provider schema, and validation errors.\n"
            f"Fix the validation errors in the examples while maintaining proper usage of the module.\n\n"
            f"## Module Files:\n"
        )
        
        for filename, content in module_files.items():
            system_prompt += f"### {filename}\n```hcl\n{content}\n```\n\n"
        
        system_prompt += f"## Current Examples Files:\n"
        for filename, content in examples_files.items():
            system_prompt += f"### examples/{filename}\n```hcl\n{content}\n```\n\n"
        
        system_prompt += (
            f"## Provider Schema:\n{schema_text}\n\n"
            f"## Documentation:\n{doc_text}\n\n"
            f"## Terraform Validation Errors:\n{error_context}\n\n"
            f"Fix these validation errors in the examples. The examples should properly call the module.\n"
            f"Output the corrected example files with these headers exactly:\n"
            f"### examples/main.tf\n...\n### examples/variables.tf\n...\n### examples/terraform.tfvars\n...\n"
        )
        
        endpoint = os.getenv("ENDPOINT_URL")
        deployment = "gpt-5-mini"
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=subscription_key, api_version="2025-01-01-preview")
        
        chat_prompt = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": "Fix the validation errors in the example files."}]}
        ]
        
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_completion_tokens=30000,
            temperature=1,
            top_p=1,
        )
        
        if completion.choices:
            return completion.choices[0].message.content.strip()
        else:
            print("❌ AI did not return fixed examples output.")
            return None
            
    except Exception as e:
        print(f"❌ Error fixing examples with AI: {e}")
        return None

async def create_examples_with_ai(module_path, url):
    """Helper function to create examples using AI with proper schema context"""
    try:
        # Extract provider and resource info to get schema
        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.split("/")
        
        if get_provider_from_url(url) == "azapi":
            # For azapi, use documentation
            doc_text = await download_azapi_doc(url)
            schema_text = "Schema not available for AzAPI."
        else:
            try:
                provider = path_parts[path_parts.index("providers") + 2]
                resource = path_parts[path_parts.index("resources") + 1]
                schema_block = fetch_schema_block(provider, resource)
                schema_text = json.dumps(schema_block, indent=2) if schema_block else "Schema not available."
                doc_text = ""
            except Exception as e:
                print(f"⚠️ Could not extract provider/resource info: {e}")
                schema_text = "Schema not available."
                doc_text = ""
        
        # Generate examples with AI
        examples_dir = await generate_examples_with_gpt(module_path, url, schema_text, doc_text)
        
        # Validate the examples folder if it was created successfully
        if examples_dir:
            print(f"\n🔧 Validating examples in {examples_dir}...")
            examples_validation, examples_error = validate_terraform_module(examples_dir)
            if examples_validation:
                print("🎉 Examples validation successful!")
            else:
                print(f"⚠️ Examples validation failed. Attempting to fix with AI...")
                
                # Keep trying to fix with AI until successful or max attempts reached
                max_attempts = 5
                current_error = examples_error
                
                for attempt in range(1, max_attempts + 1):
                    print(f"\n🔧 AI fix attempt {attempt}/{max_attempts}...")
                    fixed_examples = await fix_examples_with_gpt(module_path, url, schema_text, doc_text, current_error)
                    
                    if fixed_examples:
                        print(f"\n💾 Saving fixed examples (attempt {attempt})...")
                        save_examples_output(fixed_examples, module_path)
                        
                        # Re-validate examples
                        print(f"\n🔧 Re-validating fixed examples (attempt {attempt})...")
                        validation_success, validation_error = validate_terraform_module(examples_dir)
                        
                        if validation_success:
                            print(f"\n🎉 Examples successfully fixed and validated on attempt {attempt}!")
                            break
                        else:
                            print(f"\n⚠️ Attempt {attempt} still has validation errors:")
                            print(validation_error)
                            current_error = validation_error
                            
                            if attempt == max_attempts:
                                print(f"\n❌ Failed to fix examples after {max_attempts} attempts.")
                                print("Final errors:")
                                print(validation_error)
                            else:
                                print(f"Trying again with attempt {attempt + 1}...")
                    else:
                        print(f"❌ AI could not generate fixed examples on attempt {attempt}.")
                        if attempt == max_attempts:
                            print(f"\n❌ Failed to generate fixed examples after {max_attempts} attempts.")
        
    except Exception as e:
        print(f"❌ Error creating examples: {e}")

async def generate_module_with_gpt(doc_text, azapi_mode=False, url=None, error_context=None):
    try:
        endpoint = os.getenv("ENDPOINT_URL")
        deployment = "gpt-5-mini"
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=subscription_key, api_version="2025-01-01-preview")

        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.split("/")

        if get_provider_from_url(url) == "azapi":
            try:
                api_index = path_parts.index('api')
                service = path_parts[api_index + 1]
                resource = path_parts[api_index + 2]
                provider = "azapi"
            except Exception as e:
                print(f"❌ Error: Could not extract service/resource from Azure REST API URL '{url}'. Please check the URL format. ({e})")
                return None
            # For azapi, use documentation parsing
            doc_text = await download_azapi_doc(url)
            schema_text = "Schema not available."
            print("\n===== PARSED AZAPI DOCUMENTATION =====\n")
            print(doc_text)
            print("\n===== END PARSED AZAPI DOCUMENTATION =====\n")
        else:
            try:
                provider = path_parts[path_parts.index("providers") + 2]
                resource = path_parts[path_parts.index("resources") + 1]
            except Exception as e:
                print(f"❌ Error: Could not extract provider/resource from URL '{url}'. Please check the URL format. ({e})")
                return None
            schema_block = fetch_schema_block(provider, resource)
            schema_text = json.dumps(schema_block, indent=2) if schema_block else "Schema not available."
            doc_text = ""
            print("\n===== PROVIDER SCHEMA JSON =====\n")
            print(schema_text)
            print("\n===== END PROVIDER SCHEMA JSON =====\n")

        if error_context:
            # This is a fix attempt
            system_prompt = (
                f"You are fixing a Terraform module for resource `{provider}_{resource}` that has validation errors.\n"
                f"Below is the Terraform provider **schema** and the validation errors.\n"
                f"Check the JSON schema and fix these errors. Only use arguments and blocks defined in the schema.\n\n"
                f"## Schema JSON:\n{schema_text}\n\n"
                f"## Documentation:\n{doc_text}\n\n"
                f"## Terraform Validation Errors:\n{error_context}\n\n"
                f"Output the corrected files below. No explanations. Use these headers exactly:\n"
                f"For variables make sure to use the correct type and default value if available.\n"
                f"If the parameter is required, dont add a default value and if the parameter is optional, add a default value.\n"
                f"### main.tf\n...\n### variables.tf\n...\n### outputs.tf\n...\n"
            )
            user_prompt = "Check the JSON schema and fix these errors in the Terraform module."
        else:
            # This is initial generation
            system_prompt = (
                f"You are generating a Terraform module for resource `{provider}_{resource}`.\n"
                f"Below is the Terraform provider **schema** (if available) and documentation.\n"
                f"Only use arguments and blocks defined in the schema or documentation.\n\n"
                f"## Schema JSON:\n{schema_text}\n\n"
                f"## Documentation:\n{doc_text}\n\n"
                f"Output files below. No explanations. Use these headers exactly:\n"
                f"For variables make sure to use the correct type and default value if available.\n"
                f"If a block has multiple arguments, make sure to use to correct type.\n" 
                f"If the parameter is required, dont add a default value and if the parameter is optional, add a default value.\n"
                f"### main.tf\n...\n### variables.tf\n...\n### outputs.tf\n...\n"
            )
            user_prompt = "Generate the Terraform module now."

        chat_prompt = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
        ]
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_completion_tokens=30000,
            temperature=1,
            top_p=1,
        )
        return completion.choices[0].message.content.strip() if completion.choices else None
    except Exception as e:
        print(f"❌ AI generation error: {e}")
        return None

async def main():
    try:
        parser = argparse.ArgumentParser(description="Generate Terraform modules from documentation.")
        parser.add_argument('--url', type=str, help='Direct URL to the Terraform resource documentation.')
        parser.add_argument('--generate', action='store_true', help='Generate Terraform files using AI after downloading documentation.')
        args = parser.parse_args()
        if args.url:
            url = args.url
        else:
            url = input("🔗 Enter Terraform resource URL: ").strip()
        if not url:
            raise ValueError("URL cannot be empty")
        module_path = get_module_path(url)
        if args.generate:
            print("\n⚡ Generating Terraform files with AI...\n")
            azapi_mode = get_provider_from_url(url) == "azapi"
            gpt_output = await generate_module_with_gpt("", azapi_mode=azapi_mode, url=url)
            if gpt_output:
                split_and_save_outputs(gpt_output, module_path)
                print("\n🎉 Terraform files generated and saved!")
                
                # Validate the generated module
                validation_success, error_output = validate_terraform_module(module_path)
                if not validation_success:
                    print("\n⚠️ Module validation failed. Attempting to fix errors with AI...")
                    
                    # Keep trying to fix with AI until successful or max attempts reached
                    max_attempts = 5
                    current_error = error_output
                    module_fixed = False
                    
                    for attempt in range(1, max_attempts + 1):
                        print(f"\n🔧 AI fix attempt {attempt}/{max_attempts}...")
                        fixed_output = await generate_module_with_gpt("", azapi_mode=azapi_mode, url=url, error_context=current_error)
                        
                        if fixed_output:
                            print(f"\n💾 Saving fixed files (attempt {attempt})...")
                            split_and_save_outputs(fixed_output, module_path)
                            
                            # Re-validate module
                            print(f"\n🔧 Re-validating fixed module (attempt {attempt})...")
                            validation_success, validation_error = validate_terraform_module(module_path)
                            
                            if validation_success:
                                print(f"\n🎉 Module successfully fixed and validated on attempt {attempt}!")
                                module_fixed = True
                                break
                            else:
                                print(f"\n⚠️ Attempt {attempt} still has validation errors:")
                                print(validation_error)
                                current_error = validation_error
                                
                                if attempt == max_attempts:
                                    print(f"\n❌ Failed to fix module after {max_attempts} attempts.")
                                    print("Final errors:")
                                    print(validation_error)
                                else:
                                    print(f"Trying again with attempt {attempt + 1}...")
                        else:
                            print(f"❌ AI could not generate fixed module on attempt {attempt}.")
                            if attempt == max_attempts:
                                print(f"\n❌ Failed to generate fixed module after {max_attempts} attempts.")
                    
                    # Create examples only if module was successfully fixed
                    if module_fixed:
                        await create_examples_with_ai(module_path, url)
                else:
                    # Initial validation was successful
                    await create_examples_with_ai(module_path, url)
            else:
                print("❌ AI did not return any output.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())