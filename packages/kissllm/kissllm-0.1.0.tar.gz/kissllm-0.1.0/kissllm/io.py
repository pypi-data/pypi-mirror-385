import readline as readline
from dataclasses import dataclass
from enum import Enum, auto

from kissllm.utils import format_prompt


@dataclass
class OutputMetadata:
    pass


class SimpleTextUI:
    def __init__(self, name, input_generator=None):
        self.input_generator = input_generator or IOChannel.simple_input_generator()
        self.name = name
        self.io_channel = IOChannel(name, self)

    def run(self):
        raise NotImplementedError()


class IOChannel:
    def __init__(self, channel_type, app):
        self.channel_type = channel_type
        self.app = app

    def create_sub_channel(self, channel_type, title=""):
        return self.__class__(channel_type, self.app)

    async def read(self):
        async for user_input in self.app.input_generator:
            yield user_input

    async def write(self, content, metadata: OutputMetadata | None = None):
        if self.channel_type == IOTypeEnum.prompt_message:
            print("\n".join(format_prompt(content)))
        elif self.channel_type == IOTypeEnum.streaming_assistant:
            print(content, end="", flush=True)
        else:
            print(content)

    @staticmethod
    async def simple_input_generator():
        try:
            while True:
                line = input("\nUser (Ctrl+D to quit): ")
                yield line
        except EOFError:
            pass


class IOTypeEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    prompt_message = auto()
    streaming_assistant = auto()
