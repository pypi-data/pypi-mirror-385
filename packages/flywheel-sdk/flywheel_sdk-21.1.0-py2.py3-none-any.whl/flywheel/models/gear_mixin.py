"""Provides gear mixin"""

from .gear_invocation import GearInvocation


class GearMixin(object):
    """Gear mixin that provides additional functionality"""

    def __init__(self):
        self.__context = None

    def _set_context(self, context):
        """Set the context object (i.e. flywheel client instance)"""
        self.__context = context

    def _invoke_gear_api(self, fname, *args, **kwargs):
        """Invoke gear api"""
        if self.__context:
            fn = getattr(self.__context, fname, None)
            if fn:
                return fn(self.gear.name, *args, **kwargs)
        return None

    def create_invocation(self):
        """Create a job invocation object"""
        result = GearInvocation(self)
        result._set_context(self.__context)
        return result

    def is_analysis_gear(self):
        """Check if this is an analysis gear"""
        return self.category == "analysis"

    def print_details(self, width=90):
        """Print details about a gear to stdout

        :param int width: The maximum line width for printing
        """
        import textwrap

        def print_wrap(s, **kwargs):
            print(textwrap.fill(s, width=width, **kwargs))

        def print_col(label, value):
            line = "{:<15} {}".format(label + ":", value)
            print(textwrap.fill(line, width=width, subsequent_indent=(" " * 16)))

        gear = self.gear

        print_wrap(gear.label or gear.name)

        if gear.description:
            print("")
            print_wrap(gear.description, subsequent_indent="  ")
            print("")

        print_col("Name", gear.name)
        print_col("Version", gear.version)
        print_col("Category", self.category)

        if gear.author:
            print_col("Author", gear.author)

        if gear.maintainer:
            print_col("Maintainer", gear.maintainer)

        if gear.url:
            print_col("URL", gear.url)

        if gear.source:
            print_col("Source", gear.source)

        print("")

        if gear.inputs:
            print("Inputs:")
            for key, spec in gear.inputs.items():
                if spec.get("optional", False):
                    opt = "optional"
                else:
                    opt = "required"

                print("  {} ({}, {})".format(key, spec.get("base", "unspecified"), opt))
                if "type" in spec and "enum" in spec["type"]:
                    types = ", ".join(spec["type"]["enum"])
                    print("    Type: {}".format(types))
                if "description" in spec:
                    print_wrap(
                        spec["description"],
                        initial_indent="    ",
                        subsequent_indent="      ",
                    )
            print("")

        if gear.config:
            print("Configuration:")
            for key, spec in gear.config.items():
                if "default" in spec:
                    dflt = ", default: {}".format(spec["default"])
                else:
                    dflt = ""
                print("  {} ({}{})".format(key, spec.get("type", "unspecified"), dflt))
                if "description" in spec:
                    print_wrap(
                        spec["description"],
                        initial_indent="    ",
                        subsequent_indent="      ",
                    )

    def get_default_config(self):
        """Get the default configuration for gear"""
        config = self.gear.get("config", {})
        default_config = {}
        for key, value in config.items():
            if value.get("default") is not None:
                default_config[key] = value.get("default")
        return default_config

    def run(self, config=None, analysis_label=None, tags=None, destination=None, inputs=None, priority=None, **kwargs):
        """Run the gear.

        :param dict config: The configuration to use, if overriding defaults.
        :param str analysis_label: The label of the analysis, if running an analysis gear.
        :param list tags: The list of tags to set for the job.
        :param object destination: The destination container.
        :param dict inputs: The list of input containers or files.

        :return: The id of the job that was created (utility gear) or of the analysis container created (analysis gear).
        """
        invocation = self.create_invocation()

        if config is not None:
            invocation.update_config(config)
        if analysis_label is not None:
            invocation.set_analysis_label(analysis_label)
        if tags is not None:
            invocation.add_tags(tags)
        if destination is not None:
            invocation.set_destination(destination)
        if priority is not None:
            invocation.set_priority(priority)

        # Combine inputs and kwargs into inputs
        if inputs is not None:
            kwargs.update(inputs)
        for key, input in kwargs.items():
            invocation.set_input(key, input)

        return invocation.run()

    def propose_batch(
        self,
        containers,
        config=None,
        analysis_label=None,
        tags=None,
        priority=None,
        optional_input_policy="ignored",
    ):
        """Propose a batch run of the gear.

        :param list containers: The list of targets.
        :param dict config: The configuration to use, if overriding defaults.
        :param str analysis_label: The label of the analysis, if running an analysis gear.
        :param list tags: The list of tags to set for the job.
        :param str priority: The priority of the job.
        :param str optional_input_policy: The optional input policy, default is 'ignored'

        :return: The batch proposal, which can be started with proposal.run()
        """
        invocation = self.create_invocation()

        if config is not None:
            invocation.update_config(config)
        if analysis_label is not None:
            invocation.set_analysis_label(analysis_label)
        if tags is not None:
            invocation.add_tags(tags)
        if priority is not None:
            invocation.set_priority(priority)

        return invocation.propose_batch(containers, optional_input_policy=optional_input_policy)

    def get_series(self):
        """Get gear series by gear name."""
        return self._invoke_gear_api("get_gear_series")

    def add_permission(self, permission_type, permission_id):
        """Add individual permission to gear."""
        return self._invoke_gear_api("add_gear_permission", permission_type, permission_id)

    def replace_permissions(self, permissions):
        """Replace gear permissions."""
        return self._invoke_gear_api("replace_gear_permissions", permissions)

    def delete_permission(self, permission_type, permission_id):
        """Delete individual permission by type and id"""
        self._invoke_gear_api("delete_gear_permission", permission_type, permission_id)

    def delete_all_permissions(self):
        """
        Delete gear all permissions. Also sets `is_restricted` on the gear
            series to `False`.
        """
        self._invoke_gear_api("delete_gear_permissions")

    def modify_gear_series(self, gear_series_update):
        """
        Modify the gear series attributes such as `is_restricted`

        :param GearSeriesUpdate gear_series_update: the dictionary specifying
            the updates to make to the gear series

        Example::
            update_dict = {"is_restricted": True}
            gear.modify_gear_series(update_dict)
        """
        return self._invoke_gear_api("modify_gear_series", gear_series_update)
