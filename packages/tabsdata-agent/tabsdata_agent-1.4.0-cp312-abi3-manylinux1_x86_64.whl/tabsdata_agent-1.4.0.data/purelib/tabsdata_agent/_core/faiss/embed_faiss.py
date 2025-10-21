#
# Copyright 2025 Tabs Data Inc.
#

import glob
import os
import re
from textwrap import dedent

import yaml
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from tabsdata_agent._core.constants import faiss_index_folder

GENERATED_YAML_DIR = "../faiss/generated_yaml"


def get_subdirs(base_dir, prefix=None):
    """Return subdirectories (optionally filtered by prefix)."""
    return [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
        and (prefix is None or d.startswith(prefix))
    ]


# --- Safe YAML parsing for batched output ---
def safe_parse_yaml_batch(yaml_text):
    """
    Parses multiple YAML documents safely, removing empty docs and trimming whitespace.
    Returns a list of dicts.
    """
    documents = []
    for doc in yaml.safe_load_all(yaml_text):
        if doc is None:
            continue
        documents.append(doc)
    return documents


# --- Batched metadata generation ---
def generate_batch_metadata_with_llm(llm, batch_items):
    """
    batch_items: list of (dir_name, full_text)
    Returns: dict mapping dir_name -> metadata dict
    """
    items_text = []
    for dir_name, full_text in batch_items:
        items_text.append(f"# ITEM {dir_name}\n{full_text}")
    joined_text = "\n\n".join(items_text)

    example_yaml = dedent(
        """
    # Example for reference:
    id: example-13
    domain: Function examples
    title: Publish a Salesforce query result to a Tabsdata table
    summary: Demonstrates how to publish a Salesforce query result to a Tabsdata table.
    tags: [publisher, salesforce, api, single-table]
    kind: publisher
    type: SalesforceSource
    components: [Salesforce, TableFrame]
    """
    )

    prompt = dedent(
        f"""
        You are a Tabs Data assistant generating standardized YAML
        metadata for multiple code resources.

        Each code snippet is preceded by a line: "# ITEM <dir_name>"

        For each snippet, output a single YAML block following
        *exactly* this schema:

        id: <string>
        domain: Function examples # Always this exact string
        title: <string>
        summary: <string>
        tags: [<tag1>, <tag2>, ...]  # Output tags as a YAML array
        kind: <string>  # Only one of: publisher, subscriber, transformer
        type: <string>  # The type of connector used, or leave blank/unknown if not
        applicable
        components: [<string>, ...]

        Use the following example for formatting and value reference:
        {example_yaml}

        Output one YAML document per item, separated by '---' lines.
        DO NOT use block lists for tags. DO NOT use backticks, Markdown, or
        explanations.
        Start all top-level keys at column 0. YAML only.

        ITEMS:
        {joined_text}
    """
    )

    response = llm.invoke(prompt)
    content = response.content.strip()

    # Remove accidental leading/trailing backticks
    if content.startswith("```"):
        content = "\n".join(content.splitlines()[1:])
    if content.endswith("```"):
        content = "\n".join(content.splitlines()[:-1])

    # Ensure each document starts at column 0
    content = "\n".join(line.lstrip() for line in content.splitlines())

    try:
        documents = safe_parse_yaml_batch(content)
    except Exception as e:
        print(f"⚠️ Failed to parse batch YAML: {e}")
        return {}

    result = {}
    for i, (dir_name, _) in enumerate(batch_items):
        if i < len(documents) and isinstance(documents[i], dict):
            result[dir_name] = documents[i]
        else:
            print(f"⚠️ Missing or invalid metadata for {dir_name}, using fallback.")
            result[dir_name] = {
                "id": dir_name,
                "domain": "Function examples",
                "title": f"Function examples metadata for {dir_name}",
                "summary": "Automatically generated fallback metadata.",
                "tags": ["auto", "fallback"],
                "scenario": {"kind": "unknown", "type": "unknown", "components": []},
            }

    return result


def extract_demo_documents(example_dir):
    """Reads demo examples with existing metadata.yaml files."""
    docs = []
    meta_path = os.path.join(example_dir, "metadata.yaml")
    if not os.path.exists(meta_path):
        return docs

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = yaml.safe_load(f)

    text_parts = []
    for pyfile in glob.glob(os.path.join(example_dir, "functions", "*.py")):
        with open(pyfile, "r", encoding="utf-8") as f:
            text_parts.append(f.read())

    if text_parts:
        docs.append(Document(page_content="\n".join(text_parts), metadata=metadata))
    return docs


def discover_folders(base_dir, folder_pattern):
    print(
        f"🔎 Discovering folders in '{base_dir}' matching pattern '{folder_pattern}'..."
    )
    regex = re.compile(folder_pattern)
    folders = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and regex.match(d)
    ]
    print(f"  Found {len(folders)} folders.")
    return folders


def collect_documents(  # noqa: C901
    base_dir,
    folder_pattern,
    file_pattern,
    generated_yaml_dir,
    llm=None,
    batch_size=10,
):
    print(
        f"➡️ Processing tuple: base_dir='{base_dir}', "
        f"folder_pattern='{folder_pattern}', "
        f"file_pattern='{file_pattern}'"
    )
    folders = discover_folders(base_dir, folder_pattern)
    batch_items = []
    folder_names = []
    for folder in folders:
        text_parts = []
        # Recursively find all python files except __init__.py
        for root, dirs, files in os.walk(folder):
            for fname in files:
                if fname == "__init__.py":
                    continue  # Skip __init__.py files
                if re.fullmatch(file_pattern, fname):
                    fpath = os.path.join(root, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        text_parts.append(f.read())
        if text_parts:
            batch_items.append((os.path.basename(folder), "\n".join(text_parts)))
            folder_names.append(folder)
    print(f"  Found {len(batch_items)} folders with matching files.")
    documents = []
    for i in range(0, len(batch_items), batch_size):
        batch = batch_items[i : i + batch_size]
        batch_folder_names = folder_names[i : i + batch_size]
        # Determine which items need LLM generation
        batch_to_generate = []
        batch_to_generate_names = []
        batch_metadata = {}
        for (dir_name, full_text), folder_path in zip(batch, batch_folder_names):
            meta_path = os.path.join(folder_path, "metadata.yaml")
            yaml_path = os.path.join(generated_yaml_dir, f"{dir_name}.yaml")
            if os.path.exists(meta_path):
                print(f"      📄 Using metadata.yaml in {folder_path}")
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f)
                batch_metadata[dir_name] = metadata
            elif os.path.exists(yaml_path):
                print(
                    f"      📄 Using generated YAML: {yaml_path} (skipped generation)"
                )
                with open(yaml_path, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f)
                batch_metadata[dir_name] = metadata
            else:
                batch_to_generate.append((dir_name, full_text))
                batch_to_generate_names.append(
                    (dir_name, full_text, folder_path, yaml_path)
                )
        # Only call LLM if there are items to generate
        if batch_to_generate:
            print(
                f"    🟦 Generating metadata for {len(batch_to_generate)} items via"
                " LLM..."
            )
            batch_meta = (
                generate_batch_metadata_with_llm(llm, batch_to_generate) if llm else {}
            )
            for dir_name, full_text, folder_path, yaml_path in batch_to_generate_names:
                print(f"      📝 Generating and saving YAML: {yaml_path}")
                metadata = batch_meta.get(
                    dir_name,
                    {
                        "id": dir_name,
                        "domain": "Function examples",
                        "title": f"Function examples metadata for {dir_name}",
                        "summary": "Automatically generated fallback metadata.",
                        "tags": ["auto", "fallback"],
                        "scenario": {
                            "kind": "unknown",
                            "type": "unknown",
                            "components": [],
                        },
                    },
                )
                with open(yaml_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(metadata, f, sort_keys=False, allow_unicode=True)
                batch_metadata[dir_name] = metadata
        # Add all documents for this batch
        for (dir_name, full_text), folder_path in zip(batch, batch_folder_names):
            print(f"      ➕ Adding document for '{dir_name}'")
            documents.append(
                Document(page_content=full_text, metadata=batch_metadata[dir_name])
            )
    print(f"  ✅ Finished tuple: {len(documents)} documents collected.")
    return documents


def parse_input_tuples(input_tuples):
    """
    Parses a list of strings in the format base_dir:folder_pattern:file_pattern
    Returns a list of dicts with keys base_dir, folder_pattern, file_pattern
    """
    parsed = []
    for tup in input_tuples:
        parts = tup.split(":", 2)
        if len(parts) != 3:
            raise ValueError(
                f"Invalid input-tuple: {tup}. Expected format"
                " base_dir:folder_pattern:file_pattern"
            )
        parsed.append(
            {
                "base_dir": parts[0],
                "folder_pattern": parts[1],
                "file_pattern": parts[2],
            }
        )
    return parsed


def run_embedding_pipeline_multi(
    input_tuples,
    generated_yaml_dir,
    batch_size,
    llm_model="gpt-4",
    llm_temperature=0.1,
):
    print("🚀 Starting FAISS embedding pipeline...")
    llm = ChatOpenAI(model=llm_model, temperature=llm_temperature)
    if not os.path.exists(generated_yaml_dir):
        os.makedirs(generated_yaml_dir)
    all_docs = []
    for tup in input_tuples:
        docs = collect_documents(
            tup["base_dir"],
            tup["folder_pattern"],
            tup["file_pattern"],
            generated_yaml_dir,
            llm=llm,
            batch_size=batch_size,
        )
        all_docs.extend(docs)
    print(f"📦 Total documents for embedding: {len(all_docs)}")
    print("🔗 Generating embeddings and building FAISS index...")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(all_docs, embeddings)
    vectorstore.save_local(faiss_index_folder)
    print(f"✅ FAISS index saved to {faiss_index_folder}")


def load_config_yaml(config_path):
    """
    Loads configuration from a YAML file and expands env vars in base_dir.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Validate required keys
    if "input_tuples" not in config or not isinstance(config["input_tuples"], list):
        raise ValueError("Config file must contain 'input_tuples' as a list.")
    # Expand env vars in base_dir for each tuple
    for tup in config["input_tuples"]:
        raw_base_dir = tup["base_dir"]
        resolved_base_dir = os.path.expandvars(raw_base_dir)
        tup["base_dir"] = resolved_base_dir
        if not os.path.exists(resolved_base_dir):
            print(
                f"⚠️ Warning: Resolved base_dir '{resolved_base_dir}' does not exist"
                f" (from '{raw_base_dir}')"
            )
        else:
            print(f"🔗 Resolved base_dir: '{raw_base_dir}' -> '{resolved_base_dir}'")
    return config


def main():
    # Use config.yaml in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found.")
    config = load_config_yaml(config_path)

    # Ensure generated_yaml_dir is at the same level as this file
    gen_yaml_dir = config.get("generated_yaml_dir", "generated_yaml")
    if not os.path.isabs(gen_yaml_dir):
        gen_yaml_dir = os.path.join(script_dir, gen_yaml_dir)
    config["generated_yaml_dir"] = gen_yaml_dir

    config.setdefault("batch_size", 10)
    config.setdefault("llm_model", "gpt-4")
    config.setdefault("llm_temperature", 0.1)

    # input_tuples is now a list of dicts
    run_embedding_pipeline_multi(
        config["input_tuples"],
        config["generated_yaml_dir"],
        config["batch_size"],
        config["llm_model"],
        config["llm_temperature"],
    )


if __name__ == "__main__":
    main()
