import subprocess as sp

class Command:
    """
    A basic wrapper for Popen. 
    Command is compatible with the old, unecessarily comlpicated Command. This command will block execution as well, because AURIC commands have side effects.

    Parameters
    ----------
    cmd: list of strings
        list of the command and its arguments.
    env: dictionary
        dictionary of environment variables.
    cwd: string
        the path in which to execute the command
    """
    def __init__(self,cmd=[],env={},cwd=""):
        self.cmd = cmd
        self.env = env
        self.cwd = cwd

    def run(self, timeout=None):
        """Run the command.
        timeout is accepted for compatibility with the old version."""
        p = sp.Popen(self.cmd,env=self.env,cwd=self.cwd, stdout=sp.PIPE, stderr=sp.PIPE)
        code = p.wait(timeout)
        print(p.stdout.read().decode('utf-8'))
        print(p.stderr.read().decode('utf-8'))
        return code

class InputCommand(Command):
    def run(self,input_string=b'',timeout=None):
        """Run the command, optionally sending a string to stidn.
        
        Parameters
        ----------
        input_string: bytes
            input to communicate to stdin. Can include newlines.

        Returns
        -------
        code: int
            return code of the command
        """
        p = sp.Popen(self.cmd,env=self.env,cwd=self.cwd,stdin=sp.PIPE)
        if input_string:
            p.communicate(input_string)
        code = p.wait()
        return code
    
if __name__=="__main__":
    import os
    cmd = Command(["auric"]
                  , env={"AURIC_ROOT":"/home/geddes/auric"
                         , "PATH":os.getenv("PATH")+"/home/geddes/auric/bin/Linux"}
                  , cwd="/home/geddes/auric")
    print(cmd.run())
