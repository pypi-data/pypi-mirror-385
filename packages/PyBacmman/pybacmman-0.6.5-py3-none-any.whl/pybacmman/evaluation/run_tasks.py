import shutil
import subprocess
import os
from os import listdir
from os.path import isfile, join

def run_bacmman_task(bacmmanFolder:str, taskFile:str, logFile:str=None, progressCallback=None, verbose=1):
    """Helper method to execute a bacmman task command, display its progress and log messages

    Parameters
    ----------
    bacmmanFolder : str
        directory containing of bacmman-headless-<VERSION>.jar and dependencies. e.g. compile bacmman with the command: mvn clean dependency:copy-dependencies package -DskipTests
    taskFile : str
        path of the .json task file to execute
    logFile : str
        None or path of a file where all log messages will be append
    progressCallback : executable
        callback to display progress of the task. Called with the progress as an int in range [0,100]. use getJNBProgressBar for jupyter notebooks
    verbose : int in range [0,2]
        verbose level. if >1 all log message are displayed, if ==1 only main messages are displayed, if 0 none are displayed

    Returns
    -------
    type
        result of runCommand method
    """

    # grab bacmman-headless file (depends on version)
    getjar = lambda folder : [join(folder,f) for f in listdir(folder) if f.startswith("bacmman-headless-") and f.endswith(".jar")]
    bheadlessjar = getjar(bacmmanFolder)
    if len(bheadlessjar)==0:
        if os.path.isdir(join(bacmmanFolder, "target")):
            bacmmanFolder = join(bacmmanFolder, "target")
            bheadlessjar = getjar(bacmmanFolder)
        elif os.path.isdir(join(bacmmanFolder, "bacmman-headless", "target")):
            bacmmanFolder = join(bacmmanFolder, "bacmman-headless", "target")
            bheadlessjar = getjar(bacmmanFolder)
        elif os.path.isdir(join(bacmmanFolder, "bacmman", "bacmman-headless", "target")):
            bacmmanFolder =join(bacmmanFolder, "bacmman", "bacmman-headless", "target")
            bheadlessjar = getjar(bacmmanFolder)

    if len(bheadlessjar)==0:
        raise ValueError("bacmman-headless .jar file not found in dir:", bacmmanFolder)
    elif len(bheadlessjar)>1:
        raise ValueError("{} bacmman-headless .jar file found in dir: {}".format(len(bheadlessjar), bacmmanFolder))
    dep_folder = join(bacmmanFolder, "dependency")
    if not os.path.isdir(dep_folder):
        raise ValueError("dependency folder not found in dir:", bacmmanFolder)
    if not os.path.isfile(taskFile):
        raise ValueError("task file {} not found".format(taskFile))
    if os.name == 'nt': # windows
        cmd = "java -cp {}\*;{} bacmman.ui.ProcessTasks {}{}".format(dep_folder, bheadlessjar[0], taskFile, " "+logFile if logFile else "")
    else:
        cmd = "java -cp {}/*:{} bacmman.ui.ProcessTasks {}{}".format(dep_folder, bheadlessjar[0], taskFile, " "+logFile if logFile else "")
    print("Command : ", cmd)
    return run_command(cmd, progressCallback, verbose)

def run_command(cmd:str, progressCallback=None, verbose = 1):
    """Helper method to execute a (bacmman task) command, display its progress and log messages

    Parameters
    ----------
    cmd : str
        shell command
    progressCallback : executable
        callback to display progress of the task. Called with the progress as an int in range [0,100]. use getJNBProgressBar for jupyter notebooks
    verbose : int in range [0,2]
        verbose level. if >1 all log message are displayed, if ==1 only main messages are displayed, if 0 none are displayed

    Returns
    -------
    type
        tuple (error, exit_code)
        error : whether there was errors during the execution of the task by BACMMAN
        exit_code: exit code of the execution of the shell command

    """
    import shlex
    errorMessages = (">Error", ">Invalid Task Error")
    noErrorMessages=(">Errors: 0")
    logMessages = (">Run task: ", ">All jobs finished")
    with subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        error = False
        if verbose>0:
            if progressCallback is not None:
                progressCallback(0)
            for line in p.stdout:
                if line.startswith(">Progress: "):
                    if progressCallback is not None:
                        progressCallback(int(line.split(" ")[1][:-2]))
                elif line.startswith(errorMessages):
                    if not line.startswith(noErrorMessages):
                        error = True
                        print(line, end='', flush=True)
                elif verbose>1 or line.startswith(logMessages):
                    print(line, end='', flush=True)
        exit_code = p.poll()
    return error, exit_code

def get_jnb_progress_bar():
    '''
        return a progress bar for jupyter-lab / jupyter notebook, to be used with the runCommand method
        requires ipywidgets
    '''
    from ipywidgets import IntProgress
    from IPython.display import display
    pb = IntProgress(min=0, max=100)
    display(pb)
    def callback(value):
        pb.value = value
    return callback
