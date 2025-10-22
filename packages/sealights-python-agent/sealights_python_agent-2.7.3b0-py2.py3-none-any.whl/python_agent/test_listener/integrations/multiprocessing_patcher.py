import multiprocessing
import multiprocessing.process
import sys
import os
import time

# An attribute that will be set on the module to indicate that it has been
# monkey-patched.

PATCHED_MARKER = "_coverage$patched"

if tuple(sys.version_info) >= (3, 4):
    OriginalProcess = multiprocessing.process.BaseProcess
else:
    OriginalProcess = multiprocessing.Process

original_bootstrap = OriginalProcess._bootstrap


class ProcessWithCoverage(OriginalProcess):
    """A replacement for multiprocess.Process that starts coverage."""

    def _bootstrap(self, *args, **kwargs):
        """Wrapper around _bootstrap to start agent."""
        import logging

        log = logging.getLogger(__name__)
        try:
            log.info("Patching Process...")
        except Exception as e:
            log.error(f"Failed Initializing Agent. Error= {e}")

        # Optional child-start delay to avoid timing races with external resources (e.g., devices)
        # Set SEALIGHTS_MP_CHILD_DELAY_MS to a positive integer (milliseconds) to enable.
        try:
            delay_ms = int(os.environ.get("SEALIGHTS_MP_CHILD_DELAY_MS", "0") or "0")
            if delay_ms > 0:
                try:
                    log.info(f"Child bootstrap delay enabled: {delay_ms}ms")
                except Exception:
                    pass
                time.sleep(delay_ms / 1000.0)
        except Exception:
            # Never block child startup on parsing/sleep errors
            pass

        try:
            # Pass any additional arguments to the original _bootstrap method
            return original_bootstrap(self, *args, **kwargs)
        finally:
            try:
                from python_agent.test_listener.managers.agent_manager import (
                    AgentManager,
                )

                AgentManager().shutdown()
            except Exception as e:
                log.error(f"Failed Shutting Down Agent. Error= {e}")


class Stowaway(object):
    """An object to pickle, so when it is unpickled, it can apply the monkey-patch."""

    def __setstate__(self, state):
        patch_multiprocessing()


def patch_multiprocessing():
    """Monkey-patch the multiprocessing module.

    This enables coverage measurement of processes started by multiprocessing.
    This involves aggressive monkey-patching.

    """

    if hasattr(multiprocessing, PATCHED_MARKER):
        return

    if tuple(sys.version_info) >= (3, 4):
        OriginalProcess._bootstrap = ProcessWithCoverage._bootstrap
    else:
        multiprocessing.Process = ProcessWithCoverage

    # When spawning processes rather than forking them, we have no state in the
    # new process.  We sneak in there with a Stowaway: we stuff one of our own
    # objects into the data that gets pickled and sent to the sub-process. When
    # the Stowaway is unpickled, it's __setstate__ method is called, which
    # re-applies the monkey-patch.
    # Windows only spawns, so this is needed to keep Windows working.
    try:
        from multiprocessing import spawn

        original_get_preparation_data = spawn.get_preparation_data
    except (ImportError, AttributeError):
        pass
    else:

        def get_preparation_data_with_stowaway(name):
            """Get the original preparation data, and also insert our stowaway."""
            d = original_get_preparation_data(name)
            d["stowaway"] = Stowaway()
            return d

        spawn.get_preparation_data = get_preparation_data_with_stowaway

    setattr(multiprocessing, PATCHED_MARKER, True)
