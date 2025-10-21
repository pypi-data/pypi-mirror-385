import hashlib
import json
from enum import Enum, StrEnum
from typing import cast

from pydantic import BaseModel

from labels.model.advisories import Advisory
from labels.model.constraints import NonEmptyStr, TrimmedNonEmptyStr
from labels.model.ecosystem_data.aliases import AcceptedEcosystemData
from labels.model.file import Location
from labels.model.metadata import HealthMetadata


class Platform(StrEnum):
    ALPM = "ALPM"
    APK = "ALPINE"
    BINARY = "BINARY"
    CABAL = "CABAL"
    CARGO = "CARGO"
    COMPOSER = "COMPOSER"
    CONAN = "CONAN"
    CRAN = "CRAN"
    DEBIAN = "DEBIAN"
    ERLANG = "ERLANG"
    GEM = "GEM"
    GITHUB_ACTIONS = "GITHUB_ACTIONS"
    GO = "GO"
    GRAALVM_NATIVE_IMAGE = "GRAALVM_NATIVE_IMAGE"
    JENKINS_PLUGIN = "JENKINS_PLUGIN"
    LINUX_KERNEL = "LINUX_KERNEL"
    LINUX_KERNEL_MODULE = "LINUX_KERNEL_MODULE"
    MAVEN = "MAVEN"
    MSRC_KB = "MSRC_KB"
    NIXPKGS = "NIXPKGS"
    NPM = "NPM"
    NUGET = "NUGET"
    PIP = "PIP"
    PORTAGE = "PORTAGE"
    PUB = "PUB"
    RPM = "RPM"
    SWIFT = "SWIFT"
    UNKNOWN = "UNKNOWN"
    WORDPRESS_PLUGIN = "WORDPRESS_PLUGIN"


class Language(StrEnum):
    UNKNOWN_LANGUAGE = "unknown_language"
    CPP = "c++"
    DART = "dart"
    DOTNET = "dotnet"
    ELIXIR = "elixir"
    ERLANG = "erlang"
    GO = "go"
    GITHUB_ACTIONS = "github_actions"
    HASKELL = "haskell"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    PHP = "php"
    PYTHON = "python"
    R = "R"
    RUBY = "ruby"
    RUST = "rust"
    SWIFT = "swift"


class PackageType(Enum):
    UnknownPkg = "UnknownPackage"
    AlpmPkg = "alpm"
    ApkPkg = "apk"
    BinaryPkg = "binary"
    CocoapodsPkg = "pod"
    ConanPkg = "conan"
    DartPubPkg = "dart-pub"
    DebPkg = "deb"
    DotnetPkg = "dotnet"
    ErlangOTPPkg = "erlang-otp"
    GemPkg = "gem"
    GithubActionPkg = "github-action"
    GithubActionWorkflowPkg = "github-action-workflow"
    GoModulePkg = "go-module"
    GraalVMNativeImagePkg = "graalvm-native-image"
    HackagePkg = "hackage"
    HexPkg = "hex"
    JavaPkg = "java-archive"
    JenkinsPluginPkg = "jenkins-plugin"
    KbPkg = "msrc-kb"
    LinuxKernelPkg = "linux-kernel"
    LinuxKernelModulePkg = "linux-kernel-module"
    NixPkg = "nix"
    NpmPkg = "npm"
    PhpComposerPkg = "php-composer"
    PhpPeclPkg = "php-pecl-pkg"
    PortagePkg = "portage"
    PythonPkg = "python"
    Rpkg = "R-package"
    RpmPkg = "rpm"
    RustPkg = "rust-crate"
    SwiftPkg = "swift"
    WordpressPluginPkg = "wordpress-plugin"

    def get_platform_value(self) -> str | None:
        package_type_to_platform = {
            PackageType.CocoapodsPkg: Platform.SWIFT.value,
            PackageType.ConanPkg: Platform.CONAN.value,
            PackageType.DartPubPkg: Platform.PUB.value,
            PackageType.DotnetPkg: Platform.NUGET.value,
            PackageType.ErlangOTPPkg: Platform.ERLANG.value,
            PackageType.GemPkg: Platform.GEM.value,
            PackageType.GithubActionPkg: Platform.GITHUB_ACTIONS.value,
            PackageType.GithubActionWorkflowPkg: Platform.GITHUB_ACTIONS.value,
            PackageType.GoModulePkg: Platform.GO.value,
            PackageType.HackagePkg: Platform.CABAL.value,
            PackageType.HexPkg: Platform.ERLANG.value,
            PackageType.JavaPkg: Platform.MAVEN.value,
            PackageType.NpmPkg: Platform.NPM.value,
            PackageType.PhpComposerPkg: Platform.COMPOSER.value,
            PackageType.PhpPeclPkg: Platform.COMPOSER.value,
            PackageType.PythonPkg: Platform.PIP.value,
            PackageType.Rpkg: Platform.CRAN.value,
            PackageType.RustPkg: Platform.CARGO.value,
            PackageType.SwiftPkg: Platform.SWIFT.value,
            PackageType.AlpmPkg: Platform.ALPM.value,
            PackageType.ApkPkg: Platform.APK.value,
            PackageType.BinaryPkg: Platform.BINARY.value,
            PackageType.DebPkg: Platform.DEBIAN.value,
            PackageType.GraalVMNativeImagePkg: Platform.GRAALVM_NATIVE_IMAGE.value,
            PackageType.JenkinsPluginPkg: Platform.JENKINS_PLUGIN.value,
            PackageType.KbPkg: Platform.MSRC_KB.value,
            PackageType.LinuxKernelPkg: Platform.LINUX_KERNEL.value,
            PackageType.LinuxKernelModulePkg: Platform.LINUX_KERNEL_MODULE.value,
            PackageType.NixPkg: Platform.NIXPKGS.value,
            PackageType.PortagePkg: Platform.PORTAGE.value,
            PackageType.RpmPkg: Platform.RPM.value,
            PackageType.WordpressPluginPkg: Platform.WORDPRESS_PLUGIN.value,
            PackageType.UnknownPkg: None,
        }
        return package_type_to_platform.get(self, Platform.UNKNOWN.value)


class Package(BaseModel):
    name: NonEmptyStr
    version: TrimmedNonEmptyStr
    language: Language
    licenses: list[NonEmptyStr]
    locations: list[Location]
    type: PackageType
    advisories: list[Advisory] | None = None
    found_by: NonEmptyStr | None = None
    health_metadata: HealthMetadata | None = None
    ecosystem_data: AcceptedEcosystemData | None = None
    p_url: NonEmptyStr
    safe_versions: list[str] | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Package):
            return False

        self_dump = cast("dict[str, object]", self.model_dump())
        other_dump = cast("dict[str, object]", other.model_dump())

        return self_dump == other_dump

    def __hash__(self) -> int:
        return hash(self.id_)

    @property
    def id_(self) -> str:
        return self.id_by_hash()

    def id_by_hash(self) -> str:
        try:
            obj_data = {
                "name": self.name,
                "version": self.version,
                "language": self.language.value,
                "type": self.type.value,
                "p_url": self.p_url,
            }
            obj_str = json.dumps(obj_data, sort_keys=True)
            return hashlib.sha256(obj_str.encode()).hexdigest()
        except Exception as exc:
            error_message = "Package data invalid for ID generation: " + json.dumps(
                obj_data, sort_keys=True
            )
            raise ValueError(error_message) from exc
