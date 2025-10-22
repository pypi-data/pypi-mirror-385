from shutil import which

from ckan_pilot.root import TOOLS_SUPPORTED, logger


def check_tools(tools):
    """Check if tools are available"""
    for tool in tools:
        check_tool = which(tool)
        tool_found = True
        if check_tool:
            logger.debug("`{0}` found at: {1}".format(tool, check_tool))
        else:
            # Check if we support installation through ckan-pilot and if yes advise user to run tools install
            if tool in TOOLS_SUPPORTED:
                logger.error("`{0}` not found, please run `ckan-pilot tools install`".format(tool))
            else:
                logger.error(
                    "`{0}` not found, please install the necessary package providing it on your system".format(tool)
                )
            tool_found = False
    return tool_found
