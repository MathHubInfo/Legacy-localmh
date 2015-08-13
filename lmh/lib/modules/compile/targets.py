from lmh.lib.extenv import latexmlc_executable, pdflatex_executable, perl5env

import os

class Target():
    def __init__(self):
        pass
    def getExtension(self):
        pass
    def getTarget(self):
        pass
    def getEnvironment(self, args):
        return {}
    def build_command(self, repo, targets, args):
        # Load the right extension and add logging things
        script = "extension "+self.getExtension()+ " ; log+ "+self.getTarget()+"-result"

        # Get the environment settings.
        envstrings = " ; ".join(["envvar "+k+" \""+str(v)+"\"" for (k, v) in self.getEnvironment(args).iteritems()])


        # If we have some environment variables, add them to the script.
        if envstrings != "":
            script = script + " ; " + envstrings

        # get the targets
        targetstrings = " ; ".join(["build "+repo+" "+self.getTarget()+" "+t for t in targets])

        # if there are no targets, we have nothing to do.
        if targetstrings == "":
            return "exit"

        # else add the targets
        script = script + " ; " + targetstrings

        # and return the script.
        return script


class SMSTarget(Target):
    def __init__(self):
        pass
    def getExtension(self):
        return "info.kwarc.mmt.stex.SmsGenerator"
    def getTarget(self):
        return "sms"

class OMDOCTarget(Target):
    def __init__(self):
        pass
    def getEnvironment(self, args):
        env = perl5env(os.environ.copy())

        return {
            "LATEXMLC": latexmlc_executable,
            "LATEXMLPORT": args["worker_base"]+args["worker_id"],

            #"STEXSTYDIR": env["STEXSTYDIR"],
            "PERL5LIB": env["PERL5LIB"]
        }
    def getExtension(self):
        return "info.kwarc.mmt.stex.LaTeXML"
    def getTarget(self):
        return "latexml"

class PDFTarget(Target):
    def __init__(self):
        pass
    def getEnvironment(self, args):
        env = perl5env(os.environ.copy())

        return {
            "PDFLATEX": pdflatex_executable,

            #"STEXSTYDIR": env["STEXSTYDIR"],
            "PERL5LIB": env["PERL5LIB"]
        }
    def getExtension(self):
        return "info.kwarc.mmt.stex.PdfLatex"
    def getTarget(self):
        return "pdflatex"
