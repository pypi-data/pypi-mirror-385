#!/usr/bin/env python3

# Copyright (C) 2025 Jean Privat, based from the work of Dory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A command-line assistant for local LLMs"""

import argparse
import base64
import itertools
import json
import logging
import os
import re
import readline
import subprocess
import sys
import tempfile
import threading
import time
import tomllib

import magic
import requests
from termcolor import colored, cprint

# The global logger of the module
logger = logging.getLogger(__name__)

class LLME:
    """The God class of the application."""

    def __init__(self, config):
        self.config = config
        self.model = config.model
        self.prompts = config.prompts # Initial prompts to process
        self.messages = [] # the sequence of messages with the LLM
        self.raw_messages = [] # the sequence of messages really communicated with the LLM server to work-around their various API limitations

        self.api_headers = [] # additional headers for the server
        if self.config.api_key:
            self.api_headers["Authorization"] = f"Bearer {self.config.api_key}"

        # Timing information
        self.total_prompt_n = 0
        self.total_predicted_n = 0
        self.total_prompt_ms = 0.0
        self.total_predicted_ms = 0.0

    def add_message(self, message):
        """
        Append a new message.
        Add it as is in message but transform it in raw_messages.
        """

        logger.debug("Add %s message: %s", message['role'], message)
        self.messages.append(message)

        # Special filtering for some models/servers
        # TODO make it configurable and modular
        if isinstance(message["content"], list):
            text_content = []
            # unpack file content parts
            for part in message["content"]:
                if part["type"] == "text":
                    text_content.append(part["text"])
                if part["type"] == "file":
                    # replace the file content with its path.
                    text_content.append(f"The file is {part['file']['filename']}. You can cat its content.")
                if part["type"] == "image_url":
                    self.raw_messages.append(message)
            self.raw_messages.append({"role": message["role"], "content": "\n".join(text_content)})
            return

        self.raw_messages.append(message)

    def get_models(self):
        """List the available models"""
        url = f"{self.config.base_url}/models"
        logger.info("Get models from %s", url)
        try:
            response = requests.get(url, headers=self.api_headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(extract_requests_error(e))
            sys.exit(1)
        models = response.json()
        ids = [m["id"] for m in models["data"]]
        logger.info("Available models: %s", ids)
        return ids

    def warmup_model(self):
        """
        Run a small empty chat to load the model (if meeded) and check that the server/model is ok.
        Run in background while the user is typing its first prompt.
        """
        self.warmup = Warmup(self)


    def run_tool(self, tool, stdin):
        """Run a tool and return the result as a system message (or None if cancelled)"""
        if self.config.yolo:
            print(colored(f"{len(self.messages)} YOLO RUN {tool}", "red", attrs=["bold"]))
        elif self.config.batch:
            raise EOFError("No tool confirmation in batch mode") # ugly
        else:
            try:
                x = input(colored(f"{len(self.messages)} RUN {tool} [Yn]? ", "red", attrs=["bold"])).strip()
                if x not in ['', 'y', 'Y']:
                    return None
            except KeyboardInterrupt:
                raise EOFError("Confirmation interrupted") # ugly

        # hack for unbuffered python
        if tool == "python":
            tool = ["python", "-u"]

        proc = subprocess.Popen(
            tool,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # line-buffered
        )
        logger.debug("Starting sub-process %s", tool)

        # send data to stdin
        # FIXME: avoid deadlock...
        # It's weird there isn't a lib or something to do this properly...
        proc.stdin.write(stdin)
        proc.stdin.close()

        content = ''
        with AnimationManager("red", self.config.plain) as am:
            while line := proc.stdout.readline():
                am.stop()
                print(line, end='', flush=True)
                content += line
        proc.wait()
        if not content.endswith('\n'):
            print()

        if proc.returncode != 0:
            print(colored(f"EXIT {proc.returncode}", "red", attrs=["bold"]))

        content = f"```result {tool} exitcode={proc.returncode}\n{content}\n```\n"
        return {"role": "tool", "content": content, "tool_call_id": f"toolcallid{len(self.messages)}"}


    def next_asset(self):
        """Get the next asset from the user. or None"""
        if len(self.prompts) == 0:
            return None

        # peek a the next "prompt" to see if it's a file
        user_input = self.prompts[0]
        if not os.path.exists(user_input):
            return None

        # it's a file, so remove it from prompts and add it to files
        self.prompts.pop(0)
        file = Asset(user_input)
        # Test to handle input redirection from /dev/null
        if len(file.raw_content) > 0:
            return file
        return None


    def next_prompt(self):
        """Get the next prompt from the user.
        Returns None or a user message"""
        logger.debug("Get the next prompt. Prompts queue: %d", len(self.prompts))

        files = [] # the list of files to send to the LLM for the next prompt
        while file := self.next_asset():
            files.append(file)

        if len(self.prompts) > 0:
            user_input = self.prompts.pop(0)
            if not self.config.plain:
                print(colored(f"{len(self.messages)}>", "green", attrs=["bold"]), user_input)
        elif self.config.batch:
            raise EOFError("end of batch") # ugly
        else:
            try:
                self.warmup.check()
                if not self.config.plain:
                    user_input = input(colored(f"{len(self.messages)}> ", "green", attrs=["bold"]))
                else:
                    user_input = input()
                self.warmup.check()
            except KeyboardInterrupt:
                raise EOFError("interrupted") # ugly

        if user_input == '':
            return None

        while file := self.next_asset():
            files.append(file)

        content_parts = []
        for asset in files:
            content_part = asset.content_part()
            if content_part:
                content_parts.append(content_part)
        if len(content_parts) > 0:
            content_parts.insert(0, {"type": "text", "text": user_input})
            return {"role": "user", "content": content_parts}
        else:
            return {"role": "user", "content": user_input}


    def chat_completion(self):
        """Get a response from the LLM."""
        url = f"{self.config.base_url}/chat/completions"
        logger.debug("Sending %d raw messages to %s", len(self.raw_messages), url)

        with AnimationManager("blue", self.config.plain):
            response = requests.post(
                url,
                headers=self.api_headers,
                json={"model": self.model,
                      "messages": self.raw_messages,
                      "stream": True},
                stream=True,
                timeout=600,  # high enough
            )
            response.raise_for_status()

        if not self.config.plain:
            print(colored(f"{len(self.messages)}< ", "blue", attrs=["bold"]), end='', flush=True)

        full_content = ''
        cb = None
        timings=None
        for line in response.iter_lines():
            # The communication is loosly based on Server-Sent Events (SSE)
            if line == b'':
                continue
            if line[0] == 0x7b: # '{'
                # special case of no streamimg
                data = json.loads(line.decode())
                message = data['choices'][0]['message']
                self.add_message(message)
                print(message['content'])
                return None

            data = line.split(b':', 1)
            if len(data) != 2:
                raise ValueError(f"Unexpected chunk: {line}")
            event, data = data
            if event != b'data':
                raise ValueError(f"Unexpected event type: {line}")
            if data == b"[DONE]":
                logger.warn("Got [DONE] event, we shoud have stopped before")
                continue
            data = json.loads(data.decode())
            choice0 = data['choices'][0]
            if choice0['finish_reason'] is not None:
                logger.debug("last chunk %s", data)
                if "timings" in data:
                    timings = data["timings"]
                break
            if 'reasoning_content' in choice0['delta']:
                # Some thinking models like qwen3 have a reasoning_content field
                content = choice0['delta']['reasoning_content']
            else:
                content = choice0['delta']['content']
            if content is None:
                continue
            full_content += content
            print(content, end='', flush=True)
            #FIXME: this is fragile and ugly.
            cb = re.search(r"^```run ([\w+-]*)\n(.*?)^```$", full_content, re.DOTALL | re.MULTILINE)
            if cb:
                # Force the LLM to stop once a tool call is found
                break
        if not full_content.endswith('\n'):
            print()
        if timings:
            print(colored(f"cache: %dt prompt: %dt %.2ft/s predicted: %dt %.2ft/s" % (timings["cache_n"], timings["prompt_n"], timings["prompt_per_second"], timings["predicted_n"], timings["predicted_per_second"]), "grey", attrs=["bold"]))
            self.total_prompt_n += timings["prompt_n"]
            self.total_predicted_n += timings["predicted_n"]
            self.total_prompt_ms += timings["prompt_ms"]
            self.total_predicted_ms += timings["predicted_ms"]
        response.close()
        self.add_message({"role": "assistant", "content": full_content})
        if cb:
            r = self.run_tool(cb[1], cb[2])
            if r:
                self.add_message(r)
                return r
        return None


    def loop(self):
        """The main ping-pong loop between the user and the assistant"""
        while True:
            try:
                prompt = self.next_prompt()
                if prompt:
                    self.add_message(prompt)
                while self.chat_completion():
                    pass
            except requests.exceptions.RequestException as e:
                logger.error(extract_requests_error(e))
                break
            except KeyboardInterrupt:
                logger.warning("Interrupted by user.")
                if self.config.batch:
                    break
            except EOFError as e:
                logger.info("Quiting: %s", str(e))
                break


    def start(self):
        """Start, work, and terminate"""

        if self.config.list_models:
            models = self.get_models()
            print(f"Models of {self.config.base_url}:")
            for m in models:
                print(f"* {m}")
            return
        if not self.model:
            self.model = self.get_models()[0]
        logger.info("Use model %s from %s", self.model, self.config.base_url)

        self.warmup_model()

        if self.config.chat_input:
            logger.info("Loading conversation from %s", self.config.chat_input)
            with open(self.config.chat_input, "r") as f:
                for message in json.load(f):
                    self.add_message(message)
            logger.info("Loaded %d messages", len(self.messages))
        elif self.config.system_prompt:
            self.add_message({"role": "system", "content": self.config.system_prompt})

        stdinfile = None
        if not sys.stdin.isatty():
            if len(self.prompts) > 0:
                # There is prompts, so use stdin as data for the first prompt
                stdinfile = tempfile.NamedTemporaryFile(mode='wb', delete=False)
                with stdinfile as f:
                    f.write(sys.stdin.buffer.read())

                self.prompts.insert(0, stdinfile.name)
            else:
                # No prompts, so use stdin as prompt
                self.prompts = [sys.stdin.read()]

        try:
            self.loop()
        finally:
            if self.config.chat_output:
                logger.info("Dumping conversation to %s", self.config.chat_output)
                with open(self.config.chat_output, "w") as f:
                    json.dump(self.messages, f, indent=2)
            if stdinfile:
                os.unlink(stdinfile.name)

        if self.total_prompt_n > 0:
            print(colored(f"Total: prompt: %dt %.2ft/s predicted: %dt %.2ft/s" % (self.total_prompt_n, 1000.0*self.total_prompt_n/self.total_prompt_ms, self.total_predicted_n, 1000.0*self.total_predicted_n/self.total_predicted_ms), "grey", attrs=["bold"]))

class AnimationManager:
    """A simple context manager for a spinner animation."""
    def __init__(self, color, plain=False):
        self.color = color
        self.plain = plain
        self.stop_event = None
        self.animation_thread = None

    def _animate(self):
        """Animation loop, run in a thread."""
        for c in itertools.cycle("⠋⠙⠹⠽⠼⠴⠦⠧⠇⠏"):
            if self.stop_event.is_set():
                break
            sys.stdout.write(f'\r{colored(c, self.color, attrs=["bold"])} ')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def stop(self):
        """Manually stop the animation."""
        if self.plain:
            return
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.animation_thread.join()

    def __enter__(self):
        if not self.plain:
            self.stop_event = threading.Event()
            self.animation_thread = threading.Thread(target=self._animate)
            self.animation_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()


class Warmup:
    def __init__(self, llm):
        self.llm = llm
        self.thread = threading.Thread(target=self._process)
        self.thread.daemon = True
        self.event = threading.Event()
        self.message = None
        self.thread.start()

    def check(self):
        if self.event.is_set():
            logger.error(self.message)
            sys.exit(1)

    def _process(self):
        url = f"{self.llm.config.base_url}/chat/completions"
        json = {
            "model": self.llm.model,
            "messages": [{"role":"user", "content":""}],
            "max_completion_tokens":1,
            "max_tokens":1,
            "temperature":0,
        }
        logger.info("warmup %s", url)
        try:
            with requests.post(url=url, headers=self.llm.api_headers, json=json) as response:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.message = extract_requests_error(e)
            self.event.set()
            logger.info("warmup error: %s", self.message)
            return
        logger.info("warmup completed")


class Asset:
    "A loaded file"
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            self.raw_content = f.read()
        self.mime_type = magic.from_buffer(self.raw_content, mime=True)
        logger.info("File %s is %s", path, self.mime_type)

    def content_part(self):
        """Return the content part for the user message"""
        if self.mime_type.startswith("image/"):
            data = base64.b64encode(self.raw_content).decode()
            url = f"data:{self.mime_type};base64,{data}"
            return {"type": "image_url", "image_url": {"url": url}}
        else:
            data = base64.b64encode(self.raw_content).decode()
            return {"type": "file", "file": {"file_data": data, "filename": self.path}}


def extract_requests_error(e):
    """Common handling of requests error"""
    logger.debug("request error: %s", e)
    if e.request is None:
        return str(e)
    if e.response is None:
        return f"{e} ({e.request.url})"

    """Server may format their error in plain text or json"""
    text = e.response.text
    if text[0] == '{':
        logger.debug("full error response: %s", text)
        try:
            data = json.loads(text)
        except:
            data = {}
        if "error" in data:
            data = data["error"]
            text = data
        if "message" in data:
            text = data["message"]

    message = f"{text} ({e.response.status_code} {e.response.request.url})"
    return message


def apply_config(args, config, path):
    """Apply a config dict to an args namespace without overwriting existing values (precedence).
    The method is a little ugly but it works... """
    #TODO check types
    variables = vars(args)
    for k in variables:
        if variables[k] is None and k in config:
            setattr(args, k, config[k])
    for k in config:
        if k not in variables:
            logger.warning("%s: Unknown config key %s", path, k)

def apply_env(args):
    """Apply environment variables to an args namespace without overwriting existing values (precedence)."""
    variables = vars(args)
    for k in variables:
        var = f"LLME_{k.upper()}"
        env = os.environ.get(var)
        if variables[k] is None and env:
            # TODO type conversion
            setattr(args, k, env)
    for k in os.environ:
        m = re.match(r'LLME_(.*)', k)
        if m and m[1].lower() not in variables:
            logger.warning("Unknown environment variable %s", k)

def load_config_file(path):
    """Load a TOML config file."""
    logger.debug("Loading config from %s", path)
    with open(path, "rb") as f:
        return tomllib.load(f)

def resolve_config(args):
    """Compute config in order of precedence"""
    # 1. args have the highest precedence

    # 2. then explcit --config files in reverse order (last wins)
    if args.config:
        for path in reversed(args.config):
            config = load_config_file(path)
            apply_config(args, config, path)

    # 3. Then environment variables
    apply_env(args)

    # 4. The default config files: user, then system
    config_dirs = [
        os.path.expanduser("~/.config/llme"),
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for directory in config_dirs:
        path = os.path.join(directory, "config.toml")
        if os.path.exists(path):
            config = load_config_file(path)
            apply_config(args, config, path)
    logger.debug("Final config: %s", vars(args))

def process_args():
    """Handle command line arguments and envs."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options...] [prompts...]',
        description="OpenAI-compatible chat CLI.",
    )
    parser.add_argument("-u", "--base-url", help="API base URL [base_url]")
    parser.add_argument("-m", "--model", help="Model name [model]")
    parser.add_argument("--list-models", action="store_true", help="List available models then exit")
    parser.add_argument("--api-key", help="The API key [api_key]")
    parser.add_argument("-b", "--batch", default=None, action="store_true", help="Run non-interactively. Implicit if stdin is not a tty [batch]")
    parser.add_argument("-p", "--plain", default=None, action="store_true", help="No colors or tty fanciness. Implicit if stdout is not a tty [plain]")
    parser.add_argument("-o", "--chat-output", help="Export the full raw conversation in json")
    parser.add_argument("-i", "--chat-input", help="Continue a previous (exported) conversation")
    parser.add_argument("-s", "--system", dest="system_prompt", help="System prompt [system_prompt]")
    parser.add_argument("-c", "--config", action="append", help="Custom configuration files")
    parser.add_argument(      "--dump-config", action="store_true", help="Print the effective config and quit")
    parser.add_argument("-v", "--verbose", default=0, action="count", help="Increase verbosity level (can be used multiple times)")
    parser.add_argument("-Y", "--yolo", default=None, action="store_true", help="UNSAFE: Do not ask for confirmation before running tools. Combine with --batch to reach the singularity.")
    parser.add_argument("prompts", nargs='*', help="An initial list of prompts")

    args = parser.parse_intermixed_args()

    logging.basicConfig()
    logging_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logger.setLevel(logging_levels[min(args.verbose, len(logging_levels) - 1)])
    logger.info("Log level set to %s", logging.getLevelName(logger.level))
    logger.debug("Given arguments %s", vars(args))

    resolve_config(args)

    if args.dump_config:
        json.dump(vars(args), sys.stdout, indent=2)
        sys.exit(0)

    if args.base_url is None:
        print("Error: --base-url required and not definied the config file.", file=sys.stderr)
        sys.exit(1)

    if args.batch is None and not sys.stdin.isatty():
        args.batch = True
    if args.plain is None and not sys.stdout.isatty():
        args.plain = True

    return args


def main():
    """The main CLI entry point."""
    config = process_args()
    llme = LLME(config)
    llme.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
