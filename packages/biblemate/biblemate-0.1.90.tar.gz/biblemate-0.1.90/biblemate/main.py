from biblemate.core.systems import *
from biblemate.uba.dialogs import *
from biblemate.ui.text_area import getTextArea
from biblemate.ui.info import get_banner
from biblemate import config, DIALOGS, BIBLEMATE_VERSION, AGENTMAKE_CONFIG, BIBLEMATE_USER_DIR, BIBLEMATEDATA, fix_string, write_user_config, list_dir_content
from biblemate.uba.api import DEFAULT_MODULES, run_uba_api, run_uba_ai_commentary, run_uba_words, run_uba_discourse, run_uba_translation
from pathlib import Path
import urllib.parse
import asyncio, re, os, subprocess, click, gdown, pprint, argparse, json, zipfile, warnings, sys
from copy import deepcopy
from alive_progress import alive_bar
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake import agentmake, getOpenCommand, getDictionaryOutput, edit_file, edit_configurations, readTextFile, writeTextFile, getCurrentDateTime, AGENTMAKE_USER_DIR, USER_OS, DEVELOPER_MODE, DEFAULT_AI_BACKEND, DEFAULT_TEXT_EDITOR
from agentmake.utils.files import searchFolder, isExistingPath
from agentmake.etextedit import launch_async
from agentmake.utils.manage_package import getPackageLatestVersion
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.terminal_theme import MONOKAI
from prompt_toolkit.shortcuts import set_title, clear_title
from prompt_toolkit.completion import PathCompleter
from packaging import version
if not USER_OS == "Windows":
    import readline  # for better input experience

# set window title
set_title(f"BibleMate AI")

parser = argparse.ArgumentParser(description = f"""BibleMate AI {BIBLEMATE_VERSION} CLI options""")
# global options
parser.add_argument("default", nargs="*", default=None, help="initial prompt")
parser.add_argument("-b", "--backend", action="store", dest="backend", help="AI backend; overrides the default backend temporarily.")
parser.add_argument("-l", "--lite", action="store", dest="lite", choices=["true", "false"], help="Enable / disable lite context. Must be one of: true, false.")
parser.add_argument("-m", "--mode", action="store", dest="mode", choices=["agent", "partner", "chat"], help="Specify AI mode. Must be one of: agent, partner, chat.")
parser.add_argument("-pe", "--promptengineer", action="store", dest="promptengineer", choices=["true", "false"], help="Enable / disable prompt engineering. Must be one of: true, false.")
parser.add_argument("-s", "--steps", action="store", dest="steps", type=int, help="Specify the maximum number of steps allowed.")
parser.add_argument("-e", "--exit", action="store_true", dest="exit", help="exit after the first response (for single-turn use cases).")
# mcp options
parser.add_argument("-t", "--token", action="store", dest="token", help="specify a static token to use for authentication with the MCP server; applicable to command `biblemate` only")
parser.add_argument("-mcp", "--mcp", action="store", dest="mcp", help=f"specify a custom MCP server to use, e.g. 'http://127.0.0.1:{config.mcp_port}/mcp/'; applicable to command `biblemate` only")
parser.add_argument("-p", "--port", action="store", dest="port", help=f"specify a port for the MCP server to use, e.g. {config.mcp_port}; applicable to command `biblematemcp` only")
args = parser.parse_args()

if not sys.stdin.isatty():
    stdin_text = sys.stdin.read()
    if args.default:
        args.default.append(stdin_text)
    else:
        args.default = [stdin_text]

# write to the `config.py` file temporarily for the MCP server to pick it up
if args.backend:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.py"), "a", encoding="utf-8") as fileObj:
        fileObj.write(f'''\nbackend="{args.backend}"''')
    config.backend = args.backend
else:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.py"), "a", encoding="utf-8") as fileObj:
        fileObj.write(f'''\nbackend="{DEFAULT_AI_BACKEND}"''')
    config.backend = DEFAULT_AI_BACKEND

AGENTMAKE_CONFIG["backend"] = config.backend
DEFAULT_SYSTEM = "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."
DEFAULT_MESSAGES = [{"role": "system", "content": DEFAULT_SYSTEM}, {"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hello! I'm BibleMate AI, your personal assistant for Bible study. How can I help you today?"}] # set a tone for bible study; it is userful when auto system is used.
FINAL_INSTRUCTION = """# Instruction
Please provide me with the final answer to my original request based on the work that has been completed.

# Original Request
"""

# other temporary config changes
if args.lite == "true":
    config.lite = True
elif args.lite == "false":
    config.lite = False
if args.mode == "agent":
    config.agent_mode = True
elif args.mode == "partner":
    config.agent_mode = False
elif args.mode == "chat":
    config.agent_mode = None
if args.promptengineer == "true":
    config.prompt_engineering = True
elif args.promptengineer == "false":
    config.prompt_engineering = False
if args.steps:
    config.max_steps = args.steps

def mcp():
    builtin_mcp_server = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bible_study_mcp.py")
    user_mcp_server = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "bible_study_mcp.py") # The user path has the same basename as the built-in one; users may copy the built-in server settings to this location for customization. 
    mcp_script = readTextFile(user_mcp_server if os.path.isfile(user_mcp_server) else builtin_mcp_server)
    mcp_script = mcp_script.replace("mcp.run(show_banner=False)", f'''mcp.run(show_banner=False, transport="http", host="0.0.0.0", port={args.port if args.port else config.mcp_port})''')
    exec(mcp_script)

def main():
    asyncio.run(main_async())

async def initialize_app(client):
    """Initializes the application by fetching tools and prompts from the MCP server."""
    await client.ping()

    tools_raw = await client.list_tools()
    tools = {t.name: t.description for t in tools_raw}
    tools = dict(sorted(tools.items()))
    tools_schema = {}
    for t in tools_raw:
        schema = {
            "name": t.name,
            "description": t.description,
            "parameters": {
                "type": "object",
                "properties": t.inputSchema.get("properties", {}),
                "required": t.inputSchema.get("required", []),
            },
        }
        tools_schema[t.name] = schema

    available_tools = list(tools.keys())
    if "get_direct_text_response" not in available_tools:
        available_tools.insert(0, "get_direct_text_response")
    master_available_tools = deepcopy(available_tools)
    available_tools = [i for i in available_tools if not i in config.disabled_tools]

    tool_descriptions = ""
    if "get_direct_text_response" not in tools:
        tool_descriptions = """# TOOL DESCRIPTION: `get_direct_text_response`
Get a static text-based response directly from a text-based AI model without using any other tools. This is useful when you want to provide a simple and direct answer to a question or request, without the need for online latest updates or task execution."""
    for tool_name, tool_description in tools.items():
        tool_descriptions += f"""# TOOL DESCRIPTION: `{tool_name}`
{tool_description}\n\n\n"""

    prompts_raw = await client.list_prompts()
    prompts = {p.name: p.description for p in prompts_raw}
    prompts = dict(sorted(prompts.items()))

    prompts_schema = {}
    for p in prompts_raw:
        arg_properties = {}
        arg_required = []
        for a in p.arguments:
            arg_properties[a.name] = {
                "type": "string",
                "description": str(a.description) if a.description else "no description available",
            }
            if a.required:
                arg_required.append(a.name)
        schema = {
            "name": p.name,
            "description": p.description,
            "parameters": {
                "type": "object",
                "properties": arg_properties,
                "required": arg_required,
            },
        }
        prompts_schema[p.name] = schema
    
    resources_raw = await client.list_resources()
    resources = {r.name: (r.description, str(r.uri)) for r in resources_raw}
    resources = dict(sorted(resources.items()))

    templates_raw = await client.list_resource_templates()
    templates = {r.name: (r.description, r.uriTemplate) for r in templates_raw}
    templates = dict(sorted(templates.items()))
    
    return tools, tools_schema, master_available_tools, available_tools, tool_descriptions, prompts, prompts_schema, resources, templates

def display_info(console, info, title=None, border_style=config.color_info_border):
    """ Info panel with background """
    info_panel = Panel(
        Text(info, style="bold white on grey11", justify="center") if isinstance(info, str) else info,
        title=title,
        border_style=border_style,
        box=box.ROUNDED,
        style="on grey11" if isinstance(info, str) else "",
        #padding=(1 if isinstance(info, str) else 0, 1) # (0, 1) by default
    )
    console.print(info_panel)
    console.print()

def backup_conversation(messages, master_plan, console=None, storage_path=None):
    """Backs up the current conversation to the user's directory."""
    if len(messages) > len(DEFAULT_MESSAGES) and ((not console) or (console and storage_path) or (console and not storage_path and config.backup_required)):
        # determine storage path
        if not storage_path:
            if console:
                timestamp = getCurrentDateTime()
                storage_path = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "chats", timestamp)
            else:
                storage_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
        # create directory if not exists
        if not os.path.isdir(storage_path):
            Path(storage_path).mkdir(parents=True, exist_ok=True)
        # Save full conversation
        conversation_file = os.path.join(storage_path, "conversation.py")
        writeTextFile(conversation_file, pprint.pformat(messages))
        # Save master plan
        writeTextFile(os.path.join(storage_path, "master_plan.md"), master_plan)
        # Save markdown
        markdown_file = os.path.join(storage_path, "conversation.md")
        markdown_text = "\n\n".join(["```"+i["role"]+"\n"+i["content"]+"\n```" for i in messages if i.get("role", "") in ("user", "assistant")])
        writeTextFile(markdown_file, markdown_text)
        # Save html
        if console:
            html_file = os.path.join(storage_path, "conversation.html")
            console.save_html(html_file, inline_styles=True, theme=MONOKAI)
        # Inform users of the backup location
        if console:
            info = f"Conversation saved to: {storage_path}\nReport saved to: {html_file}"
            display_info(console, info)

def get_border_style():
    if config.agent_mode:
        return config.color_agent_mode
    elif config.agent_mode is not None:
        return config.color_partner_mode
    return "none"

async def download_data(console, default=""):
    file_ids = {
        "bible.db": "1E6pDKfjUMhmMWjjazrg5ZcpH1RBD8qgW",
        "collection.db": "1y4txzRzXTBty0aYfFgkWfz5qlHERrA17",
        "dictionary.db": "1UxDKGEQa7UEIJ6Ggknx13Yt8XNvo3Ld3",
        "encyclopedia.db": "1NLUBepvFd9UDxoGQyQ-IohmySjjeis2-",
        "exlb.db": "1Hpo6iLSh5KzgR6IZ-c7KuML--A3nmP1-",
    }
    file_id = await DIALOGS.getValidOptions(
        options=file_ids.keys(),
        title="BibleMate Data Files",
        text="Select a file:",
        default=default,
    )
    if file_id:
        output = os.path.join(BIBLEMATEDATA, file_id+".zip")
        if os.path.isfile(output):
            os.remove(output)
        if os.path.isfile(output[:-4]):
            os.remove(output[:-4])
        gdown.download(id=file_ids[file_id], output=output)
        with zipfile.ZipFile(output, 'r') as zip_ref:
            zip_ref.extractall(BIBLEMATEDATA)
        if os.path.isfile(output):
            os.remove(output)
        info = "Restart to make the changes effective!"
        display_info(console, info)

async def main_async():

    os.chdir(BIBLEMATE_USER_DIR)

    BIBLEMATE_STATIC_TOKEN = args.token if args.token else os.getenv("BIBLEMATE_STATIC_TOKEN")
    BIBLEMATE_MCP_PRIVATE_KEY=os.getenv("BIBLEMATE_MCP_PRIVATE_KEY")

    # The client that interacts with the Bible Study MCP server
    if args.mcp:
        if os.path.isfile(args.mcp):
            client = Client(args.mcp)
        else:
            mcp_server = f"http://127.0.0.1:{config.mcp_port}/mcp/" if args.mcp == "biblemate" else args.mcp
            transport = StreamableHttpTransport(
                mcp_server,
                auth=BIBLEMATE_STATIC_TOKEN if BIBLEMATE_STATIC_TOKEN else BIBLEMATE_MCP_PRIVATE_KEY if BIBLEMATE_MCP_PRIVATE_KEY else None,
                sse_read_timeout=config.mcp_timeout,
            )
            client = Client(transport=transport, timeout=config.mcp_timeout)
    else:
        builtin_mcp_server = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bible_study_mcp.py")
        user_mcp_server = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "bible_study_mcp.py") # The user path has the same basename as the built-in one; users may copy the built-in server settings to this location for customization. 
        mcp_server = user_mcp_server if os.path.isfile(user_mcp_server) else builtin_mcp_server        
        client = Client(mcp_server) # no auth for stdio transport

    APP_START = True
    DEFAULT_SYSTEM = "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."
    DEFAULT_MESSAGES = [{"role": "system", "content": DEFAULT_SYSTEM}, {"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hello! I'm BibleMate AI, your personal assistant for Bible study. How can I help you today?"}] # set a tone for bible study; it is userful when auto system is used.

    async with client:

        console = Console(record=True)
        console.clear()
        console.print(get_banner(BIBLEMATE_VERSION))

        tools, tools_schema, master_available_tools, available_tools, tool_descriptions, prompts, prompts_schema, resources, templates = await initialize_app(client)
        resource_suggestions_raw = json.loads(run_uba_api(".resources"))
        # check if default modules are valid:
        config_changed = False
        if not config.default_bible in resource_suggestions_raw["bibleListAbb"]:
            config.default_bible = "NET"
            config_changed = True
        if not config.default_commentary in resource_suggestions_raw["commentaryListAbb"]:
            config.default_commentary = "CBSC"
            config_changed = True
        if not config.default_encyclopedia in resource_suggestions_raw["encyclopediaListAbb"]:
            config.default_encyclopedia = "ISB"
            config_changed = True
        if not config.default_lexicon in resource_suggestions_raw["lexiconList"]:
            config.default_lexicon = "Morphology"
            config_changed = True
        if config_changed:
            write_user_config()
        # format input suggestions
        resource_suggestions = []
        for resource in ["bible", "chapter", "parallel", "promise", "xref", "treasury"]+BIBLE_SEARCH_SCOPES:
            resource_suggestions += [f"//{resource}/{i}/" for i in resource_suggestions_raw["bibleListAbb"]]
        if "AIC" in resource_suggestions_raw["commentaryListAbb"]:
            resource_suggestions_raw["commentaryListAbb"].remove("AIC")
            resource_suggestions_raw["commentaryList"].remove("AI Commentary")
        resource_suggestions += [f"//commentary/{i}/" for i in resource_suggestions_raw["commentaryListAbb"]]
        resource_suggestions += [f"//encyclopedia/{i}/" for i in resource_suggestions_raw["encyclopediaListAbb"]]
        resource_suggestions += [f"//lexicon/{i}/" for i in resource_suggestions_raw["lexiconList"]]
        abbr = BibleBooks.abbrev["eng"]
        resource_suggestions += [abbr[str(book)][0] for book in range(1,67)]

        write_user_config() # remove the temporary `config.backend`
        
        available_tools_pattern = "|".join(available_tools)
        prompt_list = [f"/{p}" for p in prompts.keys()]
        prompt_pattern = "|".join(prompt_list)
        prompt_pattern = f"""^({prompt_pattern}) """
        template_list = [f"//{t}/" for t in templates.keys()]
        template_pattern = "|".join(template_list)
        template_pattern = f"""^({template_pattern})"""

        user_request = ""
        master_plan = ""
        messages = deepcopy(DEFAULT_MESSAGES) # set the tone

        while not user_request == ".exit":

            # spinner while thinking
            async def thinking(process, description=None):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True  # This makes the progress bar disappear after the task is done
                ) as progress:
                    # Add an indefinite task (total=None)
                    task_id = progress.add_task(description if description else "Thinking ...", total=None)
                    # Create and run the async task concurrently
                    async_task = asyncio.create_task(process())
                    # Loop until the async task is done
                    while not async_task.done():
                        progress.update(task_id)
                        await asyncio.sleep(0.01)
                await async_task
            # progress bar for processing steps
            async def async_alive_bar(task):
                """
                A coroutine that runs a progress bar while awaiting a task.
                """
                with alive_bar(title="Processing...", spinner='dots') as bar:
                    while not task.done():
                        bar() # Update the bar
                        await asyncio.sleep(0.01) # Yield control back to the event loop
                return task.result()
            async def process_tool(tool, tool_instruction, step_number=None):
                """
                Manages the async task and the progress bar.
                """
                if step_number:
                    print(f"# Starting Step [{step_number}]...")
                # Create the async task but don't await it yet.
                task = asyncio.create_task(run_tool(tool, tool_instruction))
                # Await the custom async progress bar that awaits the task.
                await async_alive_bar(task)

            if not APP_START and args.exit:
                break

            if not len(messages) == len(DEFAULT_MESSAGES):
                console.rule()
            elif APP_START:
                APP_START = False
                print()
                if not args.exit:
                    # check for updates
                    latest_version = getPackageLatestVersion("biblemate")
                    if latest_version and latest_version > version.parse(BIBLEMATE_VERSION):
                        info = f"A new version of BibleMate AI is available: {latest_version} (you are using {BIBLEMATE_VERSION}).\nTo upgrade, close `BibleMate AI` first and run `pip install --upgrade biblemate`."
                        display_info(console, info)
                    # check connection
                    if not config.skip_connection_check:
                        try:
                            agentmake("Hello!", system=DEFAULT_SYSTEM)
                        except Exception as e:
                            print("Connection failed! Please ensure that you have a stable internet connection and that my AI backend and model are properly configured.")
                            print("Viist https://github.com/eliranwong/agentmake#supported-backends for help about the backend configuration.\n")
                            if click.confirm("Do you want to configure my AI backend and model now?", default=True):
                                edit_configurations()
                                display_info(console, "Restart to make the changes in the backend effective!")
                                exit()
            # Original user request
            # note: `python3 -m rich.emoji` for checking emoji
            console.print("Enter your request :smiley: :" if len(messages) == len(DEFAULT_MESSAGES) else "Enter a follow-up request :flexed_biceps: :")
            input_suggestions = list(config.action_list.keys())+["@ ", "@@ "]+[f"@{t} " for t in available_tools]+[f"{p} " for p in prompt_list]+[f"//{r}" for r in resources.keys()]+template_list+resource_suggestions+config.custom_input_suggestions
            if args.default:
                user_request = " ".join(args.default).strip()
                args.default = None # reset to avoid repeated use
                display_info(console, user_request)
            else:
                user_request = await getTextArea(input_suggestions=input_suggestions)
                master_plan = ""
            # open a text file as a prompt
            check_path = isExistingPath(user_request)
            if check_path and not user_request == ".":
                config.current_prompt = readTextFile(check_path)
                continue
            # luanch action menu
            if not user_request:
                continue
            elif user_request == ".":
                select = await DIALOGS.getValidOptions(options=config.action_list.keys(), descriptions=[i.capitalize() for i in config.action_list.values()], title="Action Menu", text="Select an action:")
                user_request = select if select else ""
            elif user_request.startswith("!"):
                cmd = user_request[1:].strip()
                if not cmd:
                    cmd = "cd" if USER_OS == "Windows" else "pwd"
                os.system(cmd)
                print()
                continue
            # ideas
            if user_request == ".ideas":
                # Generate ideas for `prompts to try`
                ideas = ""
                remarks = f'''\n\n# Remarks\n\nPlease note that user has already entered the following prelimary input:\n\n```\n{config.current_prompt}\n```\n\nTherefore, generate your content along this direction.''' if config.current_prompt.strip() else ""
                async def generate_ideas():
                    nonlocal ideas
                    if len(messages) == len(DEFAULT_MESSAGES):
                        ideas = agentmake(f"Generate three `prompts to try` for bible study. Each one should be one sentence long.{remarks}", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    else:
                        ideas = agentmake(messages, follow_up_prompt=f"Generate three follow-up questions according to the on-going conversation.{remarks}", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(generate_ideas, "Generating ideas ...")
                display_info(console, Markdown(ideas), title="Ideas")
                # Get input again
                continue

            # display resources
            if user_request.startswith("//") and user_request[2:] in resources:
                resource_name = user_request[2:]
                uri = resources[resource_name][1]
                resource_content = await client.read_resource(uri)
                if hasattr(resource_content[0], 'text'):
                    resource_text = resource_content[0].text
                    if resource_text.startswith("{"):
                        resource_dict = json.loads(resource_text)
                        display_content = "\n".join([f"- `{k}`: {v}" for k, v in resource_dict.items()])
                    else:
                        display_content = resource_text
                    resource_description = resources.get(resource_name, "")
                    if resource_description:
                        resource_description = resource_description[0]
                    info = Markdown(f"## `{resource_name.capitalize()}`\n\n{resource_description}\n\n{display_content}")
                    display_info(console, info, title="Information")
                continue

            # run templates
            if user_request == ".bible":
                user_request = await uba_bible(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".xref":
                user_request = await uba_ref(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".treasury":
                user_request = await uba_treasury(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".search":
                user_request = await uba_search_bible(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".chapter":
                user_request = await uba_chapter(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".compare":
                user_request = await uba_compare(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".comparechapter":
                user_request = await uba_compare_chapter(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".commentary":
                user_request = await uba_commentary(options=resource_suggestions_raw["commentaryListAbb"], descriptions=resource_suggestions_raw["commentaryList"])
            elif user_request == ".aicommentary":
                user_request = await uba_aicommentary()
            elif user_request == ".index":
                user_request = await uba_index()
            elif user_request == ".translation":
                user_request = await uba_translation()
            elif user_request == ".discourse":
                user_request = await uba_discourse()
            elif user_request == ".morphology":
                user_request = await uba_morphology()
            elif user_request == ".dictionary":
                if not args.mcp and not "//dictionary/" in template_list:
                    await download_data(console, default="dictionary.db")
                    continue
                else:
                    user_request = await uba_dictionary()
            elif user_request == ".parallel":
                if not args.mcp and not "//parallel/" in template_list:
                    await download_data(console, default="collection.db")
                    continue
                else:
                    user_request = await uba_parallel(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".promise":
                if not args.mcp and not "//promise/" in template_list:
                    await download_data(console, default="collection.db")
                    continue
                else:
                    user_request = await uba_promise(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
            elif user_request == ".topic":
                if not args.mcp and not "//topic/" in template_list:
                    await download_data(console, default="exlb.db")
                    continue
                else:
                    user_request = await uba_topic()
            elif user_request == ".name":
                if not args.mcp and not "//name/" in template_list:
                    await download_data(console, default="exlb.db")
                    continue
                else:
                    user_request = await uba_name()
            elif user_request == ".character":
                if not args.mcp and not "//character/" in template_list:
                    await download_data(console, default="exlb.db")
                    continue
                else:
                    user_request = await uba_character()
            elif user_request == ".location":
                if not args.mcp and not "//location/" in template_list:
                    await download_data(console, default="exlb.db")
                    continue
                else:
                    user_request = await uba_location()
            elif user_request == ".encyclopedia":
                if not args.mcp and not "//encyclopedia/" in template_list:
                    await download_data(console, default="encyclopedia.db")
                    continue
                else:
                    user_request = await uba_encyclopedia(options=resource_suggestions_raw["encyclopediaListAbb"], descriptions=resource_suggestions_raw["encyclopediaList"])
            elif user_request == ".lexicon":
                user_request = await uba_lexicon(options=resource_suggestions_raw["lexiconList"])
            elif user_request == ".chronology":
                user_request = "//uba/DATA:::Bible Chronology"
            if not user_request:
                continue

            if re.search(template_pattern, user_request):
                user_request = urllib.parse.quote(user_request)
                if user_request[2:].count("/") == 1:
                    # check if default module is used
                    keywords = DEFAULT_MODULES
                    keyword, entry = user_request[2:].split("/")
                    if module := keywords.get(keyword, ""):
                        user_request = f"//{keyword}/{module}/{entry}"
                        if user_request.count("/") > 4:
                            user_request = re.sub("^(//.*?/.*?/)(.*?)$", r"\1"+r"\2".replace("/", "「」"), user_request)
                    elif user_request.count("/") > 3:
                        user_request = re.sub("^(//.*?/)(.*?)$", r"\1"+r"\2".replace("/", "「」"), user_request)
                try:
                    template_name, template_args = user_request[2:].split("/", 1)
                    uri = re.sub("{.*?$", "", templates[template_name][1])+template_args
                    resource_content = await client.read_resource(uri)
                    resource_content = resource_content[0].text
                    while resource_content.startswith("[") and resource_content.endswith("]"):
                        options = json.loads(resource_content)
                        select = await DIALOGS.getValidOptions(
                            options=options,
                            title="Multiple Matches",
                            text="Select one of them to continue:"
                        )
                        if select:
                            if user_request.startswith("//name/"):
                                resource_content = select
                            else:
                                resource_content = await client.read_resource(re.sub("^(.*?/)[^/]*?$", r"\1", uri)+urllib.parse.quote(select.replace("/", "「」")))
                                resource_content = resource_content[0].text
                        else:
                            resource_content = "Cancelled by user."
                    if resource_content:
                        messages += [
                            {"role": "user", "content": f"Retrieve content from:\n\n{uri}"},
                            {"role": "assistant", "content": resource_content},
                        ]
                        if resource_content == "Cancelled by user.":
                            info = resource_content
                            display_info(console, info)
                        else:
                            info = Markdown(resource_content.strip())
                            display_info(console, info)
                    continue
                except Exception as e: # invalid uri
                    print(f"Error: {e}\n")
                    continue

            # system command
            if user_request.startswith(".open") or user_request.startswith(".import") or user_request.startswith(".reload"):
                cwd = os.getcwd()
            if user_request == ".open":
                os.chdir(BIBLEMATE_USER_DIR)
                open_item = await DIALOGS.getInputDialog(title="Open", text="Enter a file or folder path:", suggestions=PathCompleter())
                if not open_item:
                    open_item = os.getcwd()
                user_request = f".open {open_item}"
            elif user_request == ".import":
                chats_path = os.path.join(BIBLEMATE_USER_DIR, "chats")
                os.chdir(chats_path)
                import_item = await DIALOGS.getInputDialog(title="Import", text="Enter a conversation file or folder path:", suggestions=PathCompleter())
                if import_item:
                    user_request = f".import {import_item}"
                else:
                    user_request = f".open {chats_path}"
            elif user_request == ".reload":
                temp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
                last_saved_conversation = os.path.join(temp_dir, "conversation.py")
                if os.path.isfile(last_saved_conversation):
                    user_request = f".import {temp_dir}"
                    display_info(console, "Reloading ...")
                else:
                    display_info(console, "Temporary conversation not found!")
                    continue
            if user_request.startswith(".open ") and isExistingPath(user_request[6:]):
                file_path = isExistingPath(user_request[6:])
                cmd = f'''{getOpenCommand()} "{file_path}"'''
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=ResourceWarning)
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.chdir(cwd)
                continue
            elif user_request.startswith(".import ") and isExistingPath(user_request[8:]):
                load_path = isExistingPath(user_request[8:])
                try:
                    # import conversation
                    if os.path.isfile(load_path):
                        file_path = load_path
                    elif os.path.isdir(load_path) and os.path.isfile(os.path.join(load_path, "conversation.py")) and os.path.isfile(os.path.join(load_path, "master_plan.md")):
                        file_path = os.path.join(load_path, "conversation.py")
                    else:
                        print("Expected a file or a directory containing `conversation.py` and `master_plan.md`.")
                        os.chdir(cwd)
                        continue
                    backup_conversation(messages, master_plan, console)
                    config.backup_required = False
                    messages = [{"role": i["role"], "content": i["content"]} for i in eval(readTextFile(file_path)) if i.get("role", "") in ("user", "assistant")]
                    if messages:
                        messages.insert(0, {"role": "system", "content": DEFAULT_SYSTEM})
                    if messages[-1].get("role", "") == "user":
                        messages = messages[:-1]
                    # import master plan
                    if os.path.isdir(load_path):
                        master_plan = readTextFile(os.path.join(load_path, "master_plan.md"))
                        if messages[-2].get("content").startswith(FINAL_INSTRUCTION):
                            user_request = "[STOP]"
                        elif master_plan.strip():
                            user_request = "[CONTINUE]"
                        else:
                            user_request = ""
                    else:
                        master_plan = ""
                        user_request = ""
                    console.clear()
                    console.print(get_banner(BIBLEMATE_VERSION))
                    if messages:
                        for i in messages:
                            if i.get("role", "") == "user":
                                display_info(console,Markdown(i['content'].strip()), border_style=get_border_style())
                            elif i.get("role", "") == "assistant":
                                console.print(Markdown(i['content'].strip()))
                                console.print()
                    if os.path.isfile(load_path) or config.agent_mode is None:
                        # next user request
                        os.chdir(cwd)
                        continue
                except Exception as e:
                    print(f"Error: {e}\n")
                    os.chdir(cwd)
                    continue
            if user_request.startswith(".open") or user_request.startswith(".import") or user_request.startswith(".reload"):
                os.chdir(cwd)

            # predefined operations with `.` commands
            if user_request in config.action_list:
                if user_request == ".backup":
                    backup_conversation(messages, master_plan, console)
                    config.backup_required = False
                elif user_request == ".help":
                    actions = "\n".join([f"- `{k}`: {v}" for k, v in config.action_list.items()])
                    help_info = f"""## Readme

https://github.com/eliranwong/biblemate

## Key Commands

{actions}

## Key Bindings

- `Ctrl+Y`: help info
- `Ctrl+S` or `Esc+ENTER` or `Alt+ENTER`: submit input
- `Ctrl+N`: new conversation
- `Esc+I`: import conversation
- `Esc+O`: edit conversation
- `Ctrl+O`: edit input in text editor
- `Ctrl+Q`: exit input
- `Ctrl+R`: reset input
- `Ctrl+Z`: undo input changes
- `Ctrl+W`: save prompt / plan
- `Esc+W`: delete prompt / plan
- `Ctrl+L`: open prompt / plan
- `Esc+L`: search prompt / plan
- `Ctrl+B`: open bible-related features
- `Ctrl+C`: open bible commentaries
- `Ctrl+V`: open bible verse features
- `Ctrl+X`: open cross-references features
- `Ctrl+F`: open search features
- `Ctrl+J`: change AI mode
- `Ctrl+G`: toggle auto input suggestions
- `Esc+G`: generate ideas for prompts to try
- `Ctrl+P`: toggle auto prompt engineering
- `Esc+P`: improve prompt content
- `Ctrl+D`: delete
- `Ctrl+H`: backspace
- `Ctrl+W`: delete previous word
- `Ctrl+U`: kill text until start of line
- `Ctrl+K`: kill text until end of line
- `Ctrl+A`: go to beginning of line
- `Ctrl+E`: go to end of line
- `Ctrl+LEFT`: go to one word left
- `Ctrl+RIGHT`: go to one word right
- `Ctrl+UP`: scroll up
- `Ctrl+DOWN`: scroll down
- `Shift+TAB`: insert four spaces
- `TAB` or `Ctrl+I`: open input suggestion menu
- `Esc`: close input suggestion menu"""
                    display_info(console, Markdown(help_info), title="Help")
                elif user_request == ".tools":
                    enabled_tools = await DIALOGS.getMultipleSelection(
                        default_values=available_tools,
                        options=master_available_tools,
                        title="Tool Options",
                        text="Select tools to enable:"
                    )
                    if enabled_tools is not None:
                        available_tools = enabled_tools
                        available_tools_pattern = "|".join(available_tools) # reset available tools pattern
                        config.disabled_tools = [i for i in master_available_tools if not i in available_tools]
                        write_user_config()
                    tools_descriptions = [f"- `{name}`: {description}" for name, description in tools.items()]
                    info = Markdown("## Available Tools\n\n"+"\n".join(tools_descriptions))
                    display_info(console, info)
                elif user_request == ".resources":
                    resources_descriptions = [f"- `//{name}`: {description}" for name, description in resources.items()]
                    templates_descriptions = [f"- `//{name}/...`: {description}" for name, description in templates.items()]
                    info = Markdown("## Available Information\n\n"+"\n".join(resources_descriptions)+"\n\n## Available Resources\n\n"+"\n".join(templates_descriptions))
                    display_info(console, info)
                elif user_request == ".plans":
                    prompts_descriptions = [f"- `/{name}`: {description}" for name, description in prompts.items()]
                    info = Markdown("## Available Plans\n\n"+"\n".join(prompts_descriptions))
                    display_info(console, info)
                elif user_request == ".export":
                    cwd = os.getcwd()
                    chats_path = os.path.join(BIBLEMATE_USER_DIR, "chats")
                    if not os.path.isdir(chats_path):
                        Path(chats_path).mkdir(parents=True, exist_ok=True)
                    os.chdir(chats_path)
                    export_item = await DIALOGS.getInputDialog(title="Export", text="Enter a name or path:", default=config.export_item, suggestions=PathCompleter())
                    if export_item:
                        config.export_item = export_item
                        export_item_parent = os.path.dirname(export_item)
                        if not export_item_parent:
                            storage_path = os.path.join(chats_path, export_item)
                        elif os.path.isdir(export_item_parent):
                            storage_path = export_item
                        else:
                            storage_path = os.path.join(chats_path, export_item)
                        try:
                            backup_conversation(messages, master_plan, console, storage_path=storage_path)
                        except Exception as e:
                            print(f"Error: {e}\n")
                    os.chdir(cwd)
                elif user_request == ".trim":
                    options = [str(i) for i in range(0, len(messages))]
                    index_to_trim = await DIALOGS.getValidOptions(
                        default=str(len(messages)-1),
                        options=options,
                        descriptions=[f"{messages[int(i)]['role']}: "+(messages[int(i)]['content'].replace('\n', ' ')[:50]+'...' if len(messages[int(i)]['content'])>50 else messages[int(i)]['content'].replace('\n', ' ')) for i in options],
                        title="Trim Conversation",
                        text="Select an entry to be removed:\n(Note: Its paired user/assistant content will also be removed.)"
                    )
                    if index_to_trim:
                        index_to_trim = int(index_to_trim)
                        trim_role = messages[index_to_trim]["role"]
                        # make sure the user/assistant is removed in pair; skip system message
                        if trim_role == "user":
                            if len(messages) > (index_to_trim + 1) and messages[index_to_trim+1]["role"] == "assistant":
                                del messages[index_to_trim+1]
                            del messages[index_to_trim]
                        elif trim_role == "assistant":
                            del messages[index_to_trim]
                            if messages[index_to_trim-1]["role"] == "user":
                                del messages[index_to_trim-1]
                elif user_request == ".edit":
                    options = [str(i) for i in range(0, len(messages))]
                    index_to_edit = await DIALOGS.getValidOptions(
                        default=str(len(messages)-1),
                        options=options,
                        descriptions=[f"{messages[int(i)]['role']}: "+(messages[int(i)]['content'].replace('\n', ' ')[:50]+'...' if len(messages[int(i)]['content'])>50 else messages[int(i)]['content'].replace('\n', ' ')) for i in options],
                        title="Edit Conversation",
                        text="Select an entry to edit:"
                    )
                    if index_to_edit:
                        index_to_edit = int(index_to_edit)
                        edit_content = messages[index_to_edit]["content"]
                        if DEFAULT_TEXT_EDITOR == "etextedit":
                            edited_content = await launch_async(input_text=edit_content, exitWithoutSaving=True, customTitle=f"BibleMate AI")
                        else:
                            temp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp", "edit.md")
                            writeTextFile(temp_file, edit_content)
                            edit_file(temp_file)
                            edited_content = readTextFile(temp_file).strip()
                        if edited_content:
                            messages[index_to_edit]["content"] = edited_content
                            backup_conversation(messages, master_plan) # backup
                            config.backup_required = True
                            info = "Changes saved!"
                            display_info(console, info)
                elif user_request == ".backend":
                    edit_configurations()
                    info = "Restart to make the changes in the backend effective!"
                    display_info(console, info)
                elif user_request == ".steps":
                    console.print("Enter below the maximum number of steps allowed:")
                    max_steps = await getTextArea(default_entry=str(config.max_steps), title="Enter a positive integer:", multiline=False)
                    if max_steps:
                        try:
                            max_steps = int(max_steps)
                            if max_steps <= 0:
                                console.print("Invalid input.", justify="center")
                            else:
                                config.max_steps = max_steps
                                write_user_config()
                                info = f"Maximum number of steps set to: {config.max_steps}"
                                display_info(console, info)
                        except:
                            info = "Invalid input."
                            display_info(console, info)
                elif user_request == ".matches":
                    console.print("Enter below the maximum number of semantic matches allowed:")
                    max_semantic_matches = await getTextArea(default_entry=str(config.max_semantic_matches), title="Enter a positive integer:", multiline=False)
                    if max_semantic_matches:
                        try:
                            max_semantic_matches = int(max_semantic_matches)
                            if max_semantic_matches <= 0:
                                console.print("Invalid input.", justify="center")
                            else:
                                config.max_semantic_matches = max_semantic_matches
                                write_user_config()
                                info = f"Maximum number of semantic matches set to: {config.max_semantic_matches}"
                                display_info(console, info)
                        except:
                            info = "Invalid input."
                            display_info(console, info)
                elif user_request == ".content":
                    cwd = os.getcwd()
                    display_info(console, list_dir_content(cwd), title=cwd)
                elif user_request == ".autoprompt":
                    config.prompt_engineering = not config.prompt_engineering
                    write_user_config()
                    info = f"Prompt Engineering {'Enabled' if config.prompt_engineering else 'Disabled'}!"
                    display_info(console, info)
                elif user_request == ".autosuggest":
                    config.auto_suggestions = not config.auto_suggestions
                    write_user_config()
                    info = f"Auto Input Suggestions {'Enabled' if config.auto_suggestions else 'Disabled'}!"
                    display_info(console, info)
                elif user_request == ".lite":
                    config.lite = not config.lite
                    write_user_config()
                    info = f"Lite Context {'Enabled' if config.lite else 'Disabled'}!"
                    display_info(console, info)
                elif user_request == ".download":
                    await download_data(console)
                elif user_request == ".find":
                    query = await DIALOGS.getInputDialog(title="Search Chat Files", text="Enter a search query:")
                    if query:
                        searchFolder(os.path.join(BIBLEMATE_USER_DIR, "chats"), query=query, filter="*conversation.py")
                        print()
                elif user_request == ".mode":
                    default_ai_mode = "chat" if config.agent_mode is None else "agent" if config.agent_mode else "partner"
                    ai_mode = await DIALOGS.getValidOptions(
                        default=default_ai_mode,
                        options=["agent", "partner", "chat"],
                        descriptions=["AGENT - Fully automated", "PARTNER - Semi-automated, with review and edit prompts", "CHAT - Direct text responses"],
                        title="AI Modes",
                        text="Select an AI mode:"
                    )
                    if ai_mode:
                        if ai_mode == "agent":
                            config.agent_mode = True
                        elif ai_mode == "partner":
                            config.agent_mode = False
                        else:
                            config.agent_mode = None
                        write_user_config()
                        display_info(console, f"`{ai_mode.capitalize()}` Mode Enabled!")
                elif user_request == ".agent":
                    config.agent_mode = True
                    write_user_config()
                    display_info(console, f"`Agent` Mode Enabled!")
                elif user_request == ".partner":
                    config.agent_mode = False
                    write_user_config()
                    display_info(console, f"`Partner` Mode Enabled!")
                elif user_request == ".chat":
                    config.agent_mode = None
                    write_user_config()
                    display_info(console, f"`Chat` Mode Enabled!")
                elif user_request == ".defaultbible":
                    select = await uba_default_bible(options=resource_suggestions_raw["bibleListAbb"], descriptions=resource_suggestions_raw["bibleList"])
                    if select:
                        config.default_bible = select
                        write_user_config()
                        display_info(console, f"Default bible set to: `{config.default_bible}`")
                elif user_request == ".defaultcommentary":
                    select = await uba_default_commentary(options=resource_suggestions_raw["commentaryListAbb"], descriptions=resource_suggestions_raw["commentaryList"])
                    if select:
                        config.default_commentary = select
                        write_user_config()
                        display_info(console, f"Default commentary set to: `{config.default_commentary}`")
                elif user_request == ".defaultencyclopedia":
                    select = await uba_default_encyclopedia(options=resource_suggestions_raw["encyclopediaListAbb"], descriptions=resource_suggestions_raw["encyclopediaList"])
                    if select:
                        config.default_encyclopedia = select
                        write_user_config()
                        display_info(console, f"Default encyclopedia set to: `{config.default_encyclopedia}`")
                elif user_request == ".defaultlexicon":
                    select = await uba_default_lexicon(options=resource_suggestions_raw["lexiconList"])
                    if select:
                        config.default_lexicon = select
                        write_user_config()
                        display_info(console, f"Default lexicon set to: `{config.default_lexicon}`")
                elif user_request in (".new", ".exit"):
                    backup_conversation(messages, master_plan, console) # backup
                    config.backup_required = False
                # reset
                if user_request == ".new":
                    user_request = ""
                    master_plan = ""
                    messages = deepcopy(DEFAULT_MESSAGES)
                    console.clear()
                    console.print(get_banner(BIBLEMATE_VERSION))
                continue

            # Check if a single tool is specified
            specified_prompt = ""
            specified_tool = ""

            # Tool selection systemm message
            system_tool_selection = get_system_tool_selection(available_tools, tool_descriptions)

            if user_request.startswith("@ "):
                user_request = user_request[2:].strip()
                # Single Tool Suggestion
                suggested_tools = []
                async def get_tool_suggestion():
                    nonlocal suggested_tools, user_request, system_tool_selection
                    # Extract suggested tools from the step suggestion
                    suggested_tools = agentmake(user_request, system=system_tool_selection, **AGENTMAKE_CONFIG)[-1].get("content", "").strip() # Note: suggested tools are printed on terminal by default, could be hidden by setting `print_on_terminal` to false
                    suggested_tools = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                    try:
                        suggested_tools = eval(suggested_tools.replace("`", "'")) if suggested_tools.startswith("[") and suggested_tools.endswith("]") else ["get_direct_text_response"] # fallback to direct response
                    except:
                        suggested_tools = ["get_direct_text_response"]
                await thinking(get_tool_suggestion, "Selecting a tool ...")
                # Single Tool Selection
                if config.agent_mode:
                    this_tool = suggested_tools[0] if suggested_tools else "get_direct_text_response"
                else: # `partner` mode when config.agent_mode is set to False
                    this_tool = await DIALOGS.getValidOptions(options=suggested_tools if suggested_tools else available_tools, title="Suggested Tools", text="Select a tool:")
                    if not this_tool:
                        this_tool = "get_direct_text_response"
                display_info(console, Markdown(f"`{this_tool}`"), title="Selected Tool")
                # Re-format user request
                user_request = f"@{this_tool} " + user_request

            if re.search(prompt_pattern, user_request):
                specified_prompt = re.search(prompt_pattern, user_request).group(1)
                user_request = user_request[len(specified_prompt):]
            elif re.search(f"""^@({available_tools_pattern}) """, user_request):
                specified_tool = re.search(f"""^@({available_tools_pattern}) """, user_request).group(1)
                user_request = user_request[len(specified_tool)+2:]
            elif user_request.startswith("@@"):
                specified_tool = "@@"
                master_plan = user_request[2:].strip()
                async def refine_custom_plan():
                    nonlocal messages, user_request, master_plan
                    # Summarize user request in one-sentence instruction
                    user_request = agentmake(master_plan, tool="biblemate/summarize_task_instruction", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    if "```" in user_request:
                        user_request = re.sub(r"^.*?(```instruction|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                await thinking(refine_custom_plan)
                # display info
                display_info(console, Markdown(user_request), title="User Request", border_style=get_border_style())
                display_info(console, Markdown(master_plan), title="Master Plan", border_style=get_border_style())

            # Prompt Engineering
            original_request = user_request
            if not specified_tool == "@@" and config.prompt_engineering and not user_request in ("[STOP]", "[CONTINUE]"):
                async def run_prompt_engineering():
                    nonlocal user_request
                    try:
                        user_request = agentmake(messages if messages else user_request, follow_up_prompt=user_request if messages else None, tool="improve_prompt", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                        if "```" in user_request:
                            user_request = re.sub(r"^.*?(```improved_version|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                    except:
                        user_request = agentmake(messages if messages else user_request, follow_up_prompt=user_request if messages else None, system="improve_prompt_2", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                        user_request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                await thinking(run_prompt_engineering, "Improving your prompt ...")

                if not config.agent_mode:
                    display_info(console, "Please review and confirm the improved prompt, or make any changes you need.", title="Review & Confirm")
                    improved_prompt_edit = await getTextArea(default_entry=user_request, title="Review - Prompt Engineering")
                    if not improved_prompt_edit or improved_prompt_edit == ".exit":
                        if messages and messages[-1].get("role", "") == "user":
                            messages = messages[:-1]
                        display_info(console, "I've stopped processing for you.")
                        config.current_prompt = original_request
                        continue
                    else:
                        user_request = improved_prompt_edit

            # Add user request to messages
            if not user_request == "[CONTINUE]":
                messages.append({"role": "user", "content": user_request})

            async def run_tool(tool, tool_instruction):
                nonlocal messages
                tool_instruction = fix_string(tool_instruction)
                messages[-1]["content"] = fix_string(messages[-1]["content"])
                if tool == "get_direct_text_response":
                    messages = agentmake(messages, system="auto", **AGENTMAKE_CONFIG)
                else:
                    try:
                        tool_schema = tools_schema[tool]
                        tool_properties = tool_schema["parameters"]["properties"]
                        if len(tool_properties) == 1 and "request" in tool_properties: # AgentMake MCP Servers or alike
                            if "items" in tool_properties["request"]: # requires a dictionary instead of a string
                                request_dict = [{"role": "system", "content": DEFAULT_SYSTEM}]+messages[len(messages)-2:] if config.lite else deepcopy(messages)
                                tool_result = await client.call_tool(tool, {"request": request_dict}, timeout=config.mcp_timeout)
                            else:
                                tool_result = await client.call_tool(tool, {"request": tool_instruction}, timeout=config.mcp_timeout)
                        else:
                            structured_output = getDictionaryOutput(messages=messages, schema=tool_schema, backend=config.backend)
                            tool_result = await client.call_tool(tool, structured_output, timeout=config.mcp_timeout)
                        tool_result = tool_result.content[0].text
                        messages[-1]["content"] += f"\n\n[Using tool `{tool}`]"
                        messages.append({"role": "assistant", "content": tool_result if tool_result.strip() else "Tool error!"})
                    except Exception as e:
                        if DEVELOPER_MODE:
                            console.print(f"Error: {e}\nFallback to direct response...\n\n")
                        messages = agentmake(messages, system="auto", **AGENTMAKE_CONFIG)
                messages[-1]["content"] = fix_string(messages[-1]["content"])

            # user specify a single tool
            if specified_tool and not specified_tool == "@@" and not specified_prompt:
                display_info(console,Markdown(messages[-1]['content']), border_style=get_border_style())
                await process_tool(specified_tool, user_request)
                print()
                console.print(Markdown(messages[-1]['content']))
                console.print()
                config.backup_required = True
                continue

            # Chat mode
            if config.agent_mode is None and not specified_tool == "@@" and not specified_prompt:
                display_info(console,Markdown(messages[-1]['content']), border_style="none")
                async def run_chat_mode():
                    nonlocal messages, user_request
                    messages = agentmake(messages if messages else user_request, system="auto", **AGENTMAKE_CONFIG)
                await thinking(run_chat_mode, "Processing your request ...")
                print()
                console.print(Markdown(messages[-1]['content']))
                # temporaily save after each step
                backup_conversation(messages, "")
                config.backup_required = True
                continue

            # agent mode or partner mode

            # generate master plan
            if not master_plan:
                if specified_prompt:
                    # Call the MCP prompt
                    prompt_schema = prompts_schema[specified_prompt[1:]]
                    prompt_properties = prompt_schema["parameters"]["properties"]
                    if len(prompt_properties) == 1 and "request" in prompt_properties: # AgentMake MCP Servers or alike
                        result = await client.get_prompt(specified_prompt[1:], {"request": user_request})
                    else:
                        structured_output = getDictionaryOutput(messages=messages, schema=prompt_schema, backend=config.backend)
                        result = await client.get_prompt(specified_prompt[1:], structured_output)
                    #print(result, "\n\n")
                    master_plan = result.messages[0].content.text
                    # display info# display info
                    display_info(console, Markdown(user_request), title="User Request", border_style=get_border_style())
                    display_info(console, Markdown(master_plan), title="Master Plan", border_style=get_border_style())
                else:
                    # display info
                    display_info(console, Markdown(user_request), title="User Request", border_style=get_border_style())
                    # Generate master plan
                    master_plan = ""
                    async def generate_master_plan():
                        nonlocal master_plan
                        # Create initial prompt to create master plan
                        initial_prompt = f"""Provide me with the `Preliminary Action Plan` and the `Measurable Outcome` for resolving `My Request`.
    
# Available Tools

Available tools are: {available_tools}.

{tool_descriptions}

# My Request

{user_request}"""
                        master_plan = agentmake(messages+[{"role": "user", "content": initial_prompt}], system="create_action_plan", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    await thinking(generate_master_plan, "Crafting a master plan ...")

                    # partner mode
                    if not config.agent_mode:
                        display_info(console, "Please review and confirm the master plan, or make any changes you need.", title="Review & Confirm")
                        master_plan_edit = await getTextArea(default_entry=master_plan, title="Review - Master Plan")
                        if not master_plan_edit or master_plan_edit == ".exit":
                            if messages and messages[-1].get("role", "") == "user":
                                messages = messages[:-1]
                            display_info(console, "I've stopped processing for you.")
                            continue
                        else:
                            master_plan = master_plan_edit

                    # display info
                    display_info(console, Markdown(master_plan), title="Master Plan", border_style=get_border_style())

            # Step suggestion system message
            system_progress = get_system_progress(master_plan=master_plan)
            system_make_suggestion = get_system_make_suggestion(master_plan=master_plan)

            # Get the first suggestion
            conversation_broken = False
            if user_request == "[CONTINUE]":
                next_suggestion = "CONTINUE"
            elif user_request == "[STOP]":
                next_suggestion = "STOP"
            else:
                next_suggestion = "START"

            step = int(((len(messages)-len(DEFAULT_MESSAGES)-2)/2+1)) if user_request == "[CONTINUE]" else 1
            while not ("STOP" in next_suggestion or re.sub("^[^A-Za-z]*?([A-Za-z]+?)[^A-Za-z]*?$", r"\1", next_suggestion).upper() == "STOP"):

                async def make_next_suggestion():
                    nonlocal next_suggestion, system_make_suggestion, messages, step
                    next_suggestion = agentmake(user_request if next_suggestion == "START" else [{"role": "system", "content": system_make_suggestion}]+messages[len(DEFAULT_MESSAGES):], system=system_make_suggestion, follow_up_prompt=None if next_suggestion == "START" else "Please provide me with the next step suggestion, based on the action plan.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(make_next_suggestion, "Marking a suggestion ...")
                display_info(console, Markdown(next_suggestion), title=f"Suggestion [{step}]")

                # Get tool suggestion for the next iteration
                suggested_tools = []
                async def get_tool_suggestion():
                    nonlocal suggested_tools, next_suggestion, system_tool_selection
                    # Extract suggested tools from the step suggestion
                    suggested_tools = agentmake(next_suggestion, system=system_tool_selection, **AGENTMAKE_CONFIG)[-1].get("content", "").strip() # Note: suggested tools are printed on terminal by default, could be hidden by setting `print_on_terminal` to false
                    suggested_tools = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                    try:
                        suggested_tools = eval(suggested_tools.replace("`", "'")) if suggested_tools.startswith("[") and suggested_tools.endswith("]") else ["get_direct_text_response"] # fallback to direct response
                    except:
                        suggested_tools = ["get_direct_text_response"]
                await thinking(get_tool_suggestion, "Selecting a tool ...")
                if DEVELOPER_MODE and not config.hide_tools_order:
                    info = Markdown(f"## Descending Order by Relevance\n\n{suggested_tools}")
                    display_info(console, info, title=f"Tool Selection [{step}]")

                # Use the next suggested tool
                # partner mode
                if config.agent_mode:
                    next_tool = suggested_tools[0] if suggested_tools else "get_direct_text_response"
                else: # `partner` mode when config.agent_mode is set to False
                    next_tool = await DIALOGS.getValidOptions(options=suggested_tools if suggested_tools else available_tools, title="Suggested Tools", text="Select a tool:")
                    if not next_tool:
                        next_tool = "get_direct_text_response"
                prefix = f"Next Tool [{step}]" if DEVELOPER_MODE and not config.hide_tools_order else f"Tool Selection [{step}]"
                info = Markdown(f"`{next_tool}`")
                display_info(console, info, title=prefix)

                # Get next step instruction
                next_step = ""
                async def get_next_step():
                    nonlocal next_step, next_tool, next_suggestion, tools
                    if next_tool == "get_direct_text_response":
                        next_step = agentmake(next_suggestion, system="biblemate/direct_instruction", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    else:
                        next_tool_description = tools.get(next_tool, "No description available.")
                        system_tool_instruction = get_system_tool_instruction(next_tool, next_tool_description)
                        next_step = agentmake(next_suggestion, system=system_tool_instruction, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                        # The following line may give better context, but when a conversation goes long, the agent loses track of the system message.
                        #next_step = agentmake([{"role": "system", "content": system_tool_instruction}]+messages[len(DEFAULT_MESSAGES):], follow_up_prompt=next_suggestion, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(get_next_step, "Crafting the next instruction ...")
                # partner mode
                if config.agent_mode == False:
                    display_info(console, "Please review and confirm the next instruction, or make any changes you need.", title="Review & Confirm")
                    next_step_edit = await getTextArea(default_entry=next_step, title="Review - Next Instruction")
                    if not next_step_edit or next_step_edit == ".exit":
                        display_info(console, "I've stopped processing for you.")
                        break
                    else:
                        next_step = next_step_edit
                display_info(console, Markdown(next_step), title=f"Next Instruction [{step}]", border_style=get_border_style())

                if messages[-1]["role"] != "assistant": # first iteration
                    messages.append({"role": "assistant", "content": "Please provide me with an initial instruction to begin."})
                messages.append({"role": "user", "content": next_step})

                await process_tool(next_tool, next_step, step_number=step)
                console.rule()
                console.print(Markdown(f"\n## Output [{step}]\n\n{messages[-1]['content']}"))
                console.print()
                console.rule()
                # temporaily save after each step
                backup_conversation(messages, master_plan)
                config.backup_required = True

                # iteration count
                step += 1
                if step > config.max_steps:
                    info = Markdown(f"I've stopped processing for you, as the maximum steps allowed is currently set to `{config.max_steps}` steps. Enter `.steps` to configure more.")
                    display_info(console, info)
                    conversation_broken = True
                    break

                # Check the progress
                async def get_next_suggestion():
                    nonlocal next_suggestion, messages, system_progress
                    next_suggestion = agentmake([{"role": "system", "content": system_progress}]+messages[len(DEFAULT_MESSAGES):], system=system_progress, follow_up_prompt="Please decide either to `CONTINUE` or `STOP` the process.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(get_next_suggestion, description="Checking the progress ...")
            
            if messages[-1].get("role") == "user":
                messages.append({"role": "assistant", "content": next_suggestion})
            
            # write the final answer
            if messages[-2].get("content") == "[STOP]" and messages[-1].get("content") == "STOP":
                messages = messages[:-2]
            if not conversation_broken and not messages[-2].get("content").startswith(FINAL_INSTRUCTION):
                console.print(Markdown("# Wrapping up ..."))
                messages = agentmake(
                    messages,
                    system="write_final_answer",
                    follow_up_prompt=f"""{FINAL_INSTRUCTION}{user_request}""",
                    stream=True,
                )
                messages[-1]["content"] = fix_string(messages[-1]["content"])
                console.rule()
                console.print(Markdown(messages[-1]['content']))

            # Backup
            print()
            backup_conversation(messages, master_plan, console)
            config.backup_required = False
    
    # back up configurations
    write_user_config(backup=True)
    # reset terminal window title
    clear_title()

if __name__ == "__main__":
    asyncio.run(main())
