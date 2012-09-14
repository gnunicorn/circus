from circus.exc import MessageError, ArgumentError
from circus.commands.base import Command
from circus.stream import TailStream


class Showlog(Command):
    """\
       Show in process logs of a process
       ==================================

       If you've specified the Queue for stderr/stdout for your process
       with this command you can see what is currently queued up there

       ZMQ Message
       -----------

       To show the logs for a watcher::

            {
                "command": "showlog",
                "properties": {
                    "name": <name>
                }
            }

       The response return a list with one entry per line queued up.

       Command Line
       ------------

       ::

            $ circusctl showlog <watchername>

        """

    name = "showlog"

    def message(self, *args, **opts):
        if len(args) != 1:
            raise ArgumentError("Please provide the name of the watcher")

        return self.make_message(name=args[0])

    def execute(self, arbiter, props):
        try:
            name = props["name"]
        except KeyError:
            raise MessageError("Please provide the name of the watcher")

        watcher = self._get_watcher(arbiter, name)
        results = dict(stdout=[], stderr=[])
        for channel in ("stdout", "stderr"):
            stream = getattr(watcher, "%s_stream" % channel)['stream']
            if isinstance(stream, TailStream):
                results[channel] = [x for x in stream]

        return results

    def console_msg(self, msg):
        if msg['status'] != 'ok':
            return msg

        output = []
        for channel in ("stderr", "stdout"):
            if channel in msg:
                for data in msg[channel]:
                    output.append("%s - %d: %s" % \
                            (data['pid'], data['time'],
                                data['data'].encode("utf-8")))
            output.append(" -- %s:" % channel)

        output.reverse()
        return "\n".join(output)
