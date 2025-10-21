import dataclasses
import os
import os.path
import subprocess
import xml.etree.ElementTree as et

from jl95terceira.batteries import *

class Pom:

    ns = '{http://maven.apache.org/POM/4.0.0}'

    def __init__(self,pom_path:str):

        with open(os.path.join(pom_path), 'r', encoding='utf-8') as f:

            self.et = et.parse(f)

    def version(self): return self.et.find(f'{Pom.ns}version').text

    def repo_ids(self):

        repos = self.et.find(f'{Pom.ns}repositories')
        if repos is None: return None
        return list(map(lambda repo: repo.find(f'{Pom.ns}id').text, repos.findall(f'{Pom.ns}repository')))
    
    def build(self): return self.et.find(f'{Pom.ns}build')

    def build_plugins(self): return self.build().find(f'{Pom.ns}plugins')

    def dependencies(self): return map(lambda dependency_elem: PomDependency(group_id  =dependency_elem.find(f'{Pom.ns}groupId'   ).text,
                                                                             artifact_id=dependency_elem.find(f'{Pom.ns}artifactId').text,
                                                                             version   =dependency_elem.find(f'{Pom.ns}version'   ).text), self.et.find(f'{Pom.ns}dependencies').findall(f'{Pom.ns}dependency'))

    def gpg_key_name(self):

        gpg_configuration = None
        for plugin in self.build_plugins():

            if plugin.find(f'{Pom.ns}groupId')    == 'org.apache.maven.plugins' and \
               plugin.find(f'{Pom.ns}artifactId') == 'maven-gpg-plugin': 
                
                for execution in plugin.find(f'{Pom.ns}executions'):

                    if execution.find(f'{Pom.ns}id') == 'sign-artifacts':

                        gpg_configuration = execution.find(f'{Pom.ns}configuration')

        if gpg_configuration is None: raise Exception('GPG build plugin not found in POM')
        return gpg_configuration.find(f'{Pom.ns}keyname')

@dataclasses.dataclass
class PomDependency:

    group_id   :str
    artifact_id:str
    version    :str

def foo(x:str):

    if (x == 'abc'):

        return 'abc'

    return int(x)

def is_installed(dep:PomDependency):

    return os.path.exists(os.path.join(os.path.expanduser('~'), 
                                       '.m2', 'repository', 
                                       *dep.group_id.split('.'), dep.artifact_id, dep.version,
                                       f'{dep.artifact_id}-{dep.version}.jar'))

def find_root(wd:str=None):

    if wd is None:

        return find_root(os.getcwd())

    return wd if 'pom.xml' in os.listdir(wd) else (lambda p: find_root(p[0]) if p[0] != wd else None)(os.path.split(wd))

def do_it(wd      :str,
          jdk_home:str,
          maven   :str,
          options :list[str]):

    pom      = Pom(os.path.join(wd,'pom.xml'))
    version  = pom.version ()
    print(f'Version: {version}')
    repo_ids = pom.repo_ids()
    print(f'Repository IDs: {repo_ids}')
    os.environ['JAVA_HOME'] = jdk_home
    print(f'Java home: {repr(os.environ['JAVA_HOME'])}')
    subprocess.run((maven, 
                    '--file', os.path.join(wd,'pom.xml'),
                    *options,), shell=True)

if __name__ == '__main__':

    import argparse
    import jl95terceira.pytools.envlib.vars.java as envars_java

    class A:

        WORKING_DIRECTORY  = 'wd'
        JDK                = 'jdk'
        JDK_HOME           = 'jdkhome'
        MAVEN              = 'maven'
        OPTIONS            = 'options'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
                                description    ='Simpler commands for Apache Maven\nThis tool can make use of pre-defined Java home paths, personal access tokens, etc')
    p.add_argument(f'--{A.WORKING_DIRECTORY}',
                   help   =f'working directory',
                   default='.')
    p.add_argument(f'--{A.JDK}',
                   help   =f'JDK version to use\nFor this option to work, the given JDK version\'s home must be mapped in variable {repr(envars_java.JDK_HOMES._name)}.',
                   default=None)
    p.add_argument(f'--{A.JDK_HOME}',
                   help   =f'home of JDK to use\nThis option is an alternative to option {repr('jdk')}',
                   default=None)
    p.add_argument(f'--{A.MAVEN}',
                   help   =f'Maven command - defaults to \'mvn\'',
                   default=None)
    p.add_argument(f'{A.OPTIONS}',
                   help   ='Maven tasks / options',
                   nargs  ='*',
                   default=list())
    args=p.parse_args()
    def get(a:str): return getattr(args,a)
    if get(A.JDK) is None:

        if get(A.JDK_HOME) is None and 'JAVA_HOME' not in os.environ: raise Exception(f'either of options {repr(A.JDK)} or {repr(A.JDK_HOME)} must be given')
    
    elif get(A.JDK_HOME) is not None: raise Exception(f'both options {repr(A.JDK)} are {repr(A.JDK_HOME)} were given - conflicting')

    # do it
    do_it(wd           =get(A.WORKING_DIRECTORY),
          jdk_home     =envars_java.JDK_HOMES.get()\
                       [get(A.JDK)]                    if get(A.JDK)           is not None else \
                        get(A.JDK_HOME)                if get(A.JDK_HOME)      is not None else os.environ['JAVA_HOME'],
          maven        =envars_java.MAVEN    .get()    if get(A.MAVEN)         is     None else get(A.MAVEN),
          options      =get(A.OPTIONS))
