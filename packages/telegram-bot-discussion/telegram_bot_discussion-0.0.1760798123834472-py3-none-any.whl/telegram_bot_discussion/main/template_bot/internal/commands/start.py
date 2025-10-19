from telegram_bot_discussion.command import Command


class StartCommand(Command):

    class Meta(Command.Meta):
        action: str = "start"
