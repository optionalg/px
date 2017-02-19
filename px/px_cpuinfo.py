import os
import errno
import subprocess


def get_core_count():
    """
    Count the number of cores in the system.

    Returns a tuple (physical, logical) with counts of physical and logical
    cores.
    """
    return_me = get_core_count_from_proc_cpuinfo()
    if return_me is not None:
        return return_me

    return_me = get_core_count_from_sysctl()
    if return_me is not None:
        return return_me

    return None


def get_core_count_from_proc_cpuinfo(proc_cpuinfo="/proc/cpuinfo"):
    # Note the ending spaces, they must be there for number extraction to work!
    PROCESSOR_NO_PREFIX = 'processor\t: '
    CORE_ID_PREFIX = 'core id\t\t: '

    try:
        with open(proc_cpuinfo) as f:
            max_core_id = 0
            max_processor_no = 0

            for line in f:
                if line.startswith(PROCESSOR_NO_PREFIX):
                    processor_no = int(line[len(PROCESSOR_NO_PREFIX):])
                    max_processor_no = max(processor_no, max_processor_no)
                elif line.startswith(CORE_ID_PREFIX):
                    core_id = int(line[len(CORE_ID_PREFIX)])
                    max_core_id = max(core_id, max_core_id)

            return (max_core_id + 1, max_processor_no + 1)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # /proc/cpuinfo not found, we're probably not on Linux
            return None

        raise


def get_core_count_from_sysctl():
    env = os.environ.copy()
    if "LANG" in env:
        del env["LANG"]

    try:
        sysctl = subprocess.Popen(["sysctl", 'hw'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  env=env)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # sysctl not found, we're probably not on OSX
            return None

        raise

    sysctl_stdout = sysctl.communicate()[0].decode('utf-8')
    sysctl_lines = sysctl_stdout.split('\n')

    # Note the ending spaces, they must be there for number extraction to work!
    PHYSICAL_PREFIX = 'hw.physicalcpu: '
    LOGICAL_PREFIX = 'hw.logicalcpu: '

    physical = None
    logical = None
    for line in sysctl_lines:
        if line.startswith(PHYSICAL_PREFIX):
            physical = int(line[len(PHYSICAL_PREFIX):])
        elif line.startswith(LOGICAL_PREFIX):
            logical = int(line[len(LOGICAL_PREFIX)])

    return (physical, logical)
