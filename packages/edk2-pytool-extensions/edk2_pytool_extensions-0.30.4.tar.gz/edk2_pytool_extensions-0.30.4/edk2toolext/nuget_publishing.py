# @file NugetPublishing.py
# This tool allows a user to create a configuration for nuget as well as
# pack and push (publishing) a release to a feed.
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
"""Provides configuration, packing, and publishing nuget packages to a release feed."""

import argparse
import datetime
import logging
import os
import shutil
import sys
import xml.etree.ElementTree as etree
from io import StringIO
from typing import Optional

import yaml
from edk2toollib.utility_functions import RunCmd

from edk2toolext.environment.extdeptypes.nuget_dependency import NugetDependency

# Use associated SPDX license Identifier
# https://learn.microsoft.com/en-us/nuget/reference/nuspec#license
LICENSE_IDENTIFIER_SUPPORTED = {
    "BSD2": "BSD-2-Clause",
    "BSD3": "BSD-3-Clause",
    "APACHE2": "Apache-2.0",
    "MSPL": "MS-PL",  # Microsoft Public License
    "MIT": "MIT",
    "BSD2pP": "BSD-2-Clause-Patent",  # BSD2 + Patent
}


class NugetSupport(object):
    """Support object for Nuget Publishing tool to configure NuPkg information, pack and send."""

    # NOTE: This *should* have a namespace (http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd)
    #       but ElementTree is incredibly stupid with namespaces.
    NUSPEC_TEMPLATE_XML = r"""<?xml version="1.0" encoding="utf-8"?>
<package>
    <metadata>
        <!-- Required elements-->
        <id></id>
        <version></version>
        <description></description>
        <authors></authors>

        <!-- Optional elements -->
        <license></license>
        <releaseNotes></releaseNotes>
        <projectUrl></projectUrl>
        <repository />
        <copyright></copyright>
        <tags></tags>
    </metadata>
    <!-- Optional 'files' node -->
    <files>
        <file src="" target="" />
    </files>
</package>"""

    RELEASE_NOTE_SHORT_STRING_MAX_LENGTH = 500

    def __init__(self, Name: Optional[str] = None, ConfigFile: Optional[str] = None) -> None:
        """Inits a new NugetSupport object.

        for new instances without existing config provide the Name parameter.
        for creating instance based on config file provide the path to the ConfigFile
        """
        self.Name = Name
        self.TempFileToDelete = []  # everytime a temp is created add to list to cleanup
        self.NewVersion = None
        self.ConfigChanged = False

        if ConfigFile is not None:
            self.FromConfigfile(ConfigFile)
            self.Name = self.ConfigData["name"]
        else:
            if Name is None:
                raise ValueError("Cannot construct object with both Name and ConfigFile as None")
            self.ConfigData = {"name": Name}
            self.Config = None

    def CleanUp(self) -> None:
        """Remove all temporary files."""
        logging.debug("CleanUp Called.  Deleting all Temp Files")
        for a in self.TempFileToDelete:
            os.remove(a)

    def ToConfigFile(self, filepath: Optional[str] = None) -> int:
        """Save config to a yaml file."""
        if not self.ConfigChanged:
            logging.debug("No Config Changes.  Skip Writing config file")
            return 0

        if filepath is None and self.Config is None:
            logging.error("No Config File to save to.")
            return -1

        if filepath is not None:
            self.Config = filepath

        if filepath is None:
            logging.error("No filepath for Config File")

        with open(filepath, "w") as c:
            yaml.dump(self.ConfigData, c, indent=4)
        logging.debug("Wrote config file to: %s" % filepath)
        self.ConfigChanged = False
        return 0

    def FromConfigfile(self, filepath: str) -> None:
        """Load config from a yaml file."""
        self.Config = filepath
        with open(self.Config, "r") as c:
            self.ConfigData = yaml.safe_load(c)

    def SetBasicData(
        self,
        authors: str,
        license: str,
        project: str,
        description: str,
        server: str,
        copyright: str,
        repositoryType: Optional[str] = None,
        repositoryUrl: Optional[str] = None,
        repositoryBranch: Optional[str] = None,
        repositoryCommit: Optional[str] = None,
    ) -> None:
        """Set basic data in the config data."""
        self.ConfigData["author_string"] = authors
        if license:
            self.ConfigData["license"] = license
        self.ConfigData["project_url"] = project
        self.ConfigData["description_string"] = description
        self.ConfigData["server_url"] = server
        if repositoryType:
            self.ConfigData["repository_type"] = repositoryType
        if repositoryUrl:
            self.ConfigData["repository_url"] = repositoryUrl
        if repositoryBranch:
            self.ConfigData["repository_branch"] = repositoryBranch
        if repositoryCommit:
            self.ConfigData["repository_commit"] = repositoryCommit
        if not copyright:
            copyright = "Copyright %d" % datetime.date.today().year
        self.ConfigData["copyright_string"] = copyright

        self.ConfigData["tags_string"] = ""

        self.ConfigChanged = True

    def UpdateLicensePath(self, licensepath: str) -> None:
        """Update license in the config data.

        Update license in the config data with an absolute path to a license
        to pack.
        """
        self.ConfigData["license"] = licensepath

    def IsValidLicense(self) -> bool:
        """Returns whether the License is valid."""
        if "license" not in self.ConfigData:
            return False

        license = self.ConfigData["license"]

        if license in LICENSE_IDENTIFIER_SUPPORTED.values():
            return True

        if not os.path.isabs(license) or not os.path.isfile(license):
            return False

        if os.path.basename(license).lower() not in ["license.txt", "license.md"]:
            return False

        return True

    def UpdateCopyright(self, copyright: str) -> None:
        """Update copyright in the config data."""
        self.ConfigData["copyright_string"] = copyright
        self.ConfigChanged = True

    def UpdateTags(self, tags: list[str] = None) -> None:
        """Update tags in the config data."""
        if tags is None:
            tags = []
        self.ConfigData["tags_string"] = " ".join(tags)
        self.ConfigChanged = True

    def UpdateRepositoryInfo(
        self,
        r_type: Optional[str] = None,
        url: Optional[str] = None,
        branch: Optional[str] = None,
        commit: Optional[str] = None,
    ) -> None:
        """Update repository information."""
        if r_type:
            self.ConfigData["repository_type"] = r_type
            self.ConfigChanged = True
        if url:
            self.ConfigData["repository_url"] = url
            self.ConfigChanged = True
        if branch:
            self.ConfigData["repository_branch"] = branch
            self.ConfigChanged = True
        if commit:
            self.ConfigData["repository_commit"] = commit
            self.ConfigChanged = True

    def Print(self) -> str:
        """Print info about the Nuget Object."""
        print("=======================================")
        print(" Name:        " + self.Name)
        if self.Config:
            print(" ConfigFile:  " + self.Config)
        else:
            print(" ConfigFile:  NOT SET")

        for k, v in self.ConfigData.items():
            print(" %s:   %s" % (k, v))

        print("----------------------------------------")
        print(" Temp Files List: ")
        for a in self.TempFileToDelete:
            print("    " + a)
        print("-----------------------------------------")
        print("=======================================")

    def LogObject(self) -> None:
        """Logs info about Nuget Object to the logger."""
        logging.debug("=======================================")
        logging.debug(" Name:        " + self.Name)
        if self.Config:
            logging.debug(" ConfigFile:  " + self.Config)
        else:
            logging.debug(" ConfigFile:  NOT SET")

        for k, v in self.ConfigData.items():
            logging.debug(" %s:   %s" % (k, v))

        logging.debug("----------------------------------------")
        logging.debug(" Temp Files List: ")
        for a in self.TempFileToDelete:
            logging.debug("    " + a)
        logging.debug("-----------------------------------------")
        logging.debug("=======================================")

    #
    # given NugetSupport object
    # create a nuspec file for packing
    #

    def _MakeNuspecXml(self, ContentDir: str, ReleaseNotesText: Optional[str] = None) -> str:
        package = etree.fromstring(NugetSupport.NUSPEC_TEMPLATE_XML)
        package.attrib["xmlns"] = "http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd"
        meta = package.find("./metadata")
        meta.find("id").text = self.Name
        meta.find("version").text = self.NewVersion
        meta.find("authors").text = self.ConfigData["author_string"]
        meta.find("projectUrl").text = self.ConfigData["project_url"]
        repository_item_present = bool([k for k in self.ConfigData.keys() if "repository" in k.lower()])
        r = meta.find("repository")
        if repository_item_present:
            if "repository_type" in self.ConfigData:
                r.set("type", self.ConfigData["repository_type"])
            if "repository_url" in self.ConfigData:
                r.set("url", self.ConfigData["repository_url"])
            if "repository_branch" in self.ConfigData:
                r.set("branch", self.ConfigData["repository_branch"])
            if "repository_commit" in self.ConfigData:
                r.set("commit", self.ConfigData["repository_commit"])
        else:
            meta.remove(r)
        meta.find("description").text = self.ConfigData["description_string"]
        meta.find("copyright").text = self.ConfigData["copyright_string"]
        if "tags_string" in self.ConfigData:
            meta.find("tags").text = self.ConfigData["tags_string"]
        files = package.find("files")
        f = files.find("file")
        f.set("target", self.Name)
        f.set("src", ContentDir + "\\**\\*")

        # Add appropriate attribute to the license element depending on if the
        # license is custom or not. If the license is custom, add a new file
        # element pointing at the license
        if os.path.isfile(self.ConfigData["license"]):
            meta.find("license").text = os.path.basename(self.ConfigData["license"])
            meta.find("license").attrib["type"] = "file"
            f = etree.Element("file", attrib={"src": self.ConfigData["license"], "target": ""})
            files.append(f)
        else:
            meta.find("license").text = self.ConfigData["license"]
            meta.find("license").attrib["type"] = "expression"

        if ReleaseNotesText is not None:
            logging.debug("Make Nuspec Xml - ReleaseNotesText is not none.")
            #
            # Make sure it doesn't exceed reasonable length of string
            #
            if len(ReleaseNotesText) > NugetSupport.RELEASE_NOTE_SHORT_STRING_MAX_LENGTH:
                logging.info("Make Nuspec Xml - ReleaseNotesText too long.  Length is (%d)" % len(ReleaseNotesText))
                logging.debug("Original ReleaseNotesText is: %s" % ReleaseNotesText)
                # cut it off at max length
                ReleaseNotesText = ReleaseNotesText[: NugetSupport.RELEASE_NOTE_SHORT_STRING_MAX_LENGTH]
                # walk back to trim at last end of sentence
                ReleaseNotesText = ReleaseNotesText.rpartition(".")[0].strip()
                logging.debug("New ReleaseNotesText is: %s" % ReleaseNotesText)

            meta.find("releaseNotes").text = ReleaseNotesText
        else:
            logging.debug("Make Nuspec Xml - ReleaseNotesText None. Removing element from nuspec.")
            meta.remove(meta.find("releaseNotes"))

        return etree.tostring(package)

    def _GetNuPkgFileName(self, version: str) -> str:
        # Nuget removes leading zeros so to match we must do the same
        s = self.Name + "."
        append_tag = None
        parts = version.split(".")
        if "-" in parts[-1]:
            parts[-1], append_tag = parts[-1].split("-")
        int_parts = [str(int(a)) for a in parts]

        # nuget must have at least x.y.z and will make zero any element undefined
        for _ in range(len(int_parts), 3):
            int_parts.append("0")
        # Join the integers together
        s += ".".join(int_parts)
        if append_tag is not None:
            s += f"-{append_tag}"
        s += ".nupkg"
        return s

    def Pack(self, version: str, OutputDir: str, ContentDir: str, RelNotes: Optional[str] = None) -> int:
        """Pack the current contents into Nupkg."""
        self.NewVersion = version

        # content must be absolute path in nuspec otherwise it is assumed
        # relative to nuspec file.
        cdir = os.path.abspath(ContentDir)

        # make nuspec file
        xmlstring = self._MakeNuspecXml(cdir, RelNotes)
        nuspec = os.path.join(OutputDir, self.Name + ".nuspec")
        self.TempFileToDelete.append(nuspec)
        f = open(nuspec, "wb")
        f.write(xmlstring)
        f.close()

        # run nuget
        cmd = NugetDependency.GetNugetCmd()
        cmd += ["pack", nuspec]
        cmd += ["-OutputDirectory", '"' + OutputDir + '"']
        cmd += ["-Verbosity", "detailed"]
        # cmd += ["-NonInteractive"]
        ret = RunCmd(cmd[0], " ".join(cmd[1:]))

        if ret != 0:
            logging.error("Failed on nuget command.  RC = 0x%x" % ret)
            return ret

        self.NuPackageFile = os.path.join(OutputDir, self._GetNuPkgFileName(self.NewVersion))
        self.TempFileToDelete.append(self.NuPackageFile)
        return ret

    def Push(self, nuPackage: str, apikey: str) -> int:
        """Push nuget package to the server.

        Raises:
            (Exception): file path is invalid
        """
        if not os.path.isfile(nuPackage):
            raise Exception("Invalid file path for NuPkg file")
        logging.debug("Pushing %s file to server %s" % (nuPackage, self.ConfigData["server_url"]))

        cmd = NugetDependency.GetNugetCmd()
        cmd += ["push", nuPackage]
        cmd += ["-Verbosity", "detailed"]
        # cmd += ["-NonInteractive"]
        cmd += ["-Source", self.ConfigData["server_url"]]
        cmd += ["-ApiKey", apikey]
        output_buffer = StringIO()
        ret = RunCmd(cmd[0], " ".join(cmd[1:]), outstream=output_buffer)

        if ret != 0:
            # Rewind the buffer and capture the contents.
            output_buffer.seek(0)
            output_contents = output_buffer.read()

            # Check for the API message.
            if "API key is invalid".lower() in output_contents.lower():
                logging.critical("API key is invalid. Please use --ApiKey to provide a valid key.")

            # Generic error.
            logging.error("Failed on nuget command.  RC = 0x%x" % ret)

        return ret


def GatherArguments() -> argparse.Namespace:
    """Adds CLI arguments for controlling the nuget_publishing tool."""
    tempparser = argparse.ArgumentParser(
        description="Nuget Helper Script for creating, packing, and pushing packages", add_help=False
    )
    tempparser.add_argument("--Operation", dest="op", choices=["New", "Pack", "Push", "PackAndPush"], required=True)

    # Get the operation the user wants to do
    (args, rest) = tempparser.parse_known_args()

    # now build up the real parser with required parameters
    parser = argparse.ArgumentParser(description="Nuget Helper Script for creating, packing, and pushing packages")
    parser.add_argument("--Dirty", dest="Dirty", action="store_true", help="Keep all temp files", default=False)
    parser.add_argument("--Operation", dest="Operation", choices=["New", "Pack", "Push", "PackAndPush"], required=True)
    parser.add_argument("--OutputLog", dest="OutputLog", help="Create an output log file")

    if args.op.lower() == "new":
        parser.add_argument(
            "--ConfigFileFolderPath",
            dest="ConfigFileFolderPath",
            help="<Required>Path to folder to save new config file to",
            required=True,
        )
        parser.add_argument(
            "--Name",
            dest="Name",
            help="<Required> The unique id/name of the package.  This is a string naming the package",
            required=True,
        )
        parser.add_argument("--Author", dest="Author", help="<Required> Author string for publishing", required=True)
        parser.add_argument("--ProjectUrl", dest="Project", help="<Required> Project Url", required=True)
        repo_group = parser.add_argument_group(
            title="Repository Parameters", description="Optional Repository Parameters"
        )
        repo_group.add_argument(
            "--RepositoryType", dest="RepositoryType", help="<Optional> Repository Type", required=False
        )
        repo_group.add_argument(
            "--RepositoryUrl", dest="RepositoryUrl", help="<Optional> Repository Url", required=False
        )
        repo_group.add_argument(
            "--RepositoryBranch", dest="RepositoryBranch", help="<Optional> Repository Branch", required=False
        )
        repo_group.add_argument(
            "--RepositoryCommit", dest="RepositoryCommit", help="<Optional> Repository Commit", required=False
        )
        parser.add_argument(
            "--LicenseIdentifier",
            dest="LicenseIdentifier",
            default=None,
            choices=LICENSE_IDENTIFIER_SUPPORTED.keys(),
            help="Standard Licenses",
        )
        parser.add_argument(
            "--Description", dest="Description", help="<Required> Description of package.", required=True
        )
        parser.add_argument(
            "--FeedUrl", dest="FeedUrl", help="<Required>Feed Url of the nuget server feed", required=True
        )
        parser.add_argument("--Copyright", dest="Copyright", help="Copyright string", required=False)

    elif args.op.lower() == "pack" or args.op.lower() == "packandpush":
        parser.add_argument(
            "--ConfigFilePath", dest="ConfigFilePath", help="<Required>Path to config file", required=True
        )
        parser.add_argument("--Version", dest="Version", help="<Required> Version to publish", required=True)
        parser.add_argument(
            "--ReleaseNotesText", dest="ReleaseNotes", help="<Optional>Release Notes String", required=False
        )
        parser.add_argument(
            "--InputFolderPath",
            dest="InputFolderPath",
            help="<Required>Relative/Absolute Path to folder containing content to pack.",
            required=True,
        )
        parser.add_argument("--Copyright", dest="Copyright", help="<Optional>Change the Copyright string")
        parser.add_argument(
            "--t",
            "-tag",
            dest="Tags",
            type=str,
            help="<Optional>Add tags to the nuspec. Multiple are --t Tag1,Tag2 or --t Tag1 --t Tag2",
            action="append",
            default=[],
        )
        parser.add_argument(
            "--ApiKey",
            dest="ApiKey",
            help="<Optional>Api key to use. Default is 'VSTS' which will invoke interactive login",
            default="VSTS",
        )
        parser.add_argument(
            "--CustomLicensePath",
            dest="CustomLicensePath",
            default=None,
            help="<Optional> If CustomLicense set in `new` phase, provide absolute path of License \
                            File to pack. Does not override existing valid license.",
        )
        repo_group = parser.add_argument_group(
            title="Repository Parameters", description="Optional Repository Parameters"
        )
        repo_group.add_argument(
            "--RepositoryType", dest="RepositoryType", help="<Optional> Repository Type", required=False
        )
        repo_group.add_argument(
            "--RepositoryUrl", dest="RepositoryUrl", help="<Optional> Change the repository Url", required=False
        )
        repo_group.add_argument(
            "--RepositoryBranch",
            dest="RepositoryBranch",
            help="<Optional> Change the repository branch",
            required=False,
        )
        repo_group.add_argument(
            "--RepositoryCommit",
            dest="RepositoryCommit",
            help="<Optional> Change the repository commit",
            required=False,
        )

    elif args.op.lower() == "push":
        parser.add_argument(
            "--ConfigFilePath", dest="ConfigFilePath", help="<Required>Path to config file", required=True
        )
        parser.add_argument("--PackageFile", dest="PackageFile", help="<Required>Path To Package File", required=True)
        parser.add_argument(
            "--ApiKey",
            dest="ApiKey",
            help="<Optional>Api key to use. Default is 'VSTS' which will invoke interactive login",
            default="VSTS",
        )

    if args.op.lower() == "pack":
        parser.add_argument(
            "--OutputFolderPath",
            dest="OutputFolderPath",
            help="<Optional>Output folder where nupkg will be saved.  Default is cwd",
            default=os.getcwd(),
        )

    return parser.parse_args()


def main() -> int:
    """Entry point into nuget_publishing after initial configuration."""
    args = GatherArguments()
    ret = 0

    # setup file based logging if outputReport specified
    if args.OutputLog:
        if len(args.OutputLog) < 2:
            logging.critical("the output log file parameter is invalid")
            return -2

        # setup file based logging
        filelogger = logging.FileHandler(filename=args.OutputLog, mode="w")
        filelogger.setLevel(logging.DEBUG)
        logging.getLogger("").addHandler(filelogger)

    logging.info("Log Started: " + datetime.datetime.strftime(datetime.datetime.now(), "%A, %B %d, %Y %I:%M%p"))

    TempOutDir = None
    NuPkgFilePath = None

    if args.Operation.lower() == "new":
        logging.critical("Generating new nuget configuration...")
        logging.debug("Checking input parameters for new")
        ConfigFilePath = os.path.join(args.ConfigFileFolderPath, args.Name.strip() + ".config.yaml")

        if not os.path.isdir(args.ConfigFileFolderPath):
            logging.critical("Config File Folder Path doesn't exist.  %s" % args.ConfigFileFolderPath)
            raise Exception("Invalid Config File Folder.  Doesn't exist")

        if os.path.isfile(ConfigFilePath):
            logging.critical("Config File already exists at that path.  %s" % ConfigFilePath)
            raise Exception("Can't Create New Config file when file already exists")

        nu = NugetSupport(Name=args.Name)

        # Provide Standard License Identifier in New Command
        # Or provide Custom License Path in Pack Command.
        if args.LicenseIdentifier is None:
            license = None
        else:
            license = LICENSE_IDENTIFIER_SUPPORTED[args.LicenseIdentifier]

        nu.SetBasicData(
            args.Author,
            license,
            args.Project,
            args.Description,
            args.FeedUrl,
            args.Copyright,
            args.RepositoryType,
            args.RepositoryUrl,
            args.RepositoryBranch,
            args.RepositoryCommit,
        )
        nu.LogObject()
        ret = nu.ToConfigFile(ConfigFilePath)
        return ret

    elif args.Operation.lower() == "pack" or args.Operation.lower() == "packandpush":
        logging.critical("Creating nuget package")
        logging.debug("Checking input parameters for packing")
        # check args
        if not os.path.isfile(args.ConfigFilePath):
            logging.critical("Invalid Config File (%s).  File doesn't exist" % args.ConfigFilePath)
            raise Exception("Invalid Config File.  File doesn't exist")
        if not os.path.isdir(args.InputFolderPath):
            logging.critical("Invalid Input folder (%s).  Folder doesn't exist" % args.InputFolderPath)
            raise Exception("Invalid Input folder.  folder doesn't exist")
        contents = os.listdir(args.InputFolderPath)
        logging.debug("Input Folder contains %d files" % len(contents))
        if len(contents) == 0:
            logging.critical("No binary contents to pack in %s" % args.InputFolderPath)
            raise Exception("No binary contents to package")

        # make a temp dir for the pack operation which actually creates files
        TempOutDir = os.path.join(os.getcwd(), "_TEMP_" + str(datetime.datetime.now().time()).replace(":", "_"))
        os.mkdir(TempOutDir)

        nu = NugetSupport(ConfigFile=args.ConfigFilePath)

        if not nu.IsValidLicense():
            # Invalid License and not setting it with a custom License
            if args.CustomLicensePath is None:
                logging.critical("Standard License not found in config file and custom license not provided.")
                logging.critical("Provide a custom license path with --CustomLicensePath.")
                raise Exception("Invalid License.")
            nu.UpdateLicensePath(args.CustomLicensePath)

        if not nu.IsValidLicense():
            logging.critical("Invalid Custom License")
            logging.critical("    Verify custom license file name is license.txt or license.md")
            logging.critical("    Verify custom license file path is in absolute format and valid")
            raise Exception("Invalid License.")

        if args.Copyright is not None:
            nu.UpdateCopyright(args.Copyright)

        nu.UpdateRepositoryInfo(args.RepositoryType, args.RepositoryUrl, args.RepositoryBranch, args.RepositoryCommit)

        if len(args.Tags) > 0:
            tagListSet = set()
            for item in args.Tags:  # Parse out the individual packages
                item_list = item.split(",")
                for individual_item in item_list:
                    # in case cmd line caller used Windows folder slashes
                    individual_item = individual_item.replace("\\", "/")
                    tagListSet.add(individual_item.strip())
            tagList = list(tagListSet)
            nu.UpdateTags(tagList)
        """
        ret = nu.ToConfigFile()
        if (ret != 0):
            logging.error("Failed to save config file.  Return Code 0x%x" % ret)
            return ret
        """

        ret = nu.Pack(args.Version, TempOutDir, args.InputFolderPath, args.ReleaseNotes)
        if ret != 0:
            logging.error("Failed to pack.  Return Code 0x%x" % ret)
            return ret

        NuPkgFilePath = nu.NuPackageFile

    if args.Operation.lower() == "pack":
        if not os.path.isdir(args.OutputFolderPath):
            logging.critical("Invalid Pack Output Folder (%s).  Folder doesn't exist" % args.OutputFolderPath)
            raise Exception("Invalid Output folder.  folder doesn't exist")
        # since it is pack only lets copy nupkg file to output
        shutil.copyfile(NuPkgFilePath, os.path.join(args.OutputFolderPath, os.path.basename(NuPkgFilePath)))
        NuPkgFilePath = os.path.join(args.OutputFolderPath, os.path.basename(NuPkgFilePath))

    if args.Operation.lower() == "push":
        # set the parameters for push
        logging.debug("Checking input parameters for push")
        # check args
        if not os.path.isfile(args.ConfigFilePath):
            logging.critical("Invalid Config File (%s).  File doesn't exist" % args.ConfigFilePath)
            raise Exception("Invalid Config File.  File doesn't exist")
        NuPkgFilePath = args.PackageFile
        nu = NugetSupport(ConfigFile=args.ConfigFilePath)

    if args.Operation.lower() == "push" or args.Operation.lower() == "packandpush":
        # do the pushing
        logging.critical("Pushing the package")
        logging.debug("NuPkgFilePath is %s" % NuPkgFilePath)
        # check args
        if not os.path.isfile(NuPkgFilePath):
            logging.critical("NuPkgFilePath is not valid file.  %s" % NuPkgFilePath)
            raise Exception("Invalid Pkg File.  File doesn't exist")
        ret = nu.Push(NuPkgFilePath, args.ApiKey)

    nu.LogObject()
    nu.ToConfigFile(args.ConfigFilePath)  # save any changes
    if not args.Dirty:
        nu.CleanUp()
        if TempOutDir is not None:
            os.removedirs(TempOutDir)
    return ret


def go() -> None:
    """Main entry into the nuget publishing tool."""
    # setup main console as logger
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # call main worker function
    retcode = main()

    if retcode != 0:
        logging.critical("Failed.  Return Code: %d" % retcode)
    else:
        logging.critical("Success!")
    # end logging
    logging.shutdown()
    sys.exit(retcode)


if __name__ == "__main__":
    go()
